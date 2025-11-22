from typing import List
from sqlalchemy import or_, and_

from expensemgr.database.db import db_dependency
from expensemgr.schemas.expense import CreateExpense, ExpenseOut, RequestExpense
from expensemgr.database.models.expense import Expense, ExpenseVer, Currency
from expensemgr.database.models.expense import Expense, ExpenseVer, Currency
from expensemgr.routers.users import user_dependency

from expensemgr.database.db import engine

class ExpenseCreationException(Exception):
    pass

class ExpenseService:
    
    def __init__(self, db: db_dependency, user: user_dependency):
        self.db = db
        self.user = user

    def create_expense(self, expense: CreateExpense) -> ExpenseOut:
        secondary_users, secondary_user_share = expense.user_expense_secondary_share.keys(), expense.user_expense_secondary_share.values()

        try:
            # new_expense = Expense(
            #     primary_user_key = expense.primary_user_key,
            #     currency_key = expense.currency_key,
            #     division_by_key = expense.division_by_key,
            #     total_amount = expense.total_amount,
            #     expense_desc = expense.expense_desc,
            #     meta_changed_by = self.user.get("user_key"),
            # )
            new_expense_stmt = Expense.insert().values(
                primary_user_key = expense.primary_user_key,
                currency_key = expense.currency_key,
                division_by_key = expense.division_by_key,
                total_amount = expense.total_amount,
                expense_desc = expense.expense_desc,
                meta_changed_by = self.user.get("user_key"),
            )
            engine.execute(new_expense_stmt)

            # new_expense_ver = ExpenseVer(

            # )

        except ExpenseCreationException as e:
            raise e

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
    