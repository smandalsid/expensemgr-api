from fastapi import status

from tests.unit.conftest import *


def test_get_user(client, regular_user: User):
    response = client.get(url="/users/")
    assert response.status_code == status.HTTP_200_OK

    response = response.json()
    assert response.get("username") == regular_user.username
    assert response.get("first_name") == regular_user.first_name
    assert response.get("last_name") == regular_user.last_name
    assert response.get("email") == regular_user.email
    assert response.get("phone_number") == regular_user.phone_number


def test_create_existing_user(client, regular_user):
    request_data = {
        "username": "testuser",
        "phone_number": "1111111111",
        "email": "test@mail.com",
        "first_name": "firstname",
        "last_name": "lastname",
        "password": "password",
        "retyped_password": "password",
    }

    response = client.post(url="/auth/", json=request_data)
    assert response.status_code == status.HTTP_409_CONFLICT
    response = response.json()
    assert response.get("detail") == "Username already exists"


def test_create_bad_user_phoneno(client, regular_user):
    request_data = {
        "username": "testuser1",
        "phone_number": "1111111111",
        "email": "test@mail.com",
        "first_name": "firstname",
        "last_name": "lastname",
        "password": "password",
        "retyped_password": "password",
    }
    response = client.post(url="/auth/", json=request_data)
    assert response.status_code == status.HTTP_409_CONFLICT
    response = response.json()
    assert response.get("detail") == "Phone number already exists"


def test_create_bad_user(client, regular_user):
    request_data = {
        "username": "testuser1",
        "phone_number": "1111111112",
        "email": "testmail.com",
        "first_name": "f",
        "last_name": "l",
        "password": "password",
        "retyped_password": "password1",
    }
    response = client.post(url="/auth/", json=request_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    response = response.json()
    assert response == {
        "detail": [
            {
                "type": "value_error",
                "loc": ["body", "email"],
                "msg": "value is not a valid email address: An email address must have an @-sign.",
                "input": "testmail.com",
                "ctx": {"reason": "An email address must have an @-sign."},
            }
        ]
    }
