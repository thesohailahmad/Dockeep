import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.routers import documents as documents_router

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


@pytest.fixture(autouse=True)
def temp_storage(tmp_path, monkeypatch):
    monkeypatch.setattr(documents_router, "UPLOAD_DIRECTORY", tmp_path)
    return tmp_path


def upload(headers,title="My CV" , content=b"hello world",filename="cv.txt",content_type="text/plain",**form_fields,):
    return client.post(
        "/documents/upload_document",
        headers=headers,
        data={"title": title, **form_fields},                # text fields
        files={"file": (filename, content, content_type)},   # (name, bytes, mime)
    )


def create_category(headers, name="Notes") -> int:
    response = client.post(
        "/categories/create_category", json={"name": name}, headers=headers
    )
    assert response.status_code == 201, response.text
    return response.json()["category_id"]


def list_documents(headers, **params):
    
    return client.get("/documents/view_document", headers=headers, params=params)


def titles(headers) -> list:
    
    return [d["title"] for d in list_documents(headers).json()]


def update_document(headers, document_id, payload: dict):
    
    return client.put(
        f"/documents/update_document/{document_id}", json=payload, headers=headers
    )


def delete_document(headers, document_id):
    return client.delete(f"/documents/delete_document/{document_id}", headers=headers)



def test_upload_valid_file(auth_headers):
    
    content = b"hello world"
    response = upload(auth_headers, title="My CV", content=content)
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "My CV"
    assert body["original_filename"] == "cv.txt"
    assert body["mime_type"] == "text/plain"
    assert body["file_size"] == len(content)
    assert "document_id" in body


def test_upload_saves_file_on_disk(auth_headers, temp_storage):
    
    upload(auth_headers, content=b"hello world")
    saved = list(temp_storage.iterdir())
    assert len(saved) == 1
    assert saved[0].read_bytes() == b"hello world"


def test_upload_hides_server_paths(auth_headers):
    
    body = upload(auth_headers).json()
    assert "file_path" not in body
    assert "stored_filename" not in body


def test_upload_disallowed_file_type(auth_headers, temp_storage):
    
    response = upload(
        auth_headers,
        filename="virus.exe",
        content_type="application/x-msdownload",
    )
    assert response.status_code == 400
    assert list(temp_storage.iterdir()) == []


def test_upload_empty_file(auth_headers, temp_storage):
    
    response = upload(auth_headers, content=b"")
    assert response.status_code == 400
    assert list(temp_storage.iterdir()) == []   # nothing left behind


def test_upload_file_too_large(auth_headers, temp_storage, monkeypatch):
    
    monkeypatch.setattr(documents_router, "MAX_FILE_SIZE", 10)   # limit: 10 bytes
    response = upload(auth_headers, content=b"x" * 100)
    assert response.status_code in (400, 413)
    assert list(temp_storage.iterdir()) == []


def test_upload_missing_title(auth_headers):
    
    response = client.post(
        "/documents/upload_document",
        headers=auth_headers,
        files={"file": ("cv.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 422


def test_upload_missing_file(auth_headers):
    
    response = client.post(
        "/documents/upload_document",
        headers=auth_headers,
        data={"title": "No file here"},
    )
    assert response.status_code == 422


def test_upload_without_token():
    
    response = client.post(
        "/documents/upload_document",
        data={"title": "x"},
        files={"file": ("cv.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 401


def test_upload_with_own_category(auth_headers):
    category_id = create_category(auth_headers)
    response = upload(auth_headers, category_id=category_id)
    assert response.status_code == 201
    assert response.json()["category_id"] == category_id


def test_upload_with_other_users_category(auth_headers, auth_headers_B):
    
    category_id = create_category(auth_headers)

    response = upload(auth_headers_B, category_id=category_id)

    assert response.status_code == 404


def test_upload_with_category_that_does_not_exist(auth_headers):
    
    response = upload(auth_headers, category_id=NOT_FOUND_ID)

    assert response.status_code == 404



def test_list_returns_only_own_documents(auth_headers, auth_headers_B):
    
    upload(auth_headers, title="Medical")
    upload(auth_headers_B, title="Health")

    response = list_documents(auth_headers)

    assert response.status_code == 200
    assert [d["title"] for d in response.json()] == ["Medical"]


def test_list_is_empty_for_new_user(auth_headers):
    
    response = list_documents(auth_headers)

    assert response.status_code == 200
    assert response.json() == []


def test_list_pagination(auth_headers):
    
    for i in range(3):
        assert upload(auth_headers, title=f"Doc {i}").status_code == 201

    first_page = list_documents(auth_headers, skip=0, limit=2)
    second_page = list_documents(auth_headers, skip=2, limit=2)

    assert first_page.status_code == 200
    assert len(first_page.json()) == 2
    assert len(second_page.json()) == 1



def test_update_document_title(auth_headers):
    
    document_id = upload(auth_headers, title="Old title").json()["document_id"]

    response = update_document(auth_headers, document_id, {"title": "New title"})

    assert response.status_code == 200
    assert response.json()["title"] == "New title"
    assert titles(auth_headers) == ["New title"]   # really saved


def test_cannot_update_other_users_document(auth_headers, auth_headers_B):
    
    document_id = upload(auth_headers, title="Original").json()["document_id"]

    response = update_document(auth_headers_B, document_id, {"title": "Hacked"})

    assert response.status_code == 404
    assert titles(auth_headers) == ["Original"]   # owner's document untouched


def test_update_document_that_does_not_exist(auth_headers):
    
    response = update_document(auth_headers, NOT_FOUND_ID, {"title": "Whatever"})

    assert response.status_code == 404


def test_update_title_to_null_rejected(auth_headers):
    
    document_id = upload(auth_headers, title="Keep me").json()["document_id"]

    response = update_document(auth_headers, document_id, {"title": None})
    assert response.status_code == 422
    assert titles(auth_headers) == ["Keep me"]


def test_cannot_move_document_to_other_users_category(auth_headers, auth_headers_B):
    
    category_id = create_category(auth_headers)
    document_id = upload(auth_headers_B).json()["document_id"]

    response = update_document(auth_headers_B, document_id, {"category_id": category_id})

    assert response.status_code == 404



def test_delete_document_then_list(auth_headers):
    document_id = upload(auth_headers).json()["document_id"]

    response = delete_document(auth_headers, document_id)

    assert response.status_code in (200, 204)
    assert list_documents(auth_headers).json() == []


def test_delete_document_removes_file_from_disk(auth_headers, temp_storage):
    document_id = upload(auth_headers).json()["document_id"]
    assert len(list(temp_storage.iterdir())) == 1

    delete_document(auth_headers, document_id)

    
    assert list(temp_storage.iterdir()) == []


def test_cannot_delete_other_users_document(auth_headers, auth_headers_B):
    document_id = upload(auth_headers, title="Keep me").json()["document_id"]

    response = delete_document(auth_headers_B, document_id)

    assert response.status_code == 404
    assert titles(auth_headers) == ["Keep me"]   


def test_delete_document_that_does_not_exist(auth_headers):
    response = delete_document(auth_headers, NOT_FOUND_ID)

    assert response.status_code == 404