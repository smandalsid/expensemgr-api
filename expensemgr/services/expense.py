from datetime import datetime, timezone
from typing import List, Optional, Union
from sqlalchemy import and_, insert, select, func, literal, update, Connection, true, case, exists
from sqlalchemy.dialects.postgresql import array
from sqlalchemy.engine.cursor import CursorResult
from sqlalchemy.orm import aliased

from expensemgr.database.db import db_dependency
from expensemgr.schemas.expense import CreateExpense, ExpenseOut, ExpenseShare, EditExpense
from expensemgr.database.models.expense import Expense, ExpenseVer, Currency, DivisionBy
from expensemgr.database.models.users import User
from expensemgr.routers.users import user_dependency
from expensemgr.utils.logger import expense_mgr_logger
from expensemgr.utils.constants import VersionActiveInd, DeleteInd, ExpenseVerStatus


class ExpenseCreationException(Exception):
    pass


class ExpenseNotFoundException(Exception):
    pass

class ExpenseEditException(Exception):
    pass

class ExpenseDeleteException(Exception):
    pass


class ExpenseService:
    def __init__(self, db: db_dependency, user: user_dependency):
        self.db = db
        self.user = user

    def _build_expense_query(self, expense_ver_condition, get_active: Optional[bool] = False):
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
                ExpenseVer.version_active_ind.label("version_active_ind")
            )
            .select_from(Expense)
            .join(
                ExpenseVer,
                and_(
                    Expense.expense_key == ExpenseVer.expense_key,
                    and_(Expense.delete_ind == DeleteInd.NO.value,
                    ExpenseVer.version_active_ind == VersionActiveInd.ACTIVE.value) if get_active else true()
                ),
            )
            .join(u1, Expense.primary_user_key == u1.user_key)
            .join(u2, ExpenseVer.secondary_user_key == u2.user_key)
            .join(Currency, Expense.currency_key == Currency.currency_key)
            .join(DivisionBy, Expense.division_by_key == DivisionBy.division_by_key)
            .where(expense_ver_condition)
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
                    expense_ver_status=row.expense_ver_status,
                    version_active_ind=row.version_active_ind
                )
                for row in rows
            ],
        )

    @expense_mgr_logger.wrapper_logger(log_args=True)
    def create_expense_ver(self, expense: Union[CreateExpense, EditExpense], expense_key: int, now: datetime, conn: Connection):
        rows = [
            {
                "expense_key": expense_key,
                "primary_user_key": expense.primary_user_key,
                "secondary_user_key": entry.user_key,
                "expense_share": entry.user_share,
                "expense_ver_status": expense.primary_user_key == entry.user_key,
                "version_effective_dttm": now,
                "meta_changed_dttm": now,
                "meta_changed_by": self.user.get("user_key")
            }
            for entry in expense.user_expense_secondary_share
        ]
        conn.execute(statement=insert(ExpenseVer).values(rows))

    @expense_mgr_logger.wrapper_logger(log_args=True)
    def create_expense(self, expense: CreateExpense) -> ExpenseOut:
        try:
            engine = self.db.get_engine()
            with engine.begin() as conn:
                user_key = self.user.get("user_key")
                secondary_share_user_keys = {share.user_key for share in expense.user_expense_secondary_share}
                if user_key not in secondary_share_user_keys:
                    raise ExpenseCreationException("Cannot create expense where you are not included!")
                
                missing_keys = conn.execute(
                    statement=select(
                        func.unnest(array(secondary_share_user_keys)).label("missing_keys")
                    )
                    .except_(
                        select(User.user_key)
                    )
                ).all()
                if missing_keys:
                    raise ExpenseCreationException("Not all user keys are valid!")

                self_expense = False
                if len(expense.user_expense_secondary_share) == 1 and user_key == expense.user_expense_secondary_share[0].user_key:
                    self_expense = True

                now = datetime.now(timezone.utc)
                new_expense = conn.execute(
                    statement=insert(Expense).values(
                        primary_user_key=expense.primary_user_key,
                        currency_key=expense.currency_key,
                        division_by_key=expense.division_by_key,
                        total_amount=expense.total_amount,
                        expense_desc=expense.expense_desc,
                        meta_changed_by=self.user.get("user_key"),
                        expense_status=self_expense,
                        meta_changed_dttm=now,
                    )
                )
                self.create_expense_ver(
                    expense=expense,
                    expense_key=new_expense.inserted_primary_key[0],
                    now=now,
                    conn=conn
                )
                statement=self._build_expense_query(
                        Expense.expense_key == new_expense.inserted_primary_key[0]
                    )
                expense_outs = conn.execute(
                    statement=statement
                ).fetchall()
                if expense_outs:
                    return self._rows_to_expense_out(expense_outs)
                else:
                    expense_mgr_logger.get_logger().exception("Error creating expense!")
                    raise ExpenseCreationException('Error creating expense!')

        except ExpenseCreationException as e:
            expense_mgr_logger.get_logger().exception(f"Error creating expense! {e}")
            raise e

    @expense_mgr_logger.wrapper_logger(log_args=True)
    def get_all_expenses(self) -> Optional[List[ExpenseOut]]:
        expense_keys_cte = (
            select(ExpenseVer.expense_key)
            .where(
                and_(
                    ExpenseVer.secondary_user_key == self.user.get("user_key"),
                )
            )
            .distinct()
            .cte("expense_keys")
        )

        expense_outs = self.db.fetch_records(
            query=self._build_expense_query(
                Expense.expense_key.in_(select(expense_keys_cte.c.expense_key))
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
    def get_active_expenses(self) -> Optional[List[ExpenseOut]]:
        expense_keys_cte = (
            select(ExpenseVer.expense_key)
            .where(
                ExpenseVer.secondary_user_key == self.user.get("user_key"),
                ExpenseVer.version_active_ind == VersionActiveInd.ACTIVE.value
            )
            .distinct()
            .cte("expense_keys")
        )

        expense_outs = self.db.fetch_records(
            query=self._build_expense_query(
                expense_ver_condition=Expense.expense_key.in_(select(expense_keys_cte.c.expense_key)),
                get_active=True
            )
        )
        if not expense_outs:
            return

        grouped = {}
        for row in expense_outs:
            grouped.setdefault(row.expense_key, []).append(row)
        return [self._rows_to_expense_out(rows) for rows in grouped.values()]

    @expense_mgr_logger.wrapper_logger(log_args=True)
    def get_expense(self, expense_key: int) -> ExpenseOut:
        expense_keys_cte = (
            select(ExpenseVer.expense_key)
            .where(
                ExpenseVer.secondary_user_key == self.user.get("user_key"),
                ExpenseVer.expense_key == expense_key
            )
            .distinct()
            .cte("expense_keys")
        )

        expense_outs = self.db.fetch_records(
            query=self._build_expense_query(
                expense_ver_condition=Expense.expense_key.in_(select(expense_keys_cte.c.expense_key))
            )
        )
        if expense_outs:
            return self._rows_to_expense_out(expense_outs)
        else:
            expense_mgr_logger.logger.exception("Error creating expense!")
            raise ExpenseNotFoundException("Error creating expense!")

    @expense_mgr_logger.wrapper_logger(log_args=True)
    def edit_expense(self, expense: EditExpense) -> ExpenseOut:
        user_key = self.user.get("user_key")        
        now = datetime.now(timezone.utc)
        engine = self.db.get_engine()
        with engine.begin() as conn:
            query = select(
                select(1)
                .where(
                    ExpenseVer.secondary_user_key == user_key,
                    ExpenseVer.expense_key == expense.expense_key
                ).exists()
            )
            if not conn.execute(statement=query).scalar():
                raise ExpenseEditException("Cant edit an exception you are not part of!")
            query = update(
                Expense
            )\
            .where(
                Expense.expense_key == expense.expense_key
            )\
            .values(
                primary_user_key = expense.primary_user_key,
                currency_key = expense.currency_key,
                division_by_key = expense.division_by_key,
                total_amount = expense.total_amount,
                expense_desc = expense.expense_desc,
                meta_changed_dttm = now,
                meta_changed_by = user_key,
            )
            conn.execute(statement=query)

            conn.execute(
                update(ExpenseVer)
                .where(
                    ExpenseVer.expense_key == expense.expense_key,
                    ExpenseVer.version_active_ind == VersionActiveInd.ACTIVE.value
                )
                .values(
                    version_termination_dttm=now,
                    version_active_ind=VersionActiveInd.INACTIVE.value,
                    meta_changed_dttm=now,
                    meta_changed_by=user_key,
                )
            )
            self.create_expense_ver(
                expense=expense,
                expense_key=expense.expense_key,
                now=now,
                conn=conn
            )
            
            statement=self._build_expense_query(
                expense_ver_condition= Expense.expense_key == expense.expense_key,
                get_active=True
            )
            expense_outs = conn.execute(
                statement=statement
            ).fetchall()
            if expense_outs:
                return self._rows_to_expense_out(expense_outs)
            else:
                expense_mgr_logger.get_logger().exception("Error editing expense!")
                raise ExpenseCreationException('Error editing expense!')

    @expense_mgr_logger.wrapper_logger()
    def delete_expense(self, expense_key):
        engine = self.db.get_engine()
        user_key = self.user.get("user_key")
        with engine.begin() as conn:
            expense_present_check = conn.execute(
                statement=select(
                    case(
                        (~exists(select(1).where(Expense.expense_key == expense_key)), 'absent'),
                        (exists(select(1).where(Expense.expense_key == expense_key, Expense.delete_ind == DeleteInd.YES.value)), 'deleted'),
                        else_='present'
                    )
                )
            ).scalar()
            if expense_present_check == 'deleted':
                raise ExpenseDeleteException("Expense already deleted!")
            elif expense_present_check == "absent":
                raise ExpenseDeleteException("Expense not present!")
            
            is_eligible_to_delete = conn.execute(
                statement=select(
                    select(1)
                    .where(
                        ExpenseVer.expense_key == expense_key,
                        ExpenseVer.secondary_user_key == user_key,
                        ExpenseVer.version_active_ind == VersionActiveInd.ACTIVE.value
                    )
                    .exists()
                )
            ).scalar()
            if not is_eligible_to_delete:
                raise ExpenseDeleteException('Not your expense to delete!')

            now = datetime.now(timezone.utc)
            conn.execute(
                statement=update(
                    ExpenseVer
                )
                .where(
                    ExpenseVer.expense_ver_key.in_(
                        select(
                            ExpenseVer.expense_ver_key
                        )
                        .where(
                            ExpenseVer.expense_key == expense_key,
                            ExpenseVer.version_active_ind == VersionActiveInd.ACTIVE.value
                        )
                    )
                )
                .values(
                    version_termination_dttm=now,
                    version_active_ind=VersionActiveInd.INACTIVE.value,
                    meta_changed_dttm=now,
                    meta_changed_by=user_key,
                )
            )

            conn.execute(
                statement=update(
                    Expense
                )
                .where(
                    Expense.expense_key == expense_key
                )
                .values(
                    meta_changed_dttm = now,
                    meta_changed_by = user_key,
                    delete_ind = DeleteInd.YES.value,
                )
            )
        return {"detail": "Expense deleted!"}