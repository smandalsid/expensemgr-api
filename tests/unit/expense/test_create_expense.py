from fastapi import status

from tests.unit.conftest import *
from expensemgr.database.models.expense import Expense, Currency

def test_create_expense(db, client, regular_user, currency: List[Currency]):
    request_data = {
        "amount":100,
        "description": "Test Expenditure",
        "currency_id": currency[0].currency_id,
    }

    response = client.post(url="/expense/create", json=request_data)
    assert response.status_code == status.HTTP_201_CREATED

    model: Expense = db.query(Expense).filter(Expense.expense_id == 1).first()
    assert model.amount == request_data.get('amount')
    assert model.description == request_data.get('description')