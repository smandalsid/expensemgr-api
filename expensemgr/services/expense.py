from typing import List
from sqlalchemy import or_, and_, insert, select, func, literal
from sqlalchemy.engine.cursor import CursorResult
from sqlalchemy.orm import aliased

from expensemgr.database.db import db_dependency, metadata
from expensemgr.schemas.expense import CreateExpense, ExpenseOut, RequestExpense
from expensemgr.database.models.expense import Expense, ExpenseVer, Currency, DivisionBy
from expensemgr.database.models.users import User
from expensemgr.routers.users import user_dependency
from expensemgr.utils.logger import expense_mgr_logger

class ExpenseCreationException(Exception):
    pass

class ExpenseService:
    
    def __init__(self, db: db_dependency, user: user_dependency):
        self.db = db
        self.user = user

    # @expense_mgr_logger.wrapper_logger(log_args=True)
    # ddef create_

    @expense_mgr_logger.wrapper_logger(log_args=True)
    def create_expense_ver(self, expense: CreateExpense, new_expense: CursorResult):
        for secondary_user, secondary_user_share in expense.user_expense_secondary_share.items():
            self.db.execute_query(
                insert(ExpenseVer)\
                .values(
                    expense_key = new_expense.inserted_primary_key[0],
                    primary_user_key = self.user.get("user_key"),
                    secondary_user_key = secondary_user,
                    expense_share = secondary_user_share,
                )
            )

    @expense_mgr_logger.wrapper_logger(log_args=True)
    def create_expense(self, expense: CreateExpense) -> ExpenseOut:
        try:
            new_expense = self.db.execute_query(
                insert(Expense)\
                .values(
                    primary_user_key = expense.primary_user_key,
                    currency_key = expense.currency_key,
                    division_by_key = expense.division_by_key,
                    total_amount = expense.total_amount,
                    expense_desc = expense.expense_desc,
                    meta_changed_by = self.user.get("user_key"),
                )
            )

            self.create_expense_ver(
                expense,
                new_expense,
            )

            primary_user_name = self.db.fetch_one_record(
                select(
                    User.username
                ).where(
                    User.user_key == expense.primary_user_key
                )
            )[0]
            secondary_user_names = self.db.fetch_records(
                select(
                    User.username
                ).where(
                    User.user_key.in_(
                        expense.user_expense_secondary_share.keys()
                    )
                )
            )

            u1: User = aliased(User)
            u2: User = aliased(User)
            expense_out_stmt = select(
                Expense.expense_key.label("expense_key"),
                func.concat(u1.first_name, literal(" "), u1.last_name).label("primary_user_name"),
                func.concat(u2.first_name, literal(" "), u2.last_name).label("secondary_user_name"),
                ExpenseVer.expense_share.label("expense_share"),
                Currency.currency_code.label("currency_code"),
                Expense.total_amount.label("total_amount"),
                DivisionBy.division_by_code.label("division_by_code"),
                Expense.expense_desc.label("expense_desc")
            ).join(
                ExpenseVer,
                Expense.expense_key == ExpenseVer.expense_key
            ).join(
                u1,
                Expense.primary_user_key == u1.user_key
            ).join(
                u2,
                ExpenseVer.secondary_user_key == u2.user_key
            ).join(
                Currency,
                Expense.currency_key == Currency.currency_key
            ).join(
                DivisionBy,
                Expense.division_by_key == DivisionBy.division_by_key
            ).where(
                Expense.expense_key == new_expense.inserted_primary_key[0]
            )
            expense_outs = self.db.fetch_records(
                expense_out_stmt
            )
            
            return ExpenseOut(
                primary_user_name=primary_user_name,
                secondary_user_names=[x[0] for x in secondary_user_names],
                total_amount=expense.total_amount,
                expense_desc=expense.expense_desc
            )

        except ExpenseCreationException as e:
            expense_mgr_logger.get_logger().exception("Error creating expense!")
            raise e

    @expense_mgr_logger.wrapper_logger(log_args=True)
    def get_all_expenses(self) -> List[ExpenseOut]:
        return \
            self.db.query(
                Expense.amount,
                Expense.description,
                Expense.expense_id,
                Currency.abbr.label("currency_abbr")). \
            join(Currency, Expense.currency_id == Currency.currency_id). \
            filter(Expense.user_id == self.user.get('id')). \
            all()
    
    @expense_mgr_logger.wrapper_logger(log_args=True)
    def get_expense(self, request: RequestExpense) -> List[ExpenseOut]:

        filters = [
            Expense.user_id == self.user.get('id'),
            or_(
                *[Expense.currency_id == x for x in request.currency_id],
            ) if request.currency_id else None,
            or_(
                *[Expense.expense_id == x for x in request.expense_id]
            ) if request.expense_id else None,
        ]

        result = self.db.query(
            Expense.amount.label("amount"),
            Expense.description.label("description"),
            Expense.expense_id.label("expense_id"),
            Currency.abbr.label("currency_abbr")
        )\
        .join(Currency, Expense.currency_id == Currency.currency_id) \
        .filter(*[x for x in filters if x is not None]).all()

        return result
    