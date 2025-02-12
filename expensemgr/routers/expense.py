from fastapi import APIRouter, status, HTTPException, Query
from typing import List, Optional

from expensemgr.database.db import db_dependency
from expensemgr.schemas.expense import ExpenseBase, CreateExpense, ExpenseOut, RequestExpense
from expensemgr.routers.users import user_dependency
from expensemgr.services.expense import ExpenseService

router = APIRouter(
    prefix='/expense',
    tags=['expense'],
)

@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=ExpenseBase)
async def create_expense(db: db_dependency, user: user_dependency, create_expense: CreateExpense):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    
    return ExpenseService(db=db, user=user).create_expense(expense=create_expense)

@router.get("/get_all", status_code=status.HTTP_200_OK, response_model=List[ExpenseOut])
async def get_all_expenses(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    
    return ExpenseService(db=db, user=user).get_all_expenses()

@router.get("/get/", status_code=status.HTTP_200_OK, response_model=List[ExpenseOut])
async def get_expense(
        db: db_dependency,
        user: user_dependency,
        request: RequestExpense = Query(...)
    ):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    
    return ExpenseService(db=db, user=user).get_expense(request=request)