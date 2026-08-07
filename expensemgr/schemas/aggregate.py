from pydantic import BaseModel


class AggregateShareOut(BaseModel):
    user_key: int
    first_name: str
    last_name: str
    user_total: float
