from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, EmailStr
from typing import Literal, List
import uuid
import datetime as dt
# then:

 
app = FastAPI()
 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
 
# Serve files from the static/ folder at /static URL
app.mount("/static", StaticFiles(directory="static"), name="static")
 
 
class Feedback(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    email: EmailStr
    category: Literal['bug', 'feature', 'general'] = 'general'
    description: str = Field(min_length=10)
    rating: int = Field(ge=1, le=5)
    created_at: dt.datetime = Field(default_factory=dt.datetime.utcnow)
 
 
feedback_db = []
 
 
@app.get("/")
def serve_frontend():
    return FileResponse("static/index.html")
 
@app.get("/admin")
def serve_admin():
    return FileResponse("static/admin.html")
 
@app.get("/health")
def health_check():
    return {"status": "API is running"}
 
 
@app.get("/feedback", response_model=List[Feedback])
def get_feedback():
    if not feedback_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No feedback entries found"
        )
    return feedback_db
 
 
@app.post("/feedback", status_code=status.HTTP_201_CREATED)
def submit_feedback(feedback: Feedback):
    feedback_db.append(feedback)
    return {"message": "Feedback submitted successfully", "feedback": feedback}
 