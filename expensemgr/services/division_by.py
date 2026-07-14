from sqlalchemy import select

from expensemgr.database.db import db_dependency
from expensemgr.database.models.expense import DivisionBy
from expensemgr.schemas.division_by import DivisionBy

class DivisionByService:
    def __init__(self, db: db_dependency):
        self.db = db

    def get_all_divsion_by(self):
        pass