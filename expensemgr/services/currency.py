from typing import List

from expensemgr.database.db import db_dependency
from expensemgr.schemas.currency import CurrencyBase, CurrencyOut
from expensemgr.database.models.expense import Currency
from expensemgr.routers.users import user_dependency
from expensemgr.utils.logger import expense_mgr_logger

class CurrencyService:
    def __init__(self, db: db_dependency, user: user_dependency):
        self.db = db
        self.user = user

    def create_currency(self, currency: CurrencyBase) -> CurrencyBase:
        new_currency = Currency(
            currency_code = currency.currency_code,
            currency_desc = currency.currency_desc,
            currency_name = currency.currency_name,
            meta_changed_by = self.user.get('user_key'),
        )
        self.db.add(new_currency)
        self.db.commit()

        currency = self.db.query(Currency).filter(Currency.currency_key == new_currency.currency_key).first()
        return currency
    
    @expense_mgr_logger.wrapper_logger(log_args=True)
    def get_all_currency(self) -> List[CurrencyOut]:
        return self.db.query(Currency).all()