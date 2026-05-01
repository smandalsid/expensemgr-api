from fastapi import status
from jose import jwt
from datetime import timedelta

from expensemgr.services.auth import AuthService
from tests.unit.conftest import *
from expensemgr.services.utils import *

def test_authenticate_user(db, test_user):
    user = AuthService(db).authenticate_user(username='testuser', password='password')
    assert user is not None
    assert user.username == 'testuser'
    assert bcrypt_context.verify('password', user.password)

def test_create_access_token(db):
    token = AuthService(db).create_access_token(username='username', user_key=1, is_admin = False, expires_delta=timedelta(minutes=30))
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={'verify_signature':False})

    assert decoded_token['sub'] == 'username'
    assert decoded_token['user_key'] == 1
    assert decoded_token['is_admin'] == False

def test_login_for_access_token(test_user, client):
    form_data: dict = {
        "username": "testuser",
        "password": "password",
    }

    response = client.post(url="/auth/token", data=form_data)
    assert response.status_code == status.HTTP_200_OK
    response = response.json()
    assert "access_token" in response
    assert "token_type" in response
    assert response['token_type'] == 'bearer'