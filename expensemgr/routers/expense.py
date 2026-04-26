from fastapi import APIRouter, HTTPException, status
from typing import List, Optional

from expensemgr.database.db import db_dependency
from expensemgr.routers.users import user_dependency
from expensemgr.schemas.expense import (CreateExpense, ExpenseOut)
from expensemgr.services.expense import ExpenseService
from expensemgr.utils.constants import auth_failed
from expensemgr.utils.logger import expense_mgr_logger

router = APIRouter(
    prefix="/expense",
    tags=["expense"],
)


@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=ExpenseOut)
@expense_mgr_logger.wrapper_logger(log_args=True)
def create_expense(
    db: db_dependency, user: user_dependency, create_expense: CreateExpense
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=auth_failed
        )

    return ExpenseService(db=db, user=user).create_expense(expense=create_expense)


@router.get("/get_all", status_code=status.HTTP_200_OK, response_model=Optional[List[ExpenseOut]])
@expense_mgr_logger.wrapper_logger(log_args=True)
def get_all_expenses(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=auth_failed
        )

    return ExpenseService(db=db, user=user).get_all_expenses()


@router.get("/get/", status_code=status.HTTP_200_OK, response_model=ExpenseOut)
def get_expense(
    db: db_dependency, user: user_dependency, expense_key: int
):
    try:
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=auth_failed
            )

        return ExpenseService(db=db, user=user).get_expense(expense_key=expense_key)
    except Exception as e:
        return e
