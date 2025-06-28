from pydantic_settings import BaseSettings
from typing import Optional, List
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
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "your_openai_api_key_here")
    
    # News APIs - Single API with Smart Caching
    news_api_key: str = os.getenv("NEWS_API_KEY", "your_news_api_key_here")
    gnews_api_key: Optional[str] = None  # GNews API (backup)
    mediastack_api_key: Optional[str] = None  # Mediastack API (backup)
    webz_api_key: Optional[str] = None  # Webz.io API
    newscatcher_api_key: Optional[str] = None  # Newscatcher API
    worldnews_api_key: Optional[str] = None  # World News API
    guardian_api_key: Optional[str] = None  # The Guardian API
    nyt_api_key: Optional[str] = None  # NYT API
    aylien_api_key: Optional[str] = None  # Aylien News API
    contify_api_key: Optional[str] = None  # Contify API
    
    # Qdrant
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "newsnet_embeddings"
    
    # App
    app_name: str = "NewsNet"
    debug: bool = True
    
    # GDELT API (free, unlimited)
    gdelt_api_key: str = os.getenv("GDELT_API_KEY", "")  # Usually not needed for basic usage
    
    # CORS
    cors_origins: list = ["*"]
    
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

# News API Keys
if os.getenv("NEWS_API_KEY"):
    settings.news_api_key = os.getenv("NEWS_API_KEY")

if os.getenv("GNEWS_API_KEY"):
    settings.gnews_api_key = os.getenv("GNEWS_API_KEY")

if os.getenv("MEDIASTACK_API_KEY"):
    settings.mediastack_api_key = os.getenv("MEDIASTACK_API_KEY")

if os.getenv("WEBZ_API_KEY"):
    settings.webz_api_key = os.getenv("WEBZ_API_KEY")

if os.getenv("NEWSCATCHER_API_KEY"):
    settings.newscatcher_api_key = os.getenv("NEWSCATCHER_API_KEY")

if os.getenv("WORLDNEWS_API_KEY"):
    settings.worldnews_api_key = os.getenv("WORLDNEWS_API_KEY")

if os.getenv("GUARDIAN_API_KEY"):
    settings.guardian_api_key = os.getenv("GUARDIAN_API_KEY")

if os.getenv("NYT_API_KEY"):
    settings.nyt_api_key = os.getenv("NYT_API_KEY")

if os.getenv("AYLIEN_API_KEY"):
    settings.aylien_api_key = os.getenv("AYLIEN_API_KEY")

if os.getenv("CONTIFY_API_KEY"):
    settings.contify_api_key = os.getenv("CONTIFY_API_KEY") 