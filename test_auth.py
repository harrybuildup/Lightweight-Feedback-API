from fastapi.testclient import TestClient
from main import app
import sqlite3
from tables import DB_PATH

client = TestClient(app)

def clear_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users")
    conn.commit()
    conn.close()

clear_users()

# Test Registration
print("=== Testing Registration ===")
reg_response = client.post("/api/register", json={
    "email": "john@example.com",
    "password": "password123"
})
print(f"Status: {reg_response.status_code}")
print(f"Response: {reg_response.json()}\n")

# Test duplicate registration
print("=== Testing Duplicate Registration ===")
dup_response = client.post("/api/register", json={
    "email": "john@example.com",
    "password": "password456"
})
print(f"Status: {dup_response.status_code}")
print(f"Response: {dup_response.json()}\n")

# Test Login
print("=== Testing Login ===")
login_response = client.post("/api/login", json={
    "email": "john@example.com",
    "password": "password123"
})
print(f"Status: {login_response.status_code}")
login_data = login_response.json()
print(f"Has access_token: {'access_token' in login_data}")
print(f"Token type: {login_data.get('token_type')}")
token = login_data.get("access_token")
print(f"Token preview: {token[:20]}...\n")

# Test Get Current User
print("=== Testing Get Current User ===")
user_response = client.get("/api/me", headers={
    "Authorization": f"Bearer {token}"
})
print(f"Status: {user_response.status_code}")
print(f"User: {user_response.json()}\n")

# Test Invalid Login
print("=== Testing Invalid Login ===")
invalid_response = client.post("/api/login", json={
    "email": "john@example.com",
    "password": "wrongpassword"
})
print(f"Status: {invalid_response.status_code}")
print(f"Response: {invalid_response.json()}\n")

# Test Invalid Token
print("=== Testing Invalid Token ===")
invalid_token_response = client.get("/api/me", headers={
    "Authorization": "Bearer invalid_token_xyz"
})
print(f"Status: {invalid_token_response.status_code}")
print(f"Response: {invalid_token_response.json()}")
