from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import uvicorn
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import create_engine, Column, String, Text, DateTime, Float, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import uuid

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_newsnet.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    interests = Column(JSON, default=list)
    belief_fingerprint = Column(JSON, default=dict)
    bias_setting = Column(Float, default=0.5)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Story(Base):
    __tablename__ = "stories"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    event_key = Column(String, index=True, nullable=False)
    title = Column(String, nullable=False)
    summary_neutral = Column(Text, nullable=False)
    summary_modulated = Column(Text, nullable=False)
    sources = Column(JSON, default=list)
    topics = Column(JSON, default=list)
    confidence = Column(Float, default=1.0)
    published_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models
class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    interests: List[str] = []
    belief_fingerprint: dict = {}
    bias_setting: float = 0.5

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User

class StoryBase(BaseModel):
    event_key: str
    title: str
    summary_neutral: str
    summary_modulated: str
    sources: List[str] = []
    topics: List[str] = []
    confidence: float = 1.0

class Story(StoryBase):
    id: str
    published_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class StoryList(BaseModel):
    stories: List[Story]
    total: int
    page: int
    limit: int

# Security
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Auth functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

# App setup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Add some test data
    db = SessionLocal()
    try:
        # Check if we have any stories
        if db.query(Story).count() == 0:
            # Add sample stories
            sample_stories = [
                Story(
                    event_key="ai-breakthrough-2024",
                    title="Major AI Breakthrough in Medical Diagnosis",
                    summary_neutral="Researchers have developed a new AI system that can diagnose rare diseases with 95% accuracy, potentially revolutionizing healthcare.",
                    summary_modulated="Researchers have developed a new AI system that can diagnose rare diseases with 95% accuracy, potentially revolutionizing healthcare.",
                    sources=["MIT News", "Nature", "TechCrunch"],
                    topics=["technology", "health", "ai"],
                    confidence=0.9
                ),
                Story(
                    event_key="climate-agreement-2024",
                    title="Global Climate Agreement Reached at COP29",
                    summary_neutral="World leaders have agreed on ambitious new climate targets at the COP29 summit, with commitments to reduce emissions by 50% by 2030.",
                    summary_modulated="World leaders have agreed on ambitious new climate targets at the COP29 summit, with commitments to reduce emissions by 50% by 2030.",
                    sources=["BBC News", "Reuters", "CNN"],
                    topics=["environment", "politics", "international"],
                    confidence=0.85
                ),
                Story(
                    event_key="space-exploration-2024",
                    title="NASA Announces Mars Mission Success",
                    summary_neutral="NASA's latest Mars rover has successfully completed its primary mission, discovering evidence of ancient water on the red planet.",
                    summary_modulated="NASA's latest Mars rover has successfully completed its primary mission, discovering evidence of ancient water on the red planet.",
                    sources=["NASA", "Space.com", "Scientific American"],
                    topics=["science", "space", "technology"],
                    confidence=0.95
                )
            ]
            db.add_all(sample_stories)
            db.commit()
    finally:
        db.close()
    
    print("Starting NewsNet Test API...")
    yield
    print("Shutting down NewsNet Test API...")

app = FastAPI(
    title="NewsNet Test API",
    description="Test version of NewsNet API for development",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
@app.get("/")
async def root():
    return {
        "message": "Welcome to NewsNet Test API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/v1/auth/register", response_model=Token)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        name=user_data.name,
        hashed_password=hashed_password,
        interests=user_data.interests,
        belief_fingerprint=user_data.belief_fingerprint,
        bias_setting=user_data.bias_setting
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.id}, expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        user=User.from_orm(db_user)
    )

@app.post("/v1/auth/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    # Find user by email
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        user=User.from_orm(user)
    )

@app.get("/v1/users/profile", response_model=User)
def get_user_profile(current_user: User = Depends(get_current_user)):
    return User.from_orm(current_user)

@app.get("/v1/stories", response_model=StoryList)
def get_stories(
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    # Get stories with pagination
    offset = (page - 1) * limit
    stories = db.query(Story).offset(offset).limit(limit).all()
    total = db.query(Story).count()
    
    return StoryList(
        stories=[Story.from_orm(story) for story in stories],
        total=total,
        page=page,
        limit=limit
    )

@app.get("/v1/stories/{story_id}", response_model=Story)
def get_story(story_id: str, db: Session = Depends(get_db)):
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found"
        )
    
    return Story.from_orm(story)

if __name__ == "__main__":
    uvicorn.run(
        "test_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 