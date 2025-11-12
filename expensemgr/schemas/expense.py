from fastapi import Query
from pydantic import BaseModel
from typing import Optional, List

class CreateExpense(BaseModel):
    primary_user_key: int
    currency_key: int
    division_by_key: int
    total_amount: float
    expense_desc: str
    secondary_user_key_list: List[int] = None
    expense_share_list: List[float] = None

class ExpenseOut(ExpenseBase):
    expense_key: int
    currency_code: str

class RequestExpense(BaseModel):
    expense_key: Optional[List[int]] = Query(None)
    currency_key: Optional[List[int]] = Query(None)