from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from dotenv import load_dotenv
import os
from fastapi import Depends
from typing import Annotated

# load env variables
load_dotenv()

# dev db url
SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")
# testing db url
TEST_DATABASE_URL = os.getenv("TESTDB_URL")
ENV = os.getenv("ENV")

if ENV == "dev":
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
elif ENV == "test":
    engine = create_engine(TEST_DATABASE_URL)

# create db session
sessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)

metadata = MetaData()
Base = declarative_base(metadata=metadata)

# creating a db dependency for injection in routers later
def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
