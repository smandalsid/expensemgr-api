from fastapi import status
from jose import jwt
from datetime import timedelta

from expensemgr.services.auth import AuthService
from tests.unit.conftest import *
from expensemgr.services.utils import *

def test_create_user(db, client):
    request_data = {
        "username": "string1",
        "first_name": "string1",
        "last_name": "string1",
        "email": "user1@example.com",
        "phone_number": "2222222222",
        "password": "string1",
        "retyped_password": "string1"
    }

    response = client.post(url='/auth/', json=request_data)
    assert response.status_code == status.HTTP_201_CREATED

    model: User = db.query(User).filter(User.user_key == 1).first()
    assert model.username == request_data.get('username')
    assert model.first_name == request_data.get('first_name')
    assert model.last_name == request_data.get('last_name')
    assert model.email == request_data.get('email')