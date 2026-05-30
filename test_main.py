import pytest
from fastapi.testclient import TestClient
from main import app, feedback_db

client = TestClient(app)

def test_submit_feedback_success():
    feedback_db.clear()
    feedback_data = {
        "email": "test@example.com",
        "category": "bug",
        "description": "This is a test feedback entry.",
        "rating": 3
    }
    response = client.post("/api/feedback", json=feedback_data)
    assert response.status_code == 201
    assert response.json()["message"] == "Feedback submitted successfully"

def test_submit_feedback_invalid_email():
    feedback_data = {
        "email": "invalid-email",
        "category": "feature",
        "description": "This is a test feedback entry with invalid email.",
        "rating": 3
    }
    response = client.post("/api/feedback", json=feedback_data)
    assert response.status_code == 422  

def test_submit_feedback_invalid_category():
    feedback_data = {
        "email": "test@example.com",
        "category": "invalid category",
        "description": "This is a test feedback entry.",
        "rating": 3
    }
    response = client.post("/api/feedback", json=feedback_data)
    assert response.status_code == 422

def test_submit_feedback_short_description():
    feedback_data = {
        "email": "test@example.com",
        "category": "bug",
        "description": "Short",
        "rating": 3
    }
    response = client.post("/api/feedback", json=feedback_data)
    assert response.status_code == 422

def test_submit_feedback_invalid_rating():
    feedback_data = {
        "email": "test@example.com",
        "category": "bug",
        "description": "This is a test feedback entry.",
        "rating": 0
    }
    response = client.post("/api/feedback", json=feedback_data)
    assert response.status_code == 422

def test_get_feedback():
    test_submit_feedback_success()  # Ensure there is at least one feedback entry
    response = client.get("/api/feedback")
    assert response.status_code == 200
    assert len(response.json()) > 0  

def test_get_feedback_error():
    feedback_db.clear()
    response = client.get("/api/feedback")
    assert response.status_code == 404