from fastapi import status

from tests.unit.conftest import *
from expensemgr.database.models.expense import Currency

def test_get_all_currency(db, client, regular_user, currency: List[Currency]):
    response = client.get(url="/currency/get_all")
    assert response.status_code == status.HTTP_200_OK
    response = response.json()
    for x in range(len(response)):
        assert response[x].get('abbr') == currency[x].abbr
        assert response[x].get('desc') == currency[x].desc
