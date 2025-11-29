from expensemgr.database.db import DB
import json
from expensemgr.database.models.expense import Currency
from sqlalchemy import insert

db = DB.get_instance()

with open("expensemgr/utils/exchange_rates/exchange_rates.json") as f:
    data = json.load(f)
currency_codes = data.get("data").keys()

for code in currency_codes:
    stmt = insert(
        Currency
    ).values(
        currency_code=code,
        currency_desc=code,
        currency_name=code,
        meta_changed_by=2,
    )
    db.execute_query(stmt)