import os
from typing import Annotated, Generator, Optional

from dotenv import load_dotenv
from fastapi import Depends
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from sqlalchemy.pool import QueuePool

from expensemgr.utils.logger import expense_mgr_logger

# load env variables
load_dotenv()

# dev db url
SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")
# testing db url
TEST_DATABASE_URL = os.getenv("TESTDB_URL")
ENV = os.getenv("ENV")

if ENV == "dev":
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        max_overflow=10,
        pool_size=20,
        # echo=True,echo_pool="debug"
    )
elif ENV == "test":
    engine = create_engine(TEST_DATABASE_URL)

# create db session
# sessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)

metadata = MetaData()
Base = declarative_base(metadata=metadata)


class DBException(Exception):
    pass


class DB:
    _engine = engine
    _instance: Optional["DB"] = None

    @classmethod
    def get_instance(cls) -> "DB":
        if cls._instance is not None:
            return cls._instance
        cls._instance = cls.__new__(cls)
        return cls._instance

    @classmethod
    def fetch_one_record(cls, query):
        with cls._engine.connect() as conn:
            result = conn.execute(query).fetchone()
        return result

    @classmethod
    def fetch_records(cls, query):
        with cls._engine.connect() as conn:
            results = conn.execute(query).fetchall()
        return results

    @classmethod
    def execute_query(cls, query):
        with cls._engine.connect() as connection:
            with connection.begin() as transaction:
                result = connection.execute(query)
                transaction.commit()
        return result


# creating a db dependency for injection in routers later
# def get_db():
#     db = sessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


def get_db_class() -> Generator[DB, None, None]:
    try:
        db = DB.get_instance()
        return db
    except DBException as e:
        expense_mgr_logger.logger.exception("Error creating DB class!")
        raise e


db_dependency = Annotated[DB, Depends(get_db_class)]
