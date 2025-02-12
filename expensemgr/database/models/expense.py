from sqlalchemy import Column, Integer, String, Float, ForeignKey, ForeignKeyConstraint, PrimaryKeyConstraint

from expensemgr.database.db import Base

class Currency(Base):
    __tablename__ = "currency"
    __table_args__ = (
        ForeignKeyConstraint(
            ["created_by"], ["user_schema.users.user_id"], name="currency_fk01"
        ),
        PrimaryKeyConstraint("currency_id", name="currency_pk"),
        {"schema": "money_schema"},
    )

    currency_id = Column(Integer, primary_key=True, index=True)
    created_by = Column(Integer, ForeignKey("user_schema.users.user_id"))
    abbr = Column(String(10), unique=True, index=True, nullable=False)
    desc = Column(String(255), nullable=False)


class Expense(Base):
    __tablename__ = "expenses"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"], ["user_schema.users.user_id"], name="expense_fk01"
        ),
        ForeignKeyConstraint(
            ["currency_id"], ["money_schema.currency.currency_id"], name="expense_fk02"
        ),
        PrimaryKeyConstraint("expense_id", name="expense_pk"),
        {"schema": "money_schema"},
    )

    expense_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_schema.users.user_id"))
    currency_id = Column(Integer, ForeignKey("money_schema.currency.currency_id"))
    amount = Column(Float, nullable=False)
    description = Column(String(255))
