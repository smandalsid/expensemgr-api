from pydantic import BaseModel

class DivisionBy(BaseModel):
    division_by_key: int
    division_by_code: str
