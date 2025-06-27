"""
Intelligence API Routes

FastAPI routes for backend intelligence services:
- Stance detection
- User belief fingerprinting  
- Semantic search & Q&A
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

# Import our intelligence services
from services.advanced_stance_detector import advanced_stance_detector
from services.user_belief_fingerprint import user_belief_fingerprint_service
from services.semantic_search_qa import semantic_search_qa_service

router = APIRouter(prefix="/v1/intelligence", tags=["intelligence"])

# Pydantic models for request/response
class StanceDetectionRequest(BaseModel):
    belief: str
    article_text: str
    method_preference: str = "auto"

class StanceDetectionResponse(BaseModel):
    belief: str
    article_text: str
    stance: str
    confidence: float
    method: str
    evidence: List[str]
    processing_time: float
    metadata: Dict[str, Any] = None

class BeliefStatement(BaseModel):
    text: str
    category: str
    strength: float = 0.5
    source: str = "user_input"
    metadata: Dict[str, Any] = None

class CreateFingerprintRequest(BaseModel):
    user_id: str
    beliefs: List[BeliefStatement]

class UpdateFingerprintRequest(BaseModel):
    user_id: str
    new_beliefs: List[BeliefStatement]

class ContentScoringRequest(BaseModel):
    user_id: str
    content_text: str
    content_metadata: Dict[str, Any] = None

class ContentScoringResponse(BaseModel):
    content_id: str
    content_type: str
    proximity_score: float
    stance_alignment: float
    overall_score: float
    evidence: List[str]
    metadata: Dict[str, Any] = None

class PersonalizedRecommendationsRequest(BaseModel):
    user_id: str
    content_list: List[Dict[str, Any]]
    limit: int = 10

class BeliefAnalysisResponse(BaseModel):
    user_id: str
    total_beliefs: int
    categories: List[str]
    category_distribution: Dict[str, int]
    category_strengths: Dict[str, float]
    belief_diversity: float
    last_updated: str
    recommendations: Dict[str, Any]

class SemanticSearchRequest(BaseModel):
    query: str
    max_results: int = 10
    similarity_threshold: float = 0.3

class SearchResult(BaseModel):
    article_id: str
    title: str
    content: str
    source: str
    similarity_score: float
    metadata: Dict[str, Any] = None

class QARequest(BaseModel):
    question: str
    max_sources: int = 5
    min_confidence: float = 0.5

class QAResponse(BaseModel):
    question: str
    answer: str
    confidence: float
    sources: List[SearchResult]
    evidence: List[str]
    metadata: Dict[str, Any] = None

class HealthCheckResponse(BaseModel):
    service: str
    status: str
    details: Dict[str, Any]
    timestamp: str

# Stance Detection Routes
@router.post("/stance/detect", response_model=StanceDetectionResponse)
async def detect_stance(request: StanceDetectionRequest):
    """Detect stance of article toward a specific belief"""
    try:
        result = await advanced_stance_detector.detect_stance(
            belief=request.belief,
            article_text=request.article_text,
            method_preference=request.method_preference
        )
        
        return StanceDetectionResponse(
            belief=result.belief,
            article_text=result.article_text,
            stance=result.stance,
            confidence=result.confidence,
            method=result.method,
            evidence=result.evidence,
            processing_time=result.processing_time,
            metadata=result.metadata
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stance detection failed: {str(e)}")

@router.post("/stance/batch", response_model=List[StanceDetectionResponse])
async def batch_detect_stances(belief_article_pairs: List[Dict[str, str]]):
    """Detect stance for multiple belief-article pairs"""
    try:
        results = await advanced_stance_detector.batch_detect_stances(belief_article_pairs)
        
        return [
            StanceDetectionResponse(
                belief=result.belief,
                article_text=result.article_text,
                stance=result.stance,
                confidence=result.confidence,
                method=result.method,
                evidence=result.evidence,
                processing_time=result.processing_time,
                metadata=result.metadata
            )
            for result in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch stance detection failed: {str(e)}")

@router.get("/stance/metrics")
async def get_stance_metrics():
    """Get stance detection service metrics"""
    try:
        metrics = advanced_stance_detector.get_metrics()
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")

# User Belief Fingerprinting Routes
@router.post("/beliefs/create")
async def create_user_fingerprint(request: CreateFingerprintRequest):
    """Create a new user belief fingerprint"""
    try:
        # Convert Pydantic models to dictionaries
        beliefs_data = [
            {
                "text": belief.text,
                "category": belief.category,
                "strength": belief.strength,
                "source": belief.source,
                "metadata": belief.metadata or {}
            }
            for belief in request.beliefs
        ]
        
        fingerprint = await user_belief_fingerprint_service.create_user_fingerprint(
            user_id=request.user_id,
            beliefs=beliefs_data
        )
        
        return {
            "user_id": fingerprint.user_id,
            "beliefs_count": len(fingerprint.beliefs),
            "categories": fingerprint.categories,
            "last_updated": fingerprint.last_updated.isoformat(),
            "status": "created"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create fingerprint: {str(e)}")

@router.post("/beliefs/update")
async def update_user_fingerprint(request: UpdateFingerprintRequest):
    """Update an existing user belief fingerprint"""
    try:
        # Convert Pydantic models to dictionaries
        beliefs_data = [
            {
                "text": belief.text,
                "category": belief.category,
                "strength": belief.strength,
                "source": belief.source,
                "metadata": belief.metadata or {}
            }
            for belief in request.new_beliefs
        ]
        
        fingerprint = await user_belief_fingerprint_service.update_user_fingerprint(
            user_id=request.user_id,
            new_beliefs=beliefs_data
        )
        
        return {
            "user_id": fingerprint.user_id,
            "beliefs_count": len(fingerprint.beliefs),
            "categories": fingerprint.categories,
            "last_updated": fingerprint.last_updated.isoformat(),
            "status": "updated"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update fingerprint: {str(e)}")

@router.post("/beliefs/score", response_model=ContentScoringResponse)
async def score_content_for_user(request: ContentScoringRequest):
    """Score content based on user's belief fingerprint"""
    try:
        score = await user_belief_fingerprint_service.score_content_for_user(
            user_id=request.user_id,
            content_text=request.content_text,
            content_metadata=request.content_metadata
        )
        
        return ContentScoringResponse(
            content_id=score.content_id,
            content_type=score.content_type,
            proximity_score=score.proximity_score,
            stance_alignment=score.stance_alignment,
            overall_score=score.overall_score,
            evidence=score.evidence,
            metadata=score.metadata
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to score content: {str(e)}")

@router.post("/beliefs/recommendations")
async def get_personalized_recommendations(request: PersonalizedRecommendationsRequest):
    """Get personalized content recommendations for a user"""
    try:
        recommendations = await user_belief_fingerprint_service.get_personalized_recommendations(
            user_id=request.user_id,
            content_list=request.content_list,
            limit=request.limit
        )
        
        return {
            "user_id": request.user_id,
            "recommendations": [
                {
                    "content": content,
                    "score": {
                        "overall_score": score.overall_score,
                        "proximity_score": score.proximity_score,
                        "stance_alignment": score.stance_alignment,
                        "evidence": score.evidence
                    }
                }
                for content, score in recommendations
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")

@router.get("/beliefs/analyze/{user_id}", response_model=BeliefAnalysisResponse)
async def analyze_user_beliefs(user_id: str):
    """Analyze user beliefs and provide insights"""
    try:
        analysis = await user_belief_fingerprint_service.analyze_user_beliefs(user_id)
        return BeliefAnalysisResponse(**analysis)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze beliefs: {str(e)}")

@router.get("/beliefs/templates")
async def get_belief_templates(categories: Optional[str] = None):
    """Get belief templates for specified categories"""
    try:
        category_list = categories.split(",") if categories else None
        templates = await user_belief_fingerprint_service.get_belief_templates(category_list)
        return templates
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get templates: {str(e)}")

# Semantic Search & Q&A Routes
@router.post("/search/semantic")
async def semantic_search(request: SemanticSearchRequest):
    """Perform semantic search over articles"""
    try:
        results = await semantic_search_qa_service.semantic_search(
            query=request.query,
            max_results=request.max_results,
            similarity_threshold=request.similarity_threshold
        )
        
        return {
            "query": request.query,
            "results": [
                SearchResult(
                    article_id=result.article_id,
                    title=result.title,
                    content=result.content,
                    source=result.source,
                    similarity_score=result.similarity_score,
                    metadata=result.metadata
                )
                for result in results
            ],
            "total_results": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Semantic search failed: {str(e)}")

@router.post("/qa/answer", response_model=QAResponse)
async def answer_question(request: QARequest):
    """Answer a question using semantic search and content analysis"""
    try:
        answer_result = await semantic_search_qa_service.answer_question(
            question=request.question,
            max_sources=request.max_sources,
            min_confidence=request.min_confidence
        )
        
        return QAResponse(
            question=answer_result.question,
            answer=answer_result.answer,
            confidence=answer_result.confidence,
            sources=[
                SearchResult(
                    article_id=source.article_id,
                    title=source.title,
                    content=source.content,
                    source=source.source,
                    similarity_score=source.similarity_score,
                    metadata=source.metadata
                )
                for source in answer_result.sources
            ],
            evidence=answer_result.evidence,
            metadata=answer_result.metadata
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Question answering failed: {str(e)}")

@router.post("/search/index")
async def index_articles(articles: List[Dict[str, Any]]):
    """Add articles to the search index"""
    try:
        await semantic_search_qa_service.add_articles(articles)
        stats = await semantic_search_qa_service.get_search_statistics()
        
        return {
            "status": "success",
            "articles_added": len(articles),
            "total_articles": stats["total_articles"],
            "embeddings_available": stats["embeddings_available"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to index articles: {str(e)}")

@router.get("/search/statistics")
async def get_search_statistics():
    """Get statistics about the search index"""
    try:
        stats = await semantic_search_qa_service.get_search_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

# Health Check Routes
@router.get("/health", response_model=List[HealthCheckResponse])
async def health_check():
    """Health check for all intelligence services"""
    try:
        health_checks = []
        
        # Stance detection health
        stance_health = await advanced_stance_detector.health_check()
        health_checks.append(HealthCheckResponse(
            service="Stance Detection",
            status=stance_health.get("status", "unknown"),
            details=stance_health,
            timestamp=datetime.now().isoformat()
        ))
        
        # Belief fingerprinting health
        belief_health = await user_belief_fingerprint_service.health_check()
        health_checks.append(HealthCheckResponse(
            service="Belief Fingerprinting",
            status=belief_health.get("status", "unknown"),
            details=belief_health,
            timestamp=datetime.now().isoformat()
        ))
        
        # Semantic search health
        search_health = await semantic_search_qa_service.health_check()
        health_checks.append(HealthCheckResponse(
            service="Semantic Search & Q&A",
            status=search_health.get("status", "unknown"),
            details=search_health,
            timestamp=datetime.now().isoformat()
        ))
        
        return health_checks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}") 