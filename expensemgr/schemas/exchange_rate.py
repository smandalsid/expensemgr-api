from pydantic import BaseModel


class ExchangeRateOut(BaseModel):
    user_curr_code: str
    db_curr_code: str
    exchange_rate: float
