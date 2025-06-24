from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import time

from db.session import get_db
from db.models import User
from schemas.article import ArticleAggregationRequest, ArticleAggregationResponse
from api.routes.auth import get_current_user
from services.article_aggregator import ArticleAggregator

router = APIRouter()

@router.get("/test")
async def test_articles_endpoint():
    """Test endpoint to verify articles service is working"""
    return {
        "message": "Articles service is working!",
        "timestamp": time.time(),
        "status": "ok"
    }

@router.post("/aggregate", response_model=ArticleAggregationResponse)
async def aggregate_articles(
    request: ArticleAggregationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Aggregate articles based on user preferences and bias settings"""
    
    start_time = time.time()
    
    try:
        # Initialize aggregator
        aggregator = ArticleAggregator()
        
        # Aggregate articles
        articles = await aggregator.aggregate_articles(
            topics=request.topics,
            beliefs=request.beliefs,
            bias_slider=request.bias,
            limit_per_topic=request.limit_per_topic,
            db=db
        )
        
        # Calculate aggregation time
        aggregation_time = time.time() - start_time
        
        return ArticleAggregationResponse(
            articles=articles,
            total_articles=len(articles),
            topics_covered=request.topics,
            aggregation_time=aggregation_time
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to aggregate articles: {str(e)}"
        )

@router.post("/aggregate-public", response_model=ArticleAggregationResponse)
async def aggregate_articles_public(
    request: ArticleAggregationRequest,
    db: Session = Depends(get_db)
):
    """Public endpoint for article aggregation (no auth required)"""
    
    start_time = time.time()
    
    try:
        # Initialize aggregator
        aggregator = ArticleAggregator()
        
        # Aggregate articles
        articles = await aggregator.aggregate_articles(
            topics=request.topics,
            beliefs=request.beliefs,
            bias_slider=request.bias,
            limit_per_topic=request.limit_per_topic,
            db=db
        )
        
        # Calculate aggregation time
        aggregation_time = time.time() - start_time
        
        return ArticleAggregationResponse(
            articles=articles,
            total_articles=len(articles),
            topics_covered=request.topics,
            aggregation_time=aggregation_time
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to aggregate articles: {str(e)}"
        )

@router.get("/", response_model=List[dict])
async def get_articles(
    topics: List[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get articles from database (for testing/debugging)"""
    try:
        from db.models import Article
        
        query = db.query(Article)
        
        if topics:
            # Filter by topics (simplified - in production use proper JSON querying)
            query = query.limit(limit)
        
        articles = query.limit(limit).all()
        
        return [
            {
                "id": article.id,
                "title": article.title,
                "source_name": article.source_name,
                "topics": article.topics,
                "final_score": article.final_score,
                "published_at": article.published_at.isoformat() if article.published_at else None
            }
            for article in articles
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get articles: {str(e)}"
        )

@router.get("/test-mock")
async def test_mock_articles():
    """Test endpoint that returns mock articles"""
    mock_articles = [
        {
            "id": "1",
            "title": "Sample Political Article 1",
            "content": "This is a sample political article content for testing purposes.",
            "url": "https://example.com/article1",
            "source_name": "Sample News",
            "source_domain": "example.com",
            "source_bias": "Center",
            "source_reliability": 0.8,
            "topics": ["US Politics"],
            "published_at": "2024-01-15T10:00:00Z",
            "topical_score": 0.9,
            "belief_alignment_score": 0.7,
            "ideological_score": 0.6,
            "final_score": 0.8,
            "created_at": "2024-01-15T10:00:00Z"
        },
        {
            "id": "2", 
            "title": "Sample Political Article 2",
            "content": "Another sample political article for testing the frontend integration.",
            "url": "https://example.com/article2",
            "source_name": "Test News",
            "source_domain": "test.com",
            "source_bias": "Left",
            "source_reliability": 0.7,
            "topics": ["US Politics"],
            "published_at": "2024-01-15T11:00:00Z",
            "topical_score": 0.8,
            "belief_alignment_score": 0.6,
            "ideological_score": 0.5,
            "final_score": 0.7,
            "created_at": "2024-01-15T11:00:00Z"
        }
    ]
    
    return {
        "articles": mock_articles,
        "total_articles": len(mock_articles),
        "topics_covered": ["US Politics"],
        "aggregation_time": 0.1
    } 