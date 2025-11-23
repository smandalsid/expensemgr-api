from typing import Dict, List, Optional

from fastapi import Query
from pydantic import BaseModel, model_validator
from pydantic_core import PydanticCustomError
from sqlalchemy import select

from expensemgr.database.db import engine
from expensemgr.database.models.expense import DivisionBy as div_model
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

        with engine.connect() as conn:
            division_by_code = conn.execute(
                select(
                    div_model.division_by_code
                ).where(
                    div_model.division_by_key == self.division_by_key
                )
            ).fetchone()[0]
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


class ExpenseOut(BaseModel):
    primary_user_name: str
    secondary_user_names: Dict[str, float]
    total_amount: float
    expense_desc: str

class RequestExpense(BaseModel):
    expense_key: Optional[List[int]] = Query(None)
    currency_key: Optional[List[int]] = Query(None)
