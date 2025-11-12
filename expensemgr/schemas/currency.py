from pydantic import BaseModel

class CurrencyBase(BaseModel):
    currency_code: str
    currency_desc: str
    currency_name: str

class CurrencyOut(CurrencyBase):
    currency_key: int