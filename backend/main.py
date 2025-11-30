from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import uvicorn

from api.routes import auth, users, stories, articles, intelligence, langchain_articles
from db.session import engine
from db.models import Base
from config import settings
from services.multi_api_service import initialize_multi_api_service

# Create database tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting NewsNet API...")
    
    # Initialize multi-API service
    api_config = {
        'newsapi_key': settings.news_api_key,
        'gnews_key': settings.gnews_api_key,
        'mediastack_key': settings.mediastack_api_key,
        'webz_key': settings.webz_api_key,
        'newscatcher_key': settings.newscatcher_api_key,
        'worldnews_key': settings.worldnews_api_key,
        'guardian_key': settings.guardian_api_key,
        'nyt_key': settings.nyt_api_key,
        'aylien_key': settings.aylien_api_key,
        'contify_key': settings.contify_api_key,
    }
    
    # Remove None values
    api_config = {k: v for k, v in api_config.items() if v is not None}
    
    if api_config:
        initialize_multi_api_service(api_config)
        print(f"Initialized multi-API service with {len(api_config)} APIs")
    else:
        print("Warning: No API keys configured, using fallback mode")
    
    yield
    
    # Shutdown
    print("Shutting down NewsNet API...")

app = FastAPI(
    title="NewsNet API",
    description="AI-powered news analysis and narrative fusion API with multi-API architecture",
    version="2.0.0",
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
app.include_router(articles.router, prefix="/v1/articles", tags=["Articles"])
app.include_router(intelligence.router, tags=["Intelligence"])
app.include_router(langchain_articles.router, prefix="/v1", tags=["LangChain"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to NewsNet API v2.0",
        "version": "2.0.0",
        "docs": "/docs",
        "intelligence_endpoints": "/v1/intelligence",
        "features": [
            "Multi-API news aggregation",
            "Advanced bias detection",
            "Stance detection",
            "User belief fingerprinting",
            "Semantic search & Q&A"
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "2.0.0"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 