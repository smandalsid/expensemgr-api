from fastapi import Query
from pydantic import BaseModel, model_validator
from typing import Optional, List, Dict
from pydantic_core import PydanticCustomError

class CreateExpense(BaseModel):
    primary_user_key: int
    currency_key: int
    division_by_key: int
    total_amount: float
    expense_desc: str
    user_expense_secondary_share: Dict[int, float] = None

    @model_validator(mode="after")
    def validate_secondary_shares(self):
        total_secondary_share = self.user_expense_secondary_share.values()
        total_sum = 0
        for x in total_secondary_share:
            total_sum = total_sum+x

        if total_sum != self.total_amount:
            raise PydanticCustomError(
                'expense-creation-error',
                "The expense shares don't add up to the total amount!",
            )
        return self

class ExpenseOut(CreateExpense):
    expense_key: int
    currency_code: str

class RequestExpense(BaseModel):
    expense_key: Optional[List[int]] = Query(None)
    currency_key: Optional[List[int]] = Query(None)