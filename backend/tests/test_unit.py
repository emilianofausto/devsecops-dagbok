"""
Automated Backend Unit Tests for DevSecOps Diary API.
Validates core CRUD logic, schema compliance, and status codes.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from app.main import app, get_db, verify_token
from app.database import Base

TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# A dummy JWT: Header.Payload.Signature
# Payload: {"sub": "1234567890", "name": "Test User"}
AUTH_HEADERS = {
    "Authorization": (
        "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IlRlc3QgVXNlciJ9."
        "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    )
}

def mock_verify_token():
    """This is to generate a valid answer from the auth function"""
    return "auth0|test_user"

@pytest.fixture(name="db_session")
def fixture_db_session():
    """Builds and tears down a clean database schema."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(name="client")
def fixture_client(db_session):
    """Overrides the FastAPI dependency injection context."""
    def _get_test_db():
        yield db_session

    app.dependency_overrides[get_db] = _get_test_db
    app.dependency_overrides[verify_token] = mock_verify_token
    
    with TestClient(app) as test_client:
        yield test_client
        
    app.dependency_overrides.clear()

# ----------------------------------------------------------------------
# TEST CASES
# ----------------------------------------------------------------------

def test_create_valid_diary_entry(client):
    """1. POST /api/entries - Asserts record instantiation succeeds."""
    payload = {"title": "Unit Test", "category": "Testing", "content": "Content"}
    response = client.post("/api/entries", json=payload, headers=AUTH_HEADERS)
    assert response.status_code == 201

def test_create_invalid_entry_empty_fields(client):
    """2. POST /api/entries - Asserts validation rejects empty payloads."""
    payload = {"title": "", "category": "DevSecOps", "content": ""}
    response = client.post("/api/entries", json=payload, headers=AUTH_HEADERS)
    assert response.status_code == 422

def test_get_all_entries_empty_state(client):
    """3. GET /api/entries - Asserts empty list returns 200."""
    response = client.get("/api/entries", headers=AUTH_HEADERS)
    assert response.status_code == 200
    assert response.json() == []

def test_get_single_entry_not_found(client):
    """4. GET /api/entries/{id} - Asserts non-existent entity yields 404."""
    response = client.get("/api/entries/999", headers=AUTH_HEADERS)
    assert response.status_code == 404

def test_update_entry_valid_payload(client):
    """5. PUT /api/entries/{id} - Asserts updates persist."""
    initial_payload = {"title": "Old", "category": "A", "content": "Old"}
    initial = client.post(
        "/api/entries", json=initial_payload, headers=AUTH_HEADERS
    )
    entry_id = initial.json()["id"]

    payload = {"title": "New", "category": "B", "content": "New"}
    res = client.put(f"/api/entries/{entry_id}", json=payload, headers=AUTH_HEADERS)
    assert res.status_code == 200
    assert res.json()["title"] == "New"

def test_delete_entry_lifecycle(client):
    """6. DELETE /api/entries/{id} - Asserts deletion cleans storage."""
    payload = {"title": "Del", "category": "X", "content": "X"}
    initial = client.post("/api/entries", json=payload, headers=AUTH_HEADERS)
    entry_id = initial.json()["id"]

    delete_res = client.delete(
        f"/api/entries/{entry_id}", headers=AUTH_HEADERS
    )
    assert delete_res.status_code == 200

    get_res = client.get(f"/api/entries/{entry_id}", headers=AUTH_HEADERS)
    assert get_res.status_code == 404
