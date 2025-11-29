from typing import List, Optional
from sqlalchemy import or_, and_, insert, select, func, literal
from sqlalchemy.sql.expression import ColumnOperators
from sqlalchemy.engine.cursor import CursorResult
from sqlalchemy.orm import aliased

from expensemgr.database.db import db_dependency, metadata
from expensemgr.schemas.expense import CreateExpense, ExpenseOut, ExpenseShare
from expensemgr.database.models.expense import Expense, ExpenseVer, Currency, DivisionBy
from expensemgr.database.models.users import User
from expensemgr.routers.users import user_dependency
from expensemgr.utils.logger import expense_mgr_logger

class ExpenseCreationException(Exception):
    pass

class ExpenseNotFoundException(Exception):
    pass

class ExpenseService:
    
    def __init__(self, db: db_dependency, user: user_dependency):
        self.db = db
        self.user = user

    @expense_mgr_logger.wrapper_logger(log_args=True)
    def create_expense_ver(self, expense: CreateExpense, new_expense: CursorResult):
        for secondary_user, secondary_user_share in expense.user_expense_secondary_share.items():
            self.db.execute_query(
                insert(ExpenseVer)\
                .values(
                    expense_key = new_expense.inserted_primary_key[0],
                    primary_user_key = expense.primary_user_key,
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
                and_(
                    Expense.expense_key == ExpenseVer.expense_key,
                    Expense.expense_key == new_expense.inserted_primary_key[0]
                )
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
            )

            expense_outs = self.db.fetch_records(
                expense_out_stmt
            )
            if expense_outs:
                return_expense = ExpenseOut(
                    expense_key=expense_outs[0].expense_key,
                    primary_user_name=expense_outs[0].primary_user_name,
                    expense_desc=expense_outs[0].expense_desc,
                    currency_code=expense_outs[0].currency_code,
                    division_by_code=expense_outs[0].division_by_code,
                    expense_share=[],
                    total_amount=expense_outs[0].total_amount,
                )
                for expense_out in expense_outs:
                    return_expense.expense_share.append(
                        ExpenseShare(
                            secondary_user_name=expense_out.secondary_user_name,
                            expense_share=expense_out.expense_share
                        )
                    )
            else:
                expense_mgr_logger.get_logger().exception("Error creating expense!")
                raise ExpenseCreationException
            
            return return_expense

        except ExpenseCreationException as e:
            expense_mgr_logger.get_logger().exception("Error creating expense!")
            raise e

    @expense_mgr_logger.wrapper_logger(log_args=True)
    def get_all_expenses(self) -> Optional[List[ExpenseOut]]:

        expense_keys_of_user = self.db.fetch_records(
            select(
                ExpenseVer.expense_key
            ).where(
                ExpenseVer.secondary_user_key == self.user.get("user_key")
            ).distinct()
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
            and_(
                Expense.expense_key == ExpenseVer.expense_key,
                Expense.expense_key.in_(
                    i[0] for i in expense_keys_of_user
                )
            )
        ).join(
            u1,
            Expense.primary_user_key == u1.user_key,
        ).join(
            u2,
            ExpenseVer.secondary_user_key == u2.user_key,
        ).join(
            Currency,
            Expense.currency_key == Currency.currency_key
        ).join(
            DivisionBy,
            Expense.division_by_key == DivisionBy.division_by_key
        )

        expense_outs = self.db.fetch_records(
            expense_out_stmt
        )
        if not expense_outs:
            expense_mgr_logger.logger.exception("No expenses found for the user!")
            return
        
        return_expenses = {}
        for expense_out in expense_outs:
            if expense_out.expense_key not in return_expenses:
                return_expenses[expense_out.expense_key] = ExpenseOut(
                    expense_key=expense_out.expense_key,
                    primary_user_name=expense_out.primary_user_name,
                    expense_desc=expense_out.expense_desc,
                    currency_code=expense_out.currency_code,
                    division_by_code=expense_out.division_by_code,
                    expense_share=[
                        ExpenseShare(
                            secondary_user_name=expense_out.secondary_user_name,
                            expense_share=expense_out.expense_share
                        )
                    ],
                    total_amount=expense_out.total_amount,
                )
            else:
                return_expenses[expense_out.expense_key].expense_share.append(
                    ExpenseShare(
                        secondary_user_name=expense_out.secondary_user_name,
                        expense_share=expense_out.expense_share
                    )
                )
        return return_expenses.values()
    
    @expense_mgr_logger.wrapper_logger(log_args=True)
    def get_expense(self, expense_key: int) -> ExpenseOut:

        expense_keys_of_user = self.db.fetch_records(
            select(
                ExpenseVer.expense_key
            ).where(
                ExpenseVer.secondary_user_key == self.user.get("user_key")
            ).distinct()
        )
        if not expense_keys_of_user:
            raise ExpenseNotFoundException
        expense_keys_of_user = [i[0] for i in expense_keys_of_user]
        if expense_key not in expense_keys_of_user:
            raise ExpenseNotFoundException

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
            and_(
                Expense.expense_key == ExpenseVer.expense_key,
                Expense.expense_key == expense_key
            )
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
        )

        expense_outs = self.db.fetch_records(
            expense_out_stmt
        )
        if expense_outs:
            return_expense = ExpenseOut(
                expense_key=expense_outs[0].expense_key,
                primary_user_name=expense_outs[0].primary_user_name,
                expense_desc=expense_outs[0].expense_desc,
                currency_code=expense_outs[0].currency_code,
                division_by_code=expense_outs[0].division_by_code,
                expense_share=[],
                total_amount=expense_outs[0].total_amount,
            )
            for expense_out in expense_outs:
                return_expense.expense_share.append(
                    ExpenseShare(
                        secondary_user_name=expense_out.secondary_user_name,
                        expense_share=expense_out.expense_share
                    )
                )
        else:
            expense_mgr_logger.logger.exception("Error creating expense!")
            raise ExpenseNotFoundException
        
        return return_expense
