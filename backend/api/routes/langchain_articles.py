"""
LangChain-powered Article Retrieval API Routes
Provides intelligent news search with LLM-powered analysis
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Optional
import logging
from pydantic import BaseModel

from ..dependencies import get_current_user
from ...services.langchain_news_engine import LangChainNewsEngine
from ...config import get_api_keys

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/langchain", tags=["langchain"])

class LangChainSearchRequest(BaseModel):
    query: str
    bias_preference: float = 0.5
    limit: int = 10
    include_analysis: bool = True

class LangChainSearchResponse(BaseModel):
    articles: List[Dict]
    analysis: Optional[Dict] = None
    search_metadata: Dict

@router.post("/search", response_model=LangChainSearchResponse)
async def langchain_search(
    request: LangChainSearchRequest,
    current_user = Depends(get_current_user)
):
    """
    Perform intelligent news search using LangChain-powered analysis
    """
    try:
        logger.info(f"LangChain search request: {request.query} with bias {request.bias_preference}")
        
        # Get API keys
        api_keys = get_api_keys()
        
        # Initialize LangChain news engine
        news_engine = LangChainNewsEngine(api_keys)
        
        # Perform intelligent search
        result = await news_engine.intelligent_search(
            query=request.query,
            bias_preference=request.bias_preference,
            limit=request.limit,
            include_analysis=request.include_analysis
        )
        
        # Prepare response
        response = LangChainSearchResponse(
            articles=result['articles'],
            analysis=result.get('analysis'),
            search_metadata={
                'query': request.query,
                'bias_preference': request.bias_preference,
                'total_articles': len(result['articles']),
                'sources_used': result.get('sources_used', []),
                'search_time': result.get('search_time', 0)
            }
        )
        
        logger.info(f"LangChain search completed: {len(result['articles'])} articles found")
        return response
        
    except Exception as e:
        logger.error(f"LangChain search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.post("/analyze", response_model=Dict)
async def analyze_articles(
    articles: List[Dict],
    current_user = Depends(get_current_user)
):
    """
    Analyze articles using LangChain-powered stance detection and narrative synthesis
    """
    try:
        logger.info(f"Analyzing {len(articles)} articles with LangChain")
        
        # Get API keys
        api_keys = get_api_keys()
        
        # Initialize LangChain news engine
        news_engine = LangChainNewsEngine(api_keys)
        
        # Perform analysis
        analysis = await news_engine.analyze_articles(articles)
        
        logger.info("LangChain analysis completed")
        return analysis
        
    except Exception as e:
        logger.error(f"LangChain analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/health")
async def langchain_health():
    """
    Check LangChain service health
    """
    try:
        # Get API keys
        api_keys = get_api_keys()
        
        # Initialize LangChain news engine
        news_engine = LangChainNewsEngine(api_keys)
        
        # Test basic functionality
        health_status = await news_engine.health_check()
        
        return {
            "status": "healthy",
            "langchain_available": health_status['langchain_available'],
            "tools_configured": health_status['tools_configured'],
            "api_keys_available": health_status['api_keys_available']
        }
        
    except Exception as e:
        logger.error(f"LangChain health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        } 