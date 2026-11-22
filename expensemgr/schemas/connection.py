from pydantic import BaseModel, model_validator
from pydantic_core import PydanticCustomError
from sqlalchemy import select, and_, or_

from expensemgr.database.db import get_db_class, DB
from expensemgr.database.models.connection import Connection

class ConnectionBase(BaseModel):
    user_key: int

    # @model_validator(mode="after")
    # def validate_user_combination_does_not_exist(self):
    #     db: DB = get_db_class()
    #     engine = db.get_engine()
    #     with engine.begin() as conn:
    #         query = select(
    #             select(1)
    #             .where(
    #                 or_(
    #                     and_(
    #                         Connection.user_key_1 == self.user_key_1,
    #                         Connection.user_key_2 == self.user_key_2
    #                     ),
    #                     and_(
    #                         Connection.user_key_1 == self.user_key_2,
    #                         Connection.user_key_2 == self.user_key_1
    #                     )
    #                 )
    #             )
    #             .exists()
    #         )
    #         if not conn.execute(statement=query).scalar():
    #             raise PydanticCustomError(
    #                 "connection-creation-error", "Connection with the user already present/received/sent!"
    #             )