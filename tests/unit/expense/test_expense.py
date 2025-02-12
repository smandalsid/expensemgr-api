from fastapi import status
from typing import List
import pytest

from expensemgr.database.models.expense import Expense, Currency

def test_get_all_expenses(db, client, regular_user, currency: List[Currency], expense: List[Expense]):
    response = client.get(url="/expense/get_all")
    assert response.status_code == status.HTTP_200_OK
    response = response.json()
    for x in range(len(response)):
        assert response[x].get('amount') == expense[x].amount
        assert response[x].get('description') == expense[x].description
        assert response[x].get('expense_id') == expense[x].expense_id
        assert response[x].get('currency_abbr') == currency[x].abbr

@pytest.mark.parametrize("expense_id, currency_id, expected_response", [
    ([1], [1], [{'amount': 100.0, 'description': 'Test Expense 1', 'expense_id': 1, 'currency_abbr': 'TESTCUR1'}]),
    ([2], [2], [{'amount': 200.0, 'description': 'Test Expense 2', 'expense_id': 2, 'currency_abbr': 'TESTCUR2'}]),
    ([1, 2], None, [{'amount': 100.0, 'description': 'Test Expense 1', 'expense_id': 1, 'currency_abbr': 'TESTCUR1'}, {'amount': 200.0, 'description': 'Test Expense 2', 'expense_id': 2, 'currency_abbr': 'TESTCUR2'}]),
    (None, [1, 2], [{'amount': 100.0, 'description': 'Test Expense 1', 'expense_id': 1, 'currency_abbr': 'TESTCUR1'}, {'amount': 200.0, 'description': 'Test Expense 2', 'expense_id': 2, 'currency_abbr': 'TESTCUR2'}]),
    (None, None, [{'amount': 100.0, 'description': 'Test Expense 1', 'expense_id': 1, 'currency_abbr': 'TESTCUR1'}, {'amount': 200.0, 'description': 'Test Expense 2', 'expense_id': 2, 'currency_abbr': 'TESTCUR2'}])
])
def test_get_expense(db, client, regular_user, currency: List[Currency], expense: List[Expense], expense_id, currency_id, expected_response):
    expense_ids = "&expense_id=".join(map(str, expense_id)) if expense_id is not None else ""
    currency_ids = "&currency_id=".join(map(str, currency_id)) if currency_id is not None else ""

    url = f"/expense/get?"
    if expense_ids:
        url = url + f"expense_id={expense_ids}"
        if currency_ids:
            url = url + f"&currency_id={currency_ids}"
    elif currency_ids:
        url = url + f"currency_id={currency_ids}"
    print(url)

    response = client.get(url=url)
    assert response.status_code == status.HTTP_200_OK
    print("Getting", response.json())
    print("Expected", expected_response)
    assert response.json() == expected_response