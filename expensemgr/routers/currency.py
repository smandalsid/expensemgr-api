from fastapi import APIRouter, status, HTTPException
from typing import List

from expensemgr.database.db import db_dependency
from expensemgr.routers.users import user_dependency
from expensemgr.schemas.currency import CurrencyBase, CurrencyOut
from expensemgr.services.currency import CurrencyService
from expensemgr.utils.logger import expense_mgr_logger

router = APIRouter(
    prefix='/currency',
    tags=['currency'],
)

@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=CurrencyBase)
async def create_currency(user: user_dependency, db: db_dependency, currency: CurrencyBase):
    if user is None or user.get('is_admin')==False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    
    return CurrencyService(db=db, user=user).create_currency(currency=currency)

@router.get("/get_all", status_code=status.HTTP_200_OK, response_model=List[CurrencyOut])
@expense_mgr_logger.wrapper_logger(log_args=True)
def get_all_currency(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    
    return CurrencyService(db=db, user=user).get_all_currency()