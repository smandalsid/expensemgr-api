# from typing import List
# from sqlalchemy import or_, and_, insert, select, func, literal
# from sqlalchemy.engine.cursor import CursorResult
# from sqlalchemy.orm import aliased

# from expensemgr.database.db import db_dependency, metadata
# from expensemgr.schemas.expense import CreateExpense, ExpenseOut, RequestExpense, ExpenseShare
# from expensemgr.database.models.expense import Expense, ExpenseVer, Currency, DivisionBy
# from expensemgr.database.models.users import User
# from expensemgr.routers.users import user_dependency
# from expensemgr.utils.logger import expense_mgr_logger

# db = db_dependency  

# results = db.fetch_records(
#     select(
#         ExpenseVer.primary_user_key
#     ).where(
#         ExpenseVer.secondary_user_key == 1
#     ).distinct()
# )
# print(results)

# u1: User = aliased(User)
# u2: User = aliased(User)
# expense_out_stmt = select(
#     Expense.expense_key.label("expense_key"),
#     func.concat(u1.first_name, literal(" "), u1.last_name).label("primary_user_name"),
#     func.concat(u2.first_name, literal(" "), u2.last_name).label("secondary_user_name"),
#     ExpenseVer.expense_share.label("expense_share"),
#     Currency.currency_code.label("currency_code"),
#     Expense.total_amount.label("total_amount"),
#     DivisionBy.division_by_code.label("division_by_code"),
#     Expense.expense_desc.label("expense_desc")
# ).join(
#     ExpenseVer,
#     Expense.expense_key == ExpenseVer.expense_key
# ).join(
#     u1,
#     and_(
#         Expense.primary_user_key == u1.user_key,
#         ExpenseVer.primary_user_key.in_(
#             [i.primary_user_key for i in results]
#         )
#     )
# ).join(
#     u2,
#     ExpenseVer.secondary_user_key == u2.user_key,
# ).join(
#     Currency,
#     Expense.currency_key == Currency.currency_key
# ).join(
#     DivisionBy,
#     Expense.division_by_key == DivisionBy.division_by_key
# )

# expense_outs = db.fetch_records(
#     expense_out_stmt
# )

# print(expense_outs)

# import currencyapicom
# client = currencyapicom.Client('')
# result = client.latest('USD',currencies=['INR', 'AUD'])
# print(result)




from abc import ABC, abstractmethod, abstractclassmethod

class A(ABC):
    _data = 'A'

    @classmethod
    @abstractmethod    
    def change(cls, data):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def show(cls):
        raise NotImplementedError

class B(A):

    @classmethod
    def change(cls, data):
        return super().change(data)
    
    @classmethod
    def show(cls):
        print(cls._data)
    