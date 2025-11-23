from typing import List

from fastapi import HTTPException, status
from sqlalchemy import insert, select

from expensemgr.database.db import db_dependency
from expensemgr.database.models.expense import Currency
from expensemgr.routers.users import user_dependency
from expensemgr.schemas.currency import CurrencyBase, CurrencyOut
from expensemgr.utils.logger import expense_mgr_logger


class CurrencyService:
    def __init__(self, db: db_dependency, user: user_dependency):
        self.db = db
        self.user = user

    @expense_mgr_logger.wrapper_logger(log_args=True)
    def create_currency(self, currency: CurrencyBase) -> CurrencyBase:
        if self.db.fetch_one_record(
            select(Currency).where(Currency.currency_code == currency.currency_code)
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Currency code already exists!",
            )
        new_currency = self.db.execute_query(
            insert(Currency).values(
                currency_code=currency.currency_code,
                currency_desc=currency.currency_desc,
                currency_name=currency.currency_name,
                meta_changed_by=self.user.get("user_key"),
            )
        )

        currency = self.db.fetch_one_record(
            select(Currency).where(
                Currency.currency_key == new_currency.inserted_primary_key[0]
            )
        )
        return currency

    @expense_mgr_logger.wrapper_logger(log_args=True)
    def get_all_currency(self) -> List[CurrencyOut]:
        return self.db.fetch_records(select(Currency))
