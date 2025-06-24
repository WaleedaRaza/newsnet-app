from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database - Using SQLite for easy testing
    database_url: str = "sqlite:///./newsnet.db"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # JWT
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # OpenAI
    openai_api_key: Optional[str] = None
    
    # News API
    news_api_key: Optional[str] = None
    
    # Qdrant
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "newsnet_embeddings"
    
    # App
    app_name: str = "NewsNet"
    debug: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()

# Load from environment variables
if os.getenv("DATABASE_URL"):
    settings.database_url = os.getenv("DATABASE_URL")

if os.getenv("REDIS_URL"):
    settings.redis_url = os.getenv("REDIS_URL")

if os.getenv("SECRET_KEY"):
    settings.secret_key = os.getenv("SECRET_KEY")

if os.getenv("OPENAI_API_KEY"):
    settings.openai_api_key = os.getenv("OPENAI_API_KEY")

if os.getenv("NEWS_API_KEY"):
    settings.news_api_key = os.getenv("NEWS_API_KEY") 