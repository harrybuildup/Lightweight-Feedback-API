import pytest
import sqlite3
from fastapi.testclient import TestClient
from main import app, DB_PATH

client = TestClient(app)

def clear_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM feedback")
    conn.commit()
    conn.close()

def test_submit_feedback_success():
    clear_db()
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
    clear_db()
    response = client.get("/api/feedback")
    assert response.status_code == 404

def test_get_feedback_stats():
    clear_db()
    # Add some test feedback
    feedback_data = {
        "email": "test@example.com",
        "category": "bug",
        "description": "This is a test feedback entry.",
        "rating": 4
    }
    client.post("/api/feedback", json=feedback_data)
    
    response = client.get("/api/feedback/stats")
    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["average_rating"] == 4.0

def test_delete_feedback():
    clear_db()
    # Add feedback
    feedback_data = {
        "email": "test@example.com",
        "category": "bug",
        "description": "This is a test feedback entry.",
        "rating": 3
    }
    post_response = client.post("/api/feedback", json=feedback_data)
    feedback_id = post_response.json()["feedback"]["id"]
    
    # Delete it
    delete_response = client.delete(f"/api/feedback/{feedback_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Feedback deleted successfully"