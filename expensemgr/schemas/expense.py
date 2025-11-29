from typing import Dict, List, Optional

from fastapi import Query
from pydantic import BaseModel, model_validator
from pydantic_core import PydanticCustomError
from sqlalchemy import select

from expensemgr.database.db import get_db_class, DB
from expensemgr.database.models.expense import DivisionBy as div_model, Currency
from expensemgr.utils.constants import DivisionBy as div_enum


class CreateExpense(BaseModel):
    primary_user_key: int
    currency_key: int
    division_by_key: int
    total_amount: float
    expense_desc: str
    user_expense_secondary_share: Optional[dict[int, float]] = None

    @model_validator(mode="after")
    def validate_secondary_shares(self):
        total_secondary_share = self.user_expense_secondary_share.values()


        db_instance: DB = get_db_class()

        currency_key_check = db_instance.fetch_one_record(
            select(
                Currency
            ).where(
                Currency.currency_key == self.currency_key
            )
        )
        if not currency_key_check:
            raise PydanticCustomError(
                "expense-creation-error",
                "Currency key does not exist!"
            )

        division_by_code = db_instance.fetch_one_record(
            select(
                div_model.division_by_code
            ).where(
                div_model.division_by_key == self.division_by_key
            )
        )
        division_by_code = division_by_code.division_by_code if division_by_code else division_by_code
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
    secondary_user_name: str
    expense_share: float

class ExpenseOut(BaseModel):
    expense_key: int
    primary_user_name: str
    expense_desc: str
    currency_code: str
    division_by_code: str
    expense_share: List[ExpenseShare]
    total_amount: float

