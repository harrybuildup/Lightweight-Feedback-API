from fastapi import FastAPI
from pydantic import BaseModel, Field, EmailStr
from typing import Literal
import uuid


class Feedback(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    email: EmailStr
    category: Literal['bug', 'feature', 'general'] = 'general'
    description: str = Field(min_length=10)


feedback_db = []  # In-memory database for feedback entries


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/health")
def health_check():
    return {"status": "API is running"}

@app.get("/feedback")
def get_feedback():
    if not feedback_db:
        return {"message": "No feedback entries found"}
    return feedback_db

@app.post("/feedback")
def submit_feedback(feedback: Feedback):
    feedback_db.append(feedback)
    return {"message": "Feedback submitted successfully", "feedback": feedback}
