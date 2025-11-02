from sqlalchemy import Column, Integer, String, Float, ForeignKey, ForeignKeyConstraint, PrimaryKeyConstraint, DateTime, func, Boolean

from expensemgr.database.db import Base

# Models for money schema tables

class Currency(Base):
    __tablename__ = "currency"
    __table_args__ = (
        PrimaryKeyConstraint("currency_key", name="currency_pk"),
        {"schema": "money_schema"},
    )

    currency_key = Column(Integer, primary_key=True, index=True)
    currency_code = Column(String(10), unique=True, index=True, nullable=False)
    currency_name = Column(String(100), nullable=False)
    currency_desc = Column(String(255), nullable=False)
    meta_changed_dttm = Column(DateTime, default=func.now())
    meta_changed_by = Column(Integer, nullable=False) # dont want to create a foreign key yet as dont want to manage any specific deletions if the user gets deleted


class Expense(Base):
    __tablename__ = "expense"
    __table_args__ = (
        ForeignKeyConstraint(
            ["primary_user_key"], ["user_schema.user.user_key"], name="expense_fk01"
        ),
        ForeignKeyConstraint(
            ["currency_key"], ["money_schema.currency.currency_key"], name="expense_fk02"
        ),
        ForeignKeyConstraint(
            ["division_by_key"], ["money_schema.division_by.division_by_key"], name="expense_fk03"
        ),
        PrimaryKeyConstraint("expense_key", name="expense_pk"),
        {"schema": "money_schema"},
    )

    expense_key = Column(Integer, primary_key=True, index=True)
    primary_user_key = Column(Integer, ForeignKey("user_schema.user.user_key"), nullable = False)
    currency_key = Column(Integer, ForeignKey("money_schema.currency.currency_key"), nullable = False)
    division_by_key = Column(Integer, ForeignKey("money_schema.division_by.division_by_key"), nullable = False)
    total_amount = Column(Float, nullable=False)
    expense_desc = Column(String(255))
    meta_changed_dttm = Column(DateTime, default=func.now())
    meta_changed_by = Column(Integer)
    expense_status = Column(Boolean, default=False, nullable=False)

class ExpenseVer(Base):
    __tablename__ = "expense_ver"
    __table_args__ = (
        PrimaryKeyConstraint(
            "expense_ver_key", name="expense_ver_pk"
        ),
        ForeignKeyConstraint(
            ["expense_key"], ["money_schema.expense.expense_key"], name="expense_ver_fk01"
        ),
        ForeignKeyConstraint(
            ["primary_user_key"], ["user_schema.user.user_key"], name="expense_ver_fk02"
        ),
        {"schema": "money_schema"},
    )

    expense_ver_key = Column(Integer, primary_key=True)
    expense_key = Column(Integer, ForeignKey("money_schema.expense.expense_key"), nullable = False)
    primary_user_key = Column(Integer, ForeignKey("user_schema.user.user_key"), nullable = False)
    secondary_user_key = Column(Integer, nullable=False)
    expense_share = Column(Float, nullable=False)
    expense_ver_status = Column(Boolean, default=False, nullable=False)


class DivisionBy(Base):
    __tablename__ = "division_by"
    __table_args__ = (
        PrimaryKeyConstraint("division_by_key", name="division_by_pk"),
        {"schema": "money_schema"}
    )

    division_by_key = Column(Integer, primary_key=True)
    division_by_type = Column(String(10), nullable= False)
    division_by_type_desc = Column(String(100), nullable=False)