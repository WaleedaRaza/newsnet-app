from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import time

from db.session import get_db
from db.models import User
from schemas.article import ArticleAggregationRequest, ArticleAggregationResponse
from api.routes.auth import get_current_user
from services.article_aggregator import ArticleAggregator
from services.article_retrieval_service import ArticleRetrievalService
from schemas.article import ArticleCreate, ArticleResponse
from db.models import Article as ArticleModel

router = APIRouter()

# Create service instance
article_service = ArticleRetrievalService()

def extract_domain_from_url(url: str) -> str:
    """Extract domain from URL"""
    if not url:
        return "unknown"
    
    # Remove protocol
    if url.startswith(('http://', 'https://')):
        url = url.split('://', 1)[1]
    
    # Remove path and get domain
    domain = url.split('/')[0]
    
    # Remove www. prefix
    if domain.startswith('www.'):
        domain = domain[4:]
    
    return domain

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
    """Aggregate articles based on categories and bias settings"""
    
    start_time = time.time()
    
    try:
        # Initialize aggregator
        aggregator = ArticleAggregator()
        
        # Aggregate articles by category
        articles = await aggregator.aggregate_articles_by_category(
            categories=request.categories,
            bias_slider=request.bias,
            limit_per_category=request.limit_per_category,
            db=db
        )
        
        # Calculate aggregation time
        aggregation_time = time.time() - start_time
        
        return ArticleAggregationResponse(
            articles=articles,
            total_articles=len(articles),
            categories_covered=request.categories,
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
        
        # Aggregate articles by category
        articles = await aggregator.aggregate_articles_by_category(
            categories=request.categories,
            bias_slider=request.bias,
            limit_per_category=request.limit_per_category,
            db=db
        )
        
        # Calculate aggregation time
        aggregation_time = time.time() - start_time
        
        return ArticleAggregationResponse(
            articles=articles,
            total_articles=len(articles),
            categories_covered=request.categories,
            aggregation_time=aggregation_time
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to aggregate articles: {str(e)}"
        )

@router.get("/", response_model=List[dict])
async def get_articles(
    categories: List[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get articles from database (for testing/debugging)"""
    try:
        from db.models import Article
        
        query = db.query(Article)
        
        if categories:
            # Filter by categories (simplified - in production use proper JSON querying)
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
    """Test endpoint that returns mock articles by category"""
    mock_articles = [
        {
            "id": "1",
            "title": "Israel-Palestine Conflict: Latest Developments",
            "content": "Recent developments in the ongoing conflict between Israel and Palestine, including diplomatic efforts and humanitarian concerns.",
            "url": "https://example.com/article1",
            "source_name": "International News",
            "source_domain": "example.com",
            "source_bias": "Center",
            "source_reliability": 0.8,
            "topics": ["geopolitics"],
            "published_at": "2024-01-15T10:00:00Z",
            "topical_score": 0.9,
            "belief_alignment_score": 0.5,
            "ideological_score": 0.5,
            "final_score": 0.8,
            "created_at": "2024-01-15T10:00:00Z"
        },
        {
            "id": "2", 
            "title": "Federal Reserve Considers Interest Rate Changes",
            "content": "The Federal Reserve is considering changes to interest rates amid economic uncertainty and inflation concerns.",
            "url": "https://example.com/article2",
            "source_name": "Financial Times",
            "source_domain": "example.com",
            "source_bias": "Center",
            "source_reliability": 0.9,
            "topics": ["economics"],
            "published_at": "2024-01-15T11:00:00Z",
            "topical_score": 0.85,
            "belief_alignment_score": 0.5,
            "ideological_score": 0.5,
            "final_score": 0.75,
            "created_at": "2024-01-15T11:00:00Z"
        },
        {
            "id": "3",
            "title": "New AI Breakthrough in Machine Learning",
            "content": "Researchers have made a significant breakthrough in machine learning technology that could revolutionize AI applications.",
            "url": "https://example.com/article3",
            "source_name": "Tech News",
            "source_domain": "example.com",
            "source_bias": "Center",
            "source_reliability": 0.7,
            "topics": ["tech_science"],
            "published_at": "2024-01-15T12:00:00Z",
            "topical_score": 0.9,
            "belief_alignment_score": 0.5,
            "ideological_score": 0.5,
            "final_score": 0.8,
            "created_at": "2024-01-15T12:00:00Z"
        }
    ]
    
    return {
        "articles": mock_articles,
        "total_articles": len(mock_articles),
        "categories_covered": ["geopolitics", "economics", "tech_science"],
        "aggregation_time": 0.1
    }

@router.get("/search")
async def search_articles(
    q: str,
    bias: float = Query(0.5, ge=0.0, le=1.0, description="Bias preference (0.0=liberal, 1.0=conservative)"),
    limit: int = Query(20, ge=1, le=50, description="Number of articles to return")
):
    """Search articles with intelligent bias analysis"""
    try:
        articles = await article_service.search_articles(query=q, bias=bias, limit=limit)
        
        # Format response
        formatted_articles = []
        for article in articles:
            formatted_article = {
                "title": article.get("title"),
                "description": article.get("description"),
                "url": article.get("url"),
                "urlToImage": article.get("urlToImage"),
                "publishedAt": article.get("publishedAt"),
                "source": {
                    "name": article.get("source", {}).get("name"),
                    "domain": extract_domain_from_url(article.get("url", ""))
                },
                "bias_analysis": article.get("bias_analysis", {})
            }
            formatted_articles.append(formatted_article)
        
        return {
            "status": "success",
            "total_results": len(formatted_articles),
            "query": q,
            "bias_preference": bias,
            "articles": formatted_articles
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching articles: {str(e)}")

def _filter_articles_by_bias(articles: List[dict], bias: float, limit: int) -> List[dict]:
    """Filter and sort articles based on bias preference"""
    if not articles:
        return []
    
    # Sort articles by how well they match the bias preference
    # bias = 0.0 means show more challenging/opposing views (left side)
    # bias = 1.0 means show more supporting views (right side)
    
    def bias_score(article):
        article_bias = article.get("bias_score", 0.5)
        
        # Calculate how well this article matches the user's bias preference
        # If user wants supporting views (bias = 1.0), prefer high bias_score articles
        # If user wants challenging views (bias = 0.0), prefer low bias_score articles
        bias_match = 1.0 - abs(article_bias - bias)
        
        # Also consider reliability
        reliability = article.get("source_reliability", 0.5)
        
        # Combined score: bias match (70%) + reliability (30%)
        return (bias_match * 0.7) + (reliability * 0.3)
    
    # Sort by bias score (highest first)
    sorted_articles = sorted(articles, key=bias_score, reverse=True)
    
    # Return top articles
    return sorted_articles[:limit] 