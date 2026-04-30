import os
from typing import Annotated, Generator, Optional

from dotenv import load_dotenv
from fastapi import Depends
from sqlalchemy import MetaData, create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from sqlalchemy.pool import QueuePool

from expensemgr.utils.logger import expense_mgr_logger
import asyncio

# load env variables
load_dotenv()

# dev db url
# SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")
# testing db url
TEST_DATABASE_URL = os.getenv("TESTDB_URL")
ENV = os.getenv("ENV")

SUPABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=os.getenv("SUPABASE_USER"),
    password=os.getenv("SUPABASE_PASSWORD"),
    host=os.getenv("SUPABASE_HOST"),
    port=int(os.getenv("SUPABASE_POOL_PORT", "6543")),
    database=os.getenv("SUPABASE_DB"),
)
SUPABASE_DIRECT_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=os.getenv("SUPABASE_USER"),
    password=os.getenv("SUPABASE_PASSWORD"),
    host=os.getenv("SUPABASE_HOST"),
    port=int(os.getenv("SUPABASE_DIRECT_PORT", "5432")),
    database=os.getenv("SUPABASE_DB"),
)

metadata = MetaData()
Base = declarative_base(metadata=metadata)


class DBException(Exception):
    pass


class DB:
    _engine = None
    _instance: Optional["DB"] = None

    @classmethod
    def get_instance(cls) -> "DB":
        if cls._instance is None:
            cls._instance = super(DB, cls).__new__(cls)
            cls._initialise()
        return cls._instance

    @classmethod
    def _initialise(cls):
        if ENV == "dev":
            cls._engine = create_engine(
                SUPABASE_URL,
                max_overflow=10,
                pool_size=20,
                # echo=True,echo_pool="debug"
            )
        elif ENV == "test":
            cls._engine = create_engine(TEST_DATABASE_URL)

    @classmethod
    def get_engine(cls):
        instance = cls.get_instance()
        return instance._engine

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
