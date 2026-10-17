import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture()
def client():
    return TestClient(app)


def new_user_register(prefix: str = "testuser") -> dict:

    suffix = uuid.uuid4().hex[:8]
    return {
        "name": "Test User",
        "username": f"{prefix}_{suffix}",
        "email": f"{prefix}_{suffix}@example.com",
        "password": "StrongPass123",
    }


@pytest.fixture()
def registered_user(client):
    payload = new_user_register()
    response = client.post("/auth/register/", json=payload)
    assert response.status_code == 201, response.text
    return payload


def register(client, payload: dict):
    return client.post("/auth/register/", json=payload)


def login(client, username: str, password: str):
    return client.post(
        "/auth/login/", data={"username": username, "password": password}
    )



def test_user_register(client):
    
    response = register(client, new_user_register())
    assert response.status_code == 201


def test_user_invalid_email(client):
    
    payload = {**new_user_register(), "email": "testexample"}
    assert register(client, payload).status_code == 422


def test_user_duplicate_email(client, registered_user):

    payload = {**new_user_register(), "email": registered_user["email"]}
    assert register(client, payload).status_code == 400


def test_user_duplicate_username(client, registered_user):

    payload = {**new_user_register(), "username": registered_user["username"]}
    assert register(client, payload).status_code == 400


def test_user_missing_username(client):
    
    payload = new_user_register()
    del payload["username"]
    assert register(client, payload).status_code == 422


def test_user_missing_email(client):
    
    payload = new_user_register()
    del payload["email"]
    assert register(client, payload).status_code == 422


def test_user_missing_name(client):
   
    payload = new_user_register()
    del payload["name"]
    assert register(client, payload).status_code == 422


def test_user_missing_password(client):
    
    payload = new_user_register()
    del payload["password"]
    assert register(client, payload).status_code == 422


def test_user_password_length(client):

    payload = {**new_user_register(), "password": "23455"}
    assert register(client, payload).status_code == 422


def test_user_empty_value(client):

    payload = {**new_user_register(), "password": " ", "email": " "}
    assert register(client, payload).status_code == 422



def test_user_login(client, registered_user):

    response = login(client, registered_user["username"], registered_user["password"])
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_user_wrong_password(client, registered_user):
   
    response = login(client, registered_user["username"], "WrongPass999")
    assert response.status_code == 401


def test_user_wrong_username(client, registered_user):

    response = login(client, "no_such_user_" + uuid.uuid4().hex[:8], registered_user["password"])
    assert response.status_code == 401


def test_user_missing_username_in_login(client, registered_user):
    
    response = login(client, "", registered_user["password"])
    assert response.status_code == 422


def test_user_missing_password_in_login(client, registered_user):
    
    response = login(client, registered_user["username"], "")
    assert response.status_code == 422