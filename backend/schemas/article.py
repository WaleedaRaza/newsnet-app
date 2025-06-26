from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ArticleBase(BaseModel):
    title: str
    content: str
    url: str
    source_name: str
    source_domain: str
    source_bias: Optional[str] = None
    source_reliability: float = 0.5
    topics: List[str] = []
    published_at: datetime

class Article(ArticleBase):
    id: str
    topical_score: float = 0.0
    belief_alignment_score: float = 0.0
    ideological_score: float = 0.0
    final_score: float = 0.0
    created_at: datetime
    
    class Config:
        from_attributes = True

class ArticleCreate(ArticleBase):
    pass

class ArticleResponse(BaseModel):
    title: str
    description: Optional[str] = None
    url: str
    urlToImage: Optional[str] = None
    publishedAt: Optional[str] = None
    source: dict
    bias_analysis: Optional[dict] = None

class ArticleAggregationRequest(BaseModel):
    categories: List[str]
    bias: float = 0.5
    limit_per_category: int = 10

class ArticleAggregationResponse(BaseModel):
    articles: List[Article]
    total_articles: int
    categories_covered: List[str]
    aggregation_time: float

class UserBeliefBase(BaseModel):
    topic: str
    belief_text: str
    stance_value: float  # 1-10 scale
    confidence_level: float = 0.5

class UserBelief(UserBeliefBase):
    id: str
    user_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserBeliefCreate(UserBeliefBase):
    pass 