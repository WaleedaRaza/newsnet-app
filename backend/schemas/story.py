from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TimelineChunkBase(BaseModel):
    timestamp: datetime
    content: str
    sources: List[str] = []
    confidence: float = 1.0
    has_contradictions: bool = False
    contradictions: List[str] = []

class TimelineChunk(TimelineChunkBase):
    id: str
    
    class Config:
        from_attributes = True

class StoryBase(BaseModel):
    event_key: str
    title: str
    summary_neutral: str
    summary_modulated: str
    sources: List[str] = []
    topics: List[str] = []
    confidence: float = 1.0

class StoryCreate(StoryBase):
    pass

class Story(StoryBase):
    id: str
    embedding_id: Optional[str] = None
    published_at: datetime
    updated_at: Optional[datetime] = None
    timeline_chunks: List[TimelineChunk] = []
    
    class Config:
        from_attributes = True

class StoryList(BaseModel):
    stories: List[Story]
    total: int
    page: int
    limit: int

class SearchQuery(BaseModel):
    q: str

class SearchResult(BaseModel):
    stories: List[Story]
    total: int 