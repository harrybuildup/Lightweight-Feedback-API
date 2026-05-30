from fastapi import FastAPI, HTTPException, status, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from schemas import *
from typing import List, Optional
from tables import init_db, DB_PATH
from oauth2 import hash_password, verify_password, create_access_token, get_current_user
import uuid
import sqlite3
import json
import os
import datetime as dt

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve files from the static/ folder at /static URL
app.mount("/static", StaticFiles(directory="static"), name="static")


# For backward compatibility with tests
feedback_db = []

init_db()

@app.get("/")
def serve_home():
    return FileResponse("static/home.html")

@app.get("/feedback")
def serve_feedback():
    return FileResponse("static/index.html")

@app.get("/admin")
def serve_admin():
    return FileResponse("static/dashboard.html")

@app.get("/health")
def health_check():
    return {"status": "API is running"}


@app.post("/api/register", status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if user already exists
    cursor.execute("SELECT * FROM users WHERE email = ?", (user.email,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password and insert user
    hashed_password = hash_password(user.password)
    cursor.execute(
        "INSERT INTO users (email, password, created_at) VALUES (?, ?, ?)",
        (user.email, hashed_password, user.created_at.isoformat())
    )
    conn.commit()
    conn.close()
    
    return {"message": "User registered successfully", "email": user.email}

@app.post("/api/login", response_model=Token)
def login_user(user: UserLogin):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (user.email,))
    db_user = cursor.fetchone()
    conn.close()
    
    if not db_user or not verify_password(user.password, db_user[2]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create JWT token
    access_token = create_access_token(data={"sub": db_user[1]})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/me")
def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return {"email": current_user["email"], "created_at": current_user["created_at"]}

@app.get("/api/feedback", response_model=List[Feedback])
def get_feedback(category: Optional[str] = None, skip: int = 0, limit: int = 100):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if category:
        cursor.execute(
            "SELECT * FROM feedback WHERE category = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (category, limit, skip)
        )
    else:
        cursor.execute(
            "SELECT * FROM feedback ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, skip)
        )
    
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No feedback entries found"
        )
    
    return [
        Feedback(
            id=uuid.UUID(row["id"]),
            email=row["email"],
            category=row["category"],
            description=row["description"],
            rating=row["rating"],
            created_at=dt.datetime.fromisoformat(row["created_at"])
        )
        for row in rows
    ]


@app.get("/api/feedback/stats")
def get_feedback_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Total feedback
    cursor.execute("SELECT COUNT(*) FROM feedback")
    total = cursor.fetchone()[0]
    
    # Average rating
    cursor.execute("SELECT AVG(rating) FROM feedback")
    avg_rating = cursor.fetchone()[0] or 0
    
    # Category breakdown
    cursor.execute("SELECT category, COUNT(*) FROM feedback GROUP BY category")
    categories = dict(cursor.fetchall())
    
    conn.close()
    
    return {
        "total": total,
        "average_rating": round(avg_rating, 2),
        "by_category": categories
    }


@app.post("/api/feedback", status_code=status.HTTP_201_CREATED)
def submit_feedback(feedback: Feedback):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO feedback (id, email, category, description, rating, created_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (
            str(feedback.id),
            feedback.email,
            feedback.category,
            feedback.description,
            feedback.rating,
            feedback.created_at.isoformat()
        )
    )
    conn.commit()
    conn.close()
    
    return {"message": "Feedback submitted successfully", "feedback": feedback}


@app.delete("/api/feedback/{feedback_id}")
def delete_feedback(feedback_id: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM feedback WHERE id = ?", (feedback_id,))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    
    if affected == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )
    
    return {"message": "Feedback deleted successfully"}
 