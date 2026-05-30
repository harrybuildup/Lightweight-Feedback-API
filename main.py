from fastapi import FastAPI, HTTPException, status, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, EmailStr
from typing import Literal, List, Optional
import uuid
import datetime as dt
import sqlite3
import json
from pathlib import Path
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve files from the static/ folder at /static URL
app.mount("/static", StaticFiles(directory="static"), name="static")

# Database setup
DB_PATH = "feedback.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id TEXT PRIMARY KEY,
            email TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            rating INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# For backward compatibility with tests
feedback_db = []

class Feedback(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    email: EmailStr
    category: Literal['bug', 'feature', 'general'] = 'general'
    description: str = Field(min_length=10)
    rating: int = Field(ge=1, le=5)
    created_at: dt.datetime = Field(default_factory=dt.datetime.utcnow)
 
 
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
 