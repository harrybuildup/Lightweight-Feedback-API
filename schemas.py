from pydantic import BaseModel, Field, EmailStr
from typing import Literal, List, Optional
from datetime import datetime
import uuid


class Feedback(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    email: EmailStr
    category: Literal['bug', 'feature', 'general'] = 'general'
    description: str = Field(min_length=10)
    rating: int = Field(ge=1, le=5)
    created_at: datetime = Field(default_factory=datetime.utcnow)
 
class UserCreate(BaseModel):
    id: Optional[int] = None
    email: EmailStr
    password: str = Field(min_length=6)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
