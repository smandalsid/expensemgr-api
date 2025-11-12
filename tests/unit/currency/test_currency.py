from fastapi import status

from tests.unit.conftest import *
from expensemgr.database.models.expense import Currency

def test_get_all_currency(db, client, regular_user, currency: List[Currency]):
    response = client.get(url="/currency/get_all")
    assert response.status_code == status.HTTP_200_OK
    response = response.json()
    for x in range(len(response)):
        assert response[x].get('currency_code') == currency[x].currency_code
        assert response[x].get('currency_desc') == currency[x].currency_desc
        assert response[x].get('currency_name') == currency[x].currency_name
