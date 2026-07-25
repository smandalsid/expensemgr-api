from sqlalchemy import select

from expensemgr.database.db import db_dependency
from expensemgr.database.models.expense import DivisionBy as division_by_db
from expensemgr.schemas.division_by import DivisionBy as division_by_pydantic
from expensemgr.utils.constants import DeleteInd, VersionActiveInd


class DivisionByException(Exception):
    pass


class DivisionByService:
    def __init__(self, db: db_dependency):
        self.db = db

    def get_all_divsion_by(self) -> division_by_pydantic:
        data = self.db.fetch_records(
            query=select(
                division_by_db.division_by_key.label("division_by_key"),
                division_by_db.division_by_code.label("division_by_code"),
            ).where(
                division_by_db.delete_ind == DeleteInd.NO.value,
                division_by_db.version_active_ind == VersionActiveInd.ACTIVE.value,
            )
        )
        return data
