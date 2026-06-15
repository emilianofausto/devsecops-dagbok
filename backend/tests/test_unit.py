"""
Automated Backend Unit Tests for DevSecOps Diary API.
Validates core CRUD logic, schema compliance, and status codes.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app, get_db
from app.database import Base

# Setup isolated in-memory database topology for hermetic unit testing
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(name="db_session")
def fixture_db_session():
    """Builds and tears down a clean database schema for each independent test."""
    # Force table creation explicitly inside the local test in-memory engine
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(name="client")
def fixture_client(db_session):
    """Overrides the FastAPI dependency injection context to target the test database."""
    def _get_test_db():
        try:
            yield db_session
        finally:
            pass

    # Bind the dependency override to intercept get_db calls during requests
    app.dependency_overrides[get_db] = _get_test_db
    
    from app.database import engine as app_engine
    Base.metadata.create_all(bind=engine)
    Base.metadata.create_all(bind=app_engine)

    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

# ----------------------------------------------------------------------
# TEST CASES (6 Tests for VG coverage compliance)
# ----------------------------------------------------------------------

def test_create_valid_diary_entry(client):
    """1. POST /api/entries - Asserts standard record instantiation succeeds (210/201)."""
    payload = {
        "title": "Unit Test Title",
        "category": "Testing",
        "content": "This is a clean cryptographic code block text."
    }
    response = client.post("/api/entries", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert "id" in data

def test_create_invalid_entry_empty_fields(client):
    """2. POST /api/entries - Asserts input validation rejects empty payloads (422)."""
    payload = {"title": "", "category": "DevSecOps", "content": ""}
    response = client.post("/api/entries", json=payload)
    assert response.status_code == 422  # Pydantic validation error code

def test_get_all_entries_empty_state(client):
    """3. GET /api/entries - Asserts collection retrieval returns an empty list initially (200)."""
    response = client.get("/api/entries")
    assert response.status_code == 200
    assert response.json() == []

def test_get_single_entry_not_found(client):
    """4. GET /api/entries/{id} - Asserts non-existent entity requests yield a 404 handler."""
    response = client.get("/api/entries/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_update_entry_valid_payload(client):
    """5. PUT /api/entries/{id} - Asserts complete field mutations update persistent layers."""
    # Seed data
    initial = client.post(
        "/api/entries",
        json={"title": "Old", "category": "A", "content": "Old Content"}
    )
    entry_id = initial.json()["id"]

    updated_payload = {"title": "New Title", "category": "B", "content": "New Content"}
    response = client.build_request("PUT", f"/api/entries/{entry_id}", json=updated_payload)
    res = client.send(response)
    assert res.status_code == 200
    assert res.json()["title"] == "New Title"

def test_delete_entry_lifecycle(client):
    """6. DELETE /api/entries/{id} - Asserts destructive routines clean storage structures."""
    initial = client.post(
        "/api/entries",
        json={"title": "To Delete", "category": "X", "content": "Text"}
    )
    entry_id = initial.json()["id"]

    delete_res = client.delete(f"/api/entries/{entry_id}")
    assert delete_res.status_code == 200

    # Confirm it cannot be fetched anymore
    get_res = client.get(f"/api/entries/{entry_id}")
    assert get_res.status_code == 404
