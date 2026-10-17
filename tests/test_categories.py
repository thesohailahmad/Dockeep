import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

NOT_FOUND_ID = 999_999 


def make_auth_headers(prefix: str) -> dict:
    username = f"{prefix}_{uuid.uuid4().hex[:8]}"
    password = "testpassword123"

    register = client.post(
        "/auth/register/",
        json={
            "name": "Test User",
            "username": username,
            "password": password,
            "email": f"{username}@example.com",
        },
    )
    assert register.status_code == 201, register.text  

    login = client.post(
        "/auth/login/", data={"username": username, "password": password}
    )
    assert login.status_code == 200, login.text

    return {"Authorization": f"Bearer {login.json()['access_token']}"}



@pytest.fixture()
def auth_headers() -> dict:
    return make_auth_headers("sohail")


@pytest.fixture()
def auth_headers_B() -> dict:
    return make_auth_headers("sohailb")


def create_category(data: dict, name: str):
    return client.post(
        "/categories/create_category", json={"name": name}, headers=data
    )


def get_category(data: dict, category_id: int):
    return client.get(f"/categories/view_category/{category_id}", headers=data)


def update_category(data: dict, category_id: int, name: str):
    return client.put(
        f"/categories/update_category/{category_id}",
        json={"name": name},
        headers=data,
    )


def delete_category(data: dict, category_id: int):
    return client.delete(f"/categories/delete_category/{category_id}", headers=data)



def test_create_category(auth_headers):
    
    response = create_category(auth_headers, "Certificates")
    assert response.status_code == 201
    assert response.json()["name"] == "Certificates"


def test_create_category_empty(auth_headers):
    
    response = create_category(auth_headers, " ")
    assert response.status_code == 422


def test_create_category_missing_name_field(auth_headers):
    
    response = client.post("/categories/create_category", json={}, headers=auth_headers)
    assert response.status_code == 422


def test_category_duplicate_name(auth_headers):
    
    assert create_category(auth_headers, "Certificates").status_code == 201
    response = create_category(auth_headers, "Certificates")
    assert response.status_code == 409


def test_duplicate_name_rejected_case_insensitive(auth_headers):

    assert create_category(auth_headers, "Certificates").status_code == 201
    response = create_category(auth_headers, "certificates")
    assert response.status_code == 409


def test_same_name_allowed_for_different_users(auth_headers, auth_headers_B):

    assert create_category(auth_headers, "Certificates").status_code == 201
    assert create_category(auth_headers_B, "Certificates").status_code == 201


def test_create_category_without_token():
    
    response = client.post("/categories/create_category", json={"name": "Notes"})
    assert response.status_code == 401



def test_list_returns_only_own_categories(auth_headers, auth_headers_B):
    
    create_category(auth_headers, "Screenshot")
    create_category(auth_headers_B, "Medical Certificate")

    response = client.get("/categories/view_category", headers=auth_headers)

    assert response.status_code == 200
    assert [c["name"] for c in response.json()] == ["Screenshot"]


def test_list_is_empty_for_new_user(auth_headers):

    response = client.get("/categories/view_category", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []



def test_get_existing_category(auth_headers):

    category_id = create_category(auth_headers, "Notes").json()["category_id"]
    response = get_category(auth_headers, category_id)

    assert response.status_code == 200
    assert response.json()["category_id"] == category_id
    assert response.json()["name"] == "Notes"


def test_get_category_by_id_that_does_not_exist(auth_headers):
    
    response = get_category(auth_headers, NOT_FOUND_ID)
    assert response.status_code == 404


def test_cannot_get_other_users_category(auth_headers, auth_headers_B):

    category_id = create_category(auth_headers, "Private").json()["category_id"]
    response = get_category(auth_headers_B, category_id)
    assert response.status_code == 404  



def test_update_category_name(auth_headers):
    
    category_id = create_category(auth_headers, "Old name").json()["category_id"]
    response = update_category(auth_headers, category_id, "New name")
    assert response.status_code == 200
    assert response.json()["name"] == "New name"
    assert get_category(auth_headers, category_id).json()["name"] == "New name"


def test_rename_to_same_name_with_different_case_is_allowed(auth_headers):
    
    category_id = create_category(auth_headers, "Notes").json()["category_id"]
    response = update_category(auth_headers, category_id, "NOTES")
    assert response.status_code == 200
    assert response.json()["name"] == "NOTES"


def test_rename_to_existing_name_rejected(auth_headers):
    
    create_category(auth_headers, "First")
    second_id = create_category(auth_headers, "Second").json()["category_id"]
    response = update_category(auth_headers, second_id, "First")
    assert response.status_code == 409


def test_cannot_update_other_users_category(auth_headers, auth_headers_B):
    
    category_id = create_category(auth_headers, "Original").json()["category_id"]
    response = update_category(auth_headers_B, category_id, "Hacked")
    assert response.status_code == 404
    assert get_category(auth_headers, category_id).json()["name"] == "Original"


def test_delete_category(auth_headers):
    
    category_id = create_category(auth_headers, "Temporary").json()["category_id"]
    response = delete_category(auth_headers, category_id)
    assert response.status_code in (200, 204)
    assert get_category(auth_headers, category_id).status_code == 404


def test_cannot_delete_other_users_category(auth_headers, auth_headers_B):
    
    category_id = create_category(auth_headers, "Keep me").json()["category_id"]
    response = delete_category(auth_headers_B, category_id)
    assert response.status_code == 404
    assert get_category(auth_headers, category_id).status_code == 200