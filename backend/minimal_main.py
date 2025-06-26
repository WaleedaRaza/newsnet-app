#!/usr/bin/env python3
"""
Minimal NewsNet Backend - Core search functionality without langchain dependencies
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional
import uvicorn
import time

from services.stance_detector import stance_detector
from services.article_retrieval_service import ArticleRetrievalService

# Initialize FastAPI app
app = FastAPI(
    title="NewsNet Minimal Backend",
    description="Core search functionality with stance detection",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
article_service = ArticleRetrievalService()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "NewsNet Minimal Backend is running!",
        "version": "1.0.0",
        "features": ["stance_detection", "article_search", "bias_analysis"]
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "services": {
            "stance_detector": "active",
            "article_service": "active"
        }
    }

@app.get("/v1/articles/search")
async def search_articles(
    q: str = Query(..., description="Search query"),
    bias: float = Query(0.5, ge=0.0, le=1.0, description="Bias preference (0.0=challenging, 1.0=supporting)"),
    limit: int = Query(20, ge=1, le=50, description="Number of articles to return")
):
    """Search articles with stance detection and bias analysis"""
    try:
        print(f"🔍 SEARCH: Query='{q}', bias={bias}, limit={limit}")
        
        # Use the updated article service with stance detection
        articles = await article_service.search_articles(
            query=q,
            bias=bias,
            limit=limit
        )
        
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
                    "domain": article.get("source", {}).get("domain")
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
        print(f"❌ SEARCH ERROR: {e}")
        raise HTTPException(status_code=500, detail=f"Error searching articles: {str(e)}")

@app.get("/v1/articles/test-stance")
async def test_stance_detection(
    text: str = Query(..., description="Article text to analyze"),
    belief: str = Query(..., description="User belief to test against")
):
    """Test stance detection directly"""
    try:
        stance_result = stance_detector.classify_stance(text, belief)
        return {
            "status": "success",
            "text": text,
            "belief": belief,
            "stance_analysis": stance_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in stance detection: {str(e)}")

@app.get("/v1/articles/mock")
async def get_mock_articles():
    """Get mock articles for testing (when News API is rate limited)"""
    mock_articles = [
        {
            "title": "Trump faces new legal challenges in multiple states",
            "description": "Former president confronts lawsuits and investigations as legal pressure mounts across the country.",
            "url": "https://example.com/trump-legal-challenges",
            "urlToImage": None,
            "publishedAt": "2024-01-15T10:00:00Z",
            "source": {"name": "Mock News", "domain": "example.com"},
            "bias_analysis": {
                "stance": "oppose",
                "stance_confidence": 0.8,
                "stance_method": "rule_based",
                "stance_evidence": ["challenges", "lawsuits", "investigations"],
                "bias_match": 0.8,
                "user_bias_preference": 0.0,
                "user_belief": "trump I hate him",
                "analysis_method": "stance_detection"
            }
        },
        {
            "title": "Trump defends economic record, highlights job creation",
            "description": "Former president emphasizes economic achievements and job growth during his administration.",
            "url": "https://example.com/trump-economy",
            "urlToImage": None,
            "publishedAt": "2024-01-15T11:00:00Z",
            "source": {"name": "Mock News", "domain": "example.com"},
            "bias_analysis": {
                "stance": "support",
                "stance_confidence": 0.7,
                "stance_method": "rule_based",
                "stance_evidence": ["defends", "achievements", "growth"],
                "bias_match": 0.7,
                "user_bias_preference": 1.0,
                "user_belief": "trump I love him",
                "analysis_method": "stance_detection"
            }
        },
        {
            "title": "NATO increases military support to Ukraine",
            "description": "Alliance approves additional weapons and training, marking significant escalation in Western involvement.",
            "url": "https://example.com/nato-ukraine",
            "urlToImage": None,
            "publishedAt": "2024-01-15T12:00:00Z",
            "source": {"name": "Mock News", "domain": "example.com"},
            "bias_analysis": {
                "stance": "support",
                "stance_confidence": 0.6,
                "stance_method": "rule_based",
                "stance_evidence": ["increases", "support"],
                "bias_match": 0.6,
                "user_bias_preference": 0.5,
                "user_belief": "NATO escalation",
                "analysis_method": "stance_detection"
            }
        }
    ]
    
    return {
        "status": "success",
        "total_results": len(mock_articles),
        "query": "mock_data",
        "bias_preference": 0.5,
        "articles": mock_articles
    }

if __name__ == "__main__":
    print("🚀 Starting NewsNet Minimal Backend...")
    print("📡 Endpoints:")
    print("  - GET / - Health check")
    print("  - GET /v1/articles/search - Search with stance detection")
    print("  - GET /v1/articles/test-stance - Test stance detection")
    print("  - GET /v1/articles/mock - Get mock articles")
    print()
    
    uvicorn.run(
        "minimal_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 