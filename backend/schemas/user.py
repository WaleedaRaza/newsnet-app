from pydantic import BaseModel, EmailStr
from typing import List, Dict, Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    interests: List[str] = []
    belief_fingerprint: Dict[str, List[str]] = {}
    bias_setting: float = 0.5

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    interests: Optional[List[str]] = None
    belief_fingerprint: Optional[Dict[str, List[str]]] = None
    bias_setting: Optional[float] = None

class User(UserBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User

class BeliefUpdate(BaseModel):
    topic: str
    beliefs: List[str] 