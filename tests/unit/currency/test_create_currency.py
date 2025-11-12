from fastapi import status

from tests.unit.conftest import *
from expensemgr.database.models.expense import Currency

def test_create_currency(db, client, admin_user):
    request_data = {
        "currency_code": "testabbr",
        "currency_desc": "testdesc",
        "currency_name": "testname"
    }
    response = client.post(url="/currency/create", json=request_data)
    assert response.status_code == status.HTTP_201_CREATED

    model: Currency = db.query(Currency).filter(Currency.currency_key == 1).first()
    assert model.currency_code == request_data.get('currency_code')
    assert model.currency_desc == request_data.get('currency_desc')
    assert model.currency_name == request_data.get('currency_name')