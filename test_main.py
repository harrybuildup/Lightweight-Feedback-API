import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

test_feedback_db = []  # This will be used to store feedback entries during tests

def test_submit_feedback_success():
    test_feedback_db.clear()  # Clear the test database before the test
    feedback_data = {
        "email": "test@example.com",
        "category": "bug",
        "description": "This is a test feedback entry."
    }
    response = client.post("/feedback", json=feedback_data)
    assert response.status_code == 200
    assert response.json()["message"] == "Feedback submitted successfully"

def test_submit_feedback_invalid_email():
    feedback_data = {
        "email": "invalid-email",
        "category": "feature",
        "description": "This is a test feedback entry with invalid email."
    }
    response = client.post("/feedback", json=feedback_data)
    assert response.status_code == 422  

def test_submit_feedback_short_description():
    feedback_data = {
        "email": "test@example.com",
        "category": "bug",
        "description": "Short"
    }
    response = client.post("/feedback", json=feedback_data)
    assert response.status_code == 422

def test_get_feedback():
    test_submit_feedback_success()  # Ensure there is at least one feedback entry
    response = client.get("/feedback")
    assert response.status_code == 200
    assert len(response.json()) > 0  
