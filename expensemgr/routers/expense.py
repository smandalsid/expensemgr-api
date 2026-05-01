from fastapi import APIRouter, HTTPException, status
from typing import List, Optional

from expensemgr.database.db import db_dependency
from expensemgr.routers.users import user_dependency
from expensemgr.schemas.expense import CreateExpense, ExpenseOut, EditExpense
from expensemgr.services.expense import ExpenseService, ExpenseCreationException, ExpenseNotFoundException, ExpenseEditException, ExpenseDeleteException
from expensemgr.utils.constants import auth_failed
from expensemgr.utils.logger import expense_mgr_logger

router = APIRouter(
    prefix="/expense",
    tags=["expense"],
)


@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=ExpenseOut)
@expense_mgr_logger.wrapper_logger(log_args=False)
def create_expense(
    db: db_dependency, user: user_dependency, create_expense: CreateExpense
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=auth_failed
        )
    try:
        return ExpenseService(db=db, user=user).create_expense(expense=create_expense)
    except ExpenseCreationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/get_all",
    status_code=status.HTTP_200_OK,
    response_model=Optional[List[ExpenseOut]],
)
@expense_mgr_logger.wrapper_logger(log_args=False)
def get_all_expenses(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=auth_failed
        )

    return ExpenseService(db=db, user=user).get_all_expenses()

@router.get("/get_active", status_code=status.HTTP_200_OK, response_model=Optional[List[ExpenseOut]])
@expense_mgr_logger.wrapper_logger(log_args = False)
def get_active_expenses(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=auth_failed
        )
    return ExpenseService(db=db, user=user).get_active_expenses()


@router.get("/get/", status_code=status.HTTP_200_OK, response_model=ExpenseOut)
@expense_mgr_logger.wrapper_logger(log_args=False)
def get_expense(db: db_dependency, user: user_dependency, expense_key: int):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=auth_failed
        )
    try:
        return ExpenseService(db=db, user=user).get_expense(expense_key=expense_key)
    except ExpenseNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
    
@router.put("/edit", status_code=status.HTTP_200_OK)
@expense_mgr_logger.wrapper_logger(log_args=False)
def edit_expense(db: db_dependency, user: user_dependency, expense: EditExpense):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=auth_failed
        )
    try:
        return ExpenseService(db=db, user=user).edit_expense(expense=expense)
    except ExpenseEditException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/delete", status_code=status.HTTP_200_OK)
@expense_mgr_logger.wrapper_logger(log_args=False)
def delete_expense(db: db_dependency, user: user_dependency, expense_key: int):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=auth_failed
        )
    try:
        return ExpenseService(db=db, user=user).delete_expense(expense_key=expense_key)
    except ExpenseDeleteException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put("/settle", status_code=status.HTTP_200_OK, response_model=ExpenseOut)
@expense_mgr_logger.wrapper_logger(log_args=False)
def settle_expense(db: db_dependency, user: user_dependency):
    pass