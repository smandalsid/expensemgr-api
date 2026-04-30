from typing import List, Optional
from sqlalchemy import or_, and_, insert, select, func, literal
from sqlalchemy.dialects.postgresql import array
from sqlalchemy.engine.cursor import CursorResult
from sqlalchemy.orm import aliased

from expensemgr.database.db import db_dependency
from expensemgr.schemas.expense import CreateExpense, ExpenseOut, ExpenseShare
from expensemgr.database.models.expense import Expense, ExpenseVer, Currency, DivisionBy
from expensemgr.database.models.users import User
from expensemgr.routers.users import user_dependency
from expensemgr.utils.logger import expense_mgr_logger
from expensemgr.utils.constants import VersionActiveInd, DeleteInd, ExpenseVerStatus


class ExpenseCreationException(Exception):
    pass


class ExpenseNotFoundException(Exception):
    pass


class ExpenseService:
    def __init__(self, db: db_dependency, user: user_dependency):
        self.db = db
        self.user = user

    def _build_expense_query(self, expense_ver_condition):
        u1: User = aliased(User)
        u2: User = aliased(User)
        return (
            select(
                Expense.expense_key.label("expense_key"),
                u1.user_key.label("primary_user_key"),
                func.concat(u1.first_name, literal(" "), u1.last_name).label(
                    "primary_user_name"
                ),
                u2.user_key.label("secondary_user_key"),
                func.concat(u2.first_name, literal(" "), u2.last_name).label(
                    "secondary_user_name"
                ),
                ExpenseVer.expense_ver_key.label("expense_ver_key"),
                ExpenseVer.expense_share.label("expense_share"),
                Expense.expense_desc.label("expense_desc"),
                Expense.total_amount.label("total_amount"),
                Currency.currency_code.label("currency_code"),
                DivisionBy.division_by_code.label("division_by_code"),
                ExpenseVer.expense_ver_status.label("expense_ver_status"),
                Expense.meta_changed_dttm.label("meta_changed_dttm"),
            )
            .join(
                ExpenseVer,
                and_(
                    Expense.expense_key == ExpenseVer.expense_key,
                    expense_ver_condition,
                    Expense.delete_ind == DeleteInd.NO.value,
                ),
            )
            .join(
                u1,
                and_(
                    Expense.primary_user_key == u1.user_key,
                ),
            )
            .join(
                u2,
                and_(
                    ExpenseVer.secondary_user_key == u2.user_key,
                ),
            )
            .join(Currency, Expense.currency_key == Currency.currency_key)
            .join(DivisionBy, Expense.division_by_key == DivisionBy.division_by_key)
            .order_by(Expense.meta_changed_dttm.desc())
        )

    def _rows_to_expense_out(self, rows) -> ExpenseOut:
        first = rows[0]
        return ExpenseOut(
            expense_key=first.expense_key,
            primary_user_key=first.primary_user_key,
            primary_user_name=first.primary_user_name,
            expense_desc=first.expense_desc,
            currency_code=first.currency_code,
            division_by_code=first.division_by_code,
            total_amount=first.total_amount,
            expense_share=[
                ExpenseShare(
                    secondary_user_key=row.secondary_user_key,
                    secondary_user_name=row.secondary_user_name,
                    expense_ver_key=row.expense_ver_key,
                    expense_share=row.expense_share,
                    expense_ver_status=row.expense_ver_status
                )
                for row in rows
            ],
        )

    @expense_mgr_logger.wrapper_logger(log_args=True)
    def create_expense_ver(self, expense: CreateExpense, new_expense: CursorResult):
        for entry in expense.user_expense_secondary_share:
            self_expense = False
            if expense.primary_user_key == entry.user_key:
                self_expense = True
            self.db.execute_query(
                insert(ExpenseVer).values(
                    expense_key=new_expense.inserted_primary_key[0],
                    primary_user_key=expense.primary_user_key,
                    secondary_user_key=entry.user_key,
                    expense_share=entry.user_share,
                    expense_ver_status=self_expense
                )
            )

    @expense_mgr_logger.wrapper_logger(log_args=True)
    def create_expense(self, expense: CreateExpense) -> ExpenseOut:
        try:
            user_key = self.user.get("user_key")
            secondary_share_user_keys = {share.user_key for share in expense.user_expense_secondary_share}
            if user_key not in secondary_share_user_keys:
                raise ExpenseCreationException("Cannot create expense where you are not included!")
            
            missing_keys = self.db.execute_query(
                select(
                    func.unnest(array(secondary_share_user_keys)).label("missing_keys")
                )
                .except_(
                    select(User.user_key)
                )
            )
            if missing_keys.all():
                raise ExpenseCreationException("Not all user keys are valid!")

            self_expense = False
            if len(expense.user_expense_secondary_share) == 1 and user_key == expense.user_expense_secondary_share[0].user_key:
                self_expense = True

            new_expense = self.db.execute_query(
                insert(Expense).values(
                    primary_user_key=expense.primary_user_key,
                    currency_key=expense.currency_key,
                    division_by_key=expense.division_by_key,
                    total_amount=expense.total_amount,
                    expense_desc=expense.expense_desc,
                    meta_changed_by=self.user.get("user_key"),
                    expense_status=self_expense
                )
            )

            self.create_expense_ver(
                expense=expense,
                new_expense=new_expense,
            )

            expense_outs = self.db.fetch_records(
                self._build_expense_query(
                    Expense.expense_key == new_expense.inserted_primary_key[0]
                )
            )
            if expense_outs:
                return self._rows_to_expense_out(expense_outs)
            else:
                expense_mgr_logger.get_logger().exception("Error creating expense!")
                raise ExpenseCreationException

        except ExpenseCreationException as e:
            expense_mgr_logger.get_logger().exception(f"Error creating expense! {e}")
            raise e

    @expense_mgr_logger.wrapper_logger(log_args=True)
    def get_all_expenses(self) -> Optional[List[ExpenseOut]]:
        expense_keys_of_user = self.db.fetch_records(
            select(ExpenseVer.expense_key)
            .where(
                and_(
                    ExpenseVer.secondary_user_key == self.user.get("user_key"),
                    ExpenseVer.version_active_ind == VersionActiveInd.ACTIVE.value
                )
            )
            .distinct()
        )

        expense_outs = self.db.fetch_records(
            self._build_expense_query(
                Expense.expense_key.in_(i[0] for i in expense_keys_of_user)
            )
        )
        if not expense_outs:
            expense_mgr_logger.logger.exception("No expenses found for the user!")
            return

        grouped = {}
        for row in expense_outs:
            grouped.setdefault(row.expense_key, []).append(row)
        return [self._rows_to_expense_out(rows) for rows in grouped.values()]

    @expense_mgr_logger.wrapper_logger(log_args=True)
    def get_expense(self, expense_key: int) -> ExpenseOut:
        expense_keys_of_user = self.db.fetch_records(
            select(ExpenseVer.expense_key)
            .where(ExpenseVer.secondary_user_key == self.user.get("user_key"))
            .distinct()
        )
        if not expense_keys_of_user:
            raise ExpenseNotFoundException
        expense_keys_of_user = [i[0] for i in expense_keys_of_user]
        if expense_key not in expense_keys_of_user:
            raise ExpenseNotFoundException

        expense_outs = self.db.fetch_records(
            self._build_expense_query(Expense.expense_key == expense_key)
        )
        if expense_outs:
            return self._rows_to_expense_out(expense_outs)
        else:
            expense_mgr_logger.logger.exception("Error creating expense!")
            raise ExpenseNotFoundException
