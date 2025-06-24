from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import uvicorn

from api.routes import auth, users, stories, fusion, articles
from db.session import engine
from db.models import Base
from config import settings

# Create database tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting NewsNet API...")
    yield
    # Shutdown
    print("Shutting down NewsNet API...")

app = FastAPI(
    title="NewsNet API",
    description="AI-powered news analysis and narrative fusion API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Include routers
app.include_router(auth.router, prefix="/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/v1/users", tags=["Users"])
app.include_router(stories.router, prefix="/v1/stories", tags=["Stories"])
app.include_router(fusion.router, prefix="/v1/fusion", tags=["Fusion"])
app.include_router(articles.router, prefix="/v1/articles", tags=["Articles"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to NewsNet API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 