import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from fastapi.testclient import TestClient
from dotenv import load_dotenv
from typing import Generator, List
import os
import sys
from datetime import timedelta
from jose import jwt

from expensemgr.database.db import Base, get_db
from expensemgr.main import app
from expensemgr.services.auth import AuthService
from expensemgr.services.utils import bcrypt_context
from expensemgr.database.models.users import User
from expensemgr.database.models.expense import Currency, Expense
from expensemgr.services.utils import *

load_dotenv()

TEST_DATABASE_URL = os.getenv("TESTDB_URL")

engine = create_engine(TEST_DATABASE_URL)

TestingSessionLocal=sessionmaker(autocommit=False, autoflush=False, bind=engine)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

@pytest.fixture(scope="module", autouse=True)
def setup_test_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="module")
def db(setup_test_database):
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind = connection)
    session.expire_on_commit = False
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="module")
def client(db: Session) -> Generator[TestClient, any, any]:
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db]=override_get_db

    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

@pytest.fixture(scope="module")
def test_user(db):
    user = User(
        username='testuser',
        phone_number='1111111111',
        email='test@mail.com',
        first_name='firstname',
        last_name='lastname',
        password=bcrypt_context.hash('password'),
    )
    db.add(user)
    db.commit()
    yield user

@pytest.fixture(scope="module")
def regular_user(db, test_user, client: TestClient):
    user : User = test_user
    access_token: str = AuthService(db).create_access_token(user.username, user.user_key, user.is_admin, timedelta(30))
    headers = {'Authorization' : f"Bearer {access_token}"}
    client.headers.update(headers)
    yield user
    client.headers.clear()

@pytest.fixture(scope="module")
def admin_user(db, test_user, client: TestClient):
    user : User = test_user
    access_token: str = AuthService(db).create_access_token(user.username, user.user_key, True, timedelta(30))
    headers = {'Authorization' : f"Bearer {access_token}"}
    client.headers.update(headers)
    yield user
    client.headers.clear()

@pytest.fixture(scope="module")
def currency(db, admin_user: User):
    test_currency = [
        Currency(
            meta_changed_by = admin_user.user_key,
            currency_code = "TESTCUR1",
            currency_desc = "Test Currency 1",
            currency_name = "Test name 1"
        ),
        Currency(
            meta_changed_by = admin_user.user_key,
            currency_code = "TESTCUR2",
            currency_desc = "Test Currency 2",
            currency_name = "Test name 2"
        )
    ]
    db.add_all(test_currency)
    db.commit()
    yield test_currency

@pytest.fixture(scope="module")
def expense(db, regular_user: User, currency: List[Currency]):
    test_expense = [
        Expense(
            user_id = regular_user.user_id,
            currency_id = currency[0].currency_id,
            amount = 100,
            description = "Test Expense 1"
        ),
        Expense(
            user_id = regular_user.user_id,
            currency_id = currency[1].currency_id,
            amount = 200,
            description = "Test Expense 2"
        )
    ]

    db.add_all(test_expense)
    db.commit()
    yield test_expense