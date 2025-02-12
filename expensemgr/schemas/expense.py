from fastapi import Query
from pydantic import BaseModel
from typing import Optional, List

class ExpenseBase(BaseModel):
    amount: float
    description: str

class CreateExpense(ExpenseBase):
    currency_id: int

class ExpenseOut(ExpenseBase):
    expense_id: int
    currency_abbr: str

class RequestExpense(BaseModel):
    expense_id: Optional[List[int]] = Query(None)
    currency_id: Optional[List[int]] = Query(None)