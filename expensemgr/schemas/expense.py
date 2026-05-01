from typing import List

from pydantic import BaseModel, model_validator
from pydantic_core import PydanticCustomError
from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import array

from expensemgr.database.db import get_db_class, DB
from expensemgr.database.models.expense import DivisionBy as div_model, Currency, Expense, ExpenseVer
from expensemgr.utils.constants import DivisionBy as div_enum, VersionActiveInd


class UserExpenseShare(BaseModel):
    user_key: int
    user_share: float

class EditUserExpenseShare(UserExpenseShare):
    expense_ver_key: int

class CreateExpense(BaseModel):
    primary_user_key: int
    currency_key: int
    division_by_key: int
    total_amount: float
    expense_desc: str
    user_expense_secondary_share: List[UserExpenseShare]

    @model_validator(mode="after")
    def validation_user_presence_in_expense(self):
        secondary_share_user_keys = {share.user_key for share in self.user_expense_secondary_share}
        if self.primary_user_key not in secondary_share_user_keys:
            raise PydanticCustomError(
                "expense-creation-error", "Primary user is not in the expense share!"
            )
        return self

    @model_validator(mode="after")
    def validate_secondary_shares(self):
        total_secondary_share = [
            s.user_share for s in self.user_expense_secondary_share
        ]

        db_instance: DB = get_db_class()

        currency_key_check = db_instance.fetch_one_record(
            query=select(Currency).where(Currency.currency_key == self.currency_key)
        )
        if not currency_key_check:
            raise PydanticCustomError(
                "expense-creation-error", "Currency key does not exist!"
            )

        division_by_code = db_instance.fetch_one_record(
            query=select(div_model.division_by_code).where(
                div_model.division_by_key == self.division_by_key
            )
        )
        division_by_code = (
            division_by_code.division_by_code if division_by_code else division_by_code
        )
        if division_by_code == div_enum.AMOUNT.value:
            total_sum = sum(total_secondary_share)
            if total_sum != self.total_amount:
                raise PydanticCustomError(
                    "expense-creation-error",
                    "The expense shares don't add up to the total amount!",
                )
            return self
        elif division_by_code == div_enum.PERCENTAGE.value:
            total_percentage = sum(total_secondary_share)
            if total_percentage != 100:
                raise PydanticCustomError(
                    "expense-creation-error",
                    "The expense shares don't add up to 100%!",
                )
            return self
        else:
            raise PydanticCustomError(
                "expense-creation-error",
                "Invalid division type!",
            )


class ExpenseShare(BaseModel):
    secondary_user_key: int
    secondary_user_name: str
    expense_ver_key: int
    expense_share: float
    expense_ver_status: bool
    version_active_ind: bool

class ExpenseOut(BaseModel):
    expense_key: int
    primary_user_key: int
    primary_user_name: str
    expense_desc: str
    currency_code: str
    division_by_code: str
    expense_share: List[ExpenseShare]
    total_amount: float

class EditExpense(CreateExpense):
    expense_key: int
    user_expense_secondary_share: List[EditUserExpenseShare]

    @model_validator(mode="after")
    def validate_expense_key(self):
        db_instance: DB = get_db_class()
        expense_in_db = db_instance.execute_query(
            query=select(
                select(1)
                .where(
                    Expense.expense_key == self.expense_key
                ).exists(),
            )
        )
        if not expense_in_db.scalar():
            raise PydanticCustomError(
                "edit-expense-exception", "Expense key does not exist!"
            )
        return self
    
    @model_validator(mode="after")
    def validate_expense_ver_keys(self):
        db_instance: DB = get_db_class()
        secondary_share_expense_ver_keys = {share.expense_ver_key for share in self.user_expense_secondary_share}
        missing_keys = db_instance.execute_query(
            query=select(
                func.unnest(array(secondary_share_expense_ver_keys)).label("missing_keys")
            )
            .except_(
                select(ExpenseVer.expense_ver_key)
            )
        )
        if missing_keys.all():
            raise PydanticCustomError(
                "edit-expense-exception", "Expense shares do not exist!"
            )

        return self
    
    @model_validator(mode="after")
    def validate_expense_vers_align_with_expense(self):
        db_instance: DB = get_db_class()
        expense_key = self.expense_key
        secondary_share_expense_ver_keys = {share.expense_ver_key for share in self.user_expense_secondary_share}

        expense_ver_keys= db_instance.execute_query(
            query=select(
                ExpenseVer.expense_ver_key.label("expense_ver_key"),
            )
            .where(
                ExpenseVer.expense_key == expense_key,
                ExpenseVer.version_active_ind == VersionActiveInd.ACTIVE.value
            )
        )
        if set(expense_ver_keys.scalars().all()) != secondary_share_expense_ver_keys:
            raise PydanticCustomError(
                "edit-expense-exception", "Expense and Expense shares do not match!"
            )

        return self
