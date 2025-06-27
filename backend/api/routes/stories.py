from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from db.session import get_db
from db.models import Story, TimelineChunk, ChatMessage
from schemas.story import Story as StorySchema, StoryList, SearchQuery, SearchResult
from schemas.fusion import ChatMessage as ChatMessageSchema, ChatRequest
from api.routes.auth import get_current_user
# from services.fusion_engine import FusionEngine  # Temporarily disabled due to LangChain dependency issues

router = APIRouter()

@router.get("/test-mock")
def get_mock_stories():
    """Test endpoint that returns mock stories without authentication"""
    mock_stories = [
        {
            "id": "1",
            "event_key": "ukraine_conflict_2024",
            "title": "Ukraine Conflict: Latest Developments",
            "summary_neutral": "Recent developments in the ongoing conflict between Ukraine and Russia, including diplomatic efforts and military updates.",
            "summary_modulated": "The situation in Ukraine continues to evolve with new diplomatic initiatives and military developments.",
            "sources": ["Reuters", "BBC", "CNN"],
            "timeline_chunks": [
                {
                    "id": "chunk_1",
                    "timestamp": "2024-01-15T10:00:00Z",
                    "content": "Recent developments in the ongoing conflict between Ukraine and Russia, including diplomatic efforts and military updates.",
                    "sources": ["Reuters", "BBC", "CNN"],
                    "confidence": 0.85,
                    "has_contradictions": False,
                    "contradictions": []
                }
            ],
            "topics": ["Ukraine", "Russia", "War", "Politics"],
            "confidence": 0.85,
            "embedding_id": None,
            "published_at": "2024-01-15T10:00:00Z",
            "updated_at": "2024-01-15T10:00:00Z",
            "user_id": None
        },
        {
            "id": "2",
            "event_key": "ai_breakthrough_2024",
            "title": "AI Breakthrough: New Language Model Released",
            "summary_neutral": "A major technology company has released a new advanced language model with improved capabilities.",
            "summary_modulated": "The latest AI breakthrough shows significant progress in natural language processing technology.",
            "sources": ["TechCrunch", "Wired", "MIT Technology Review"],
            "timeline_chunks": [
                {
                    "id": "chunk_2",
                    "timestamp": "2024-01-15T11:00:00Z",
                    "content": "A major technology company has released a new advanced language model with improved capabilities.",
                    "sources": ["TechCrunch", "Wired", "MIT Technology Review"],
                    "confidence": 0.92,
                    "has_contradictions": False,
                    "contradictions": []
                }
            ],
            "topics": ["AI", "Technology", "Machine Learning"],
            "confidence": 0.92,
            "embedding_id": None,
            "published_at": "2024-01-15T11:00:00Z",
            "updated_at": "2024-01-15T11:00:00Z",
            "user_id": None
        },
        {
            "id": "3",
            "event_key": "climate_summit_2024",
            "title": "Global Climate Summit: New Commitments Made",
            "summary_neutral": "World leaders gathered for the annual climate summit, announcing new commitments to reduce carbon emissions.",
            "summary_modulated": "The climate summit has resulted in promising new commitments from global leaders to address environmental challenges.",
            "sources": ["The Guardian", "Reuters", "AP"],
            "timeline_chunks": [
                {
                    "id": "chunk_3",
                    "timestamp": "2024-01-15T12:00:00Z",
                    "content": "World leaders gathered for the annual climate summit, announcing new commitments to reduce carbon emissions.",
                    "sources": ["The Guardian", "Reuters", "AP"],
                    "confidence": 0.88,
                    "has_contradictions": False,
                    "contradictions": []
                }
            ],
            "topics": ["Climate Change", "Environment", "Politics"],
            "confidence": 0.88,
            "embedding_id": None,
            "published_at": "2024-01-15T12:00:00Z",
            "updated_at": "2024-01-15T12:00:00Z",
            "user_id": None
        }
    ]
    
    return {
        "stories": mock_stories,
        "total": len(mock_stories),
        "page": 1,
        "limit": 20
    }

@router.get("/", response_model=StoryList)
def get_stories(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    topics: Optional[List[str]] = Query(None),
    bias: Optional[float] = Query(None, ge=0.0, le=1.0),
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    # Build query
    query = db.query(Story)
    
    # Filter by topics if provided
    if topics:
        query = query.filter(Story.topics.overlap(topics))
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * limit
    stories = query.offset(offset).limit(limit).all()
    
    # Convert to schema
    story_schemas = [StorySchema.from_orm(story) for story in stories]
    
    return StoryList(
        stories=story_schemas,
        total=total,
        page=page,
        limit=limit
    )

@router.get("/{story_id}", response_model=StorySchema)
def get_story(story_id: str, db: Session = Depends(get_db)):
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found"
        )
    
    return StorySchema.from_orm(story)

@router.get("/{story_id}/timeline", response_model=List[dict])
def get_timeline(story_id: str, db: Session = Depends(get_db)):
    # Verify story exists
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found"
        )
    
    # Get timeline chunks
    chunks = db.query(TimelineChunk).filter(
        TimelineChunk.story_id == story_id
    ).order_by(TimelineChunk.timestamp).all()
    
    return [
        {
            "id": chunk.id,
            "timestamp": chunk.timestamp,
            "content": chunk.content,
            "sources": chunk.sources,
            "confidence": chunk.confidence,
            "has_contradictions": chunk.has_contradictions,
            "contradictions": chunk.contradictions
        }
        for chunk in chunks
    ]

@router.get("/{story_id}/chat", response_model=List[ChatMessageSchema])
def get_chat_history(
    story_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    # Verify story exists
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found"
        )
    
    # Get chat messages
    messages = db.query(ChatMessage).filter(
        ChatMessage.story_id == story_id
    ).order_by(ChatMessage.timestamp.desc()).all()
    
    return [ChatMessageSchema.from_orm(msg) for msg in messages]

@router.post("/{story_id}/chat", response_model=dict)
async def send_message(
    story_id: str,
    chat_request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    # Verify story exists
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found"
        )
    
    # Save user message
    user_message = ChatMessage(
        story_id=story_id,
        user_id=current_user.id if current_user else None,
        content=chat_request.message,
        is_user=True
    )
    db.add(user_message)
    db.commit()
    
    # Generate AI response
    try:
        # fusion_engine = FusionEngine()  # Temporarily disabled
        # ai_response = await fusion_engine.generate_chat_response(
        #     story_id=story_id,
        #     user_message=chat_request.message,
        #     bias=chat_request.bias,
        #     db=db
        # )
        
        # Mock AI response for now
        ai_response = {
            "content": f"I understand you're asking about this story. This is a temporary response while the AI features are being updated. Your message was: {chat_request.message}",
            "source_context": "Mock response",
            "sources": []
        }
        
        # Save AI response
        ai_message = ChatMessage(
            story_id=story_id,
            content=ai_response["content"],
            is_user=False,
            source_context=ai_response.get("source_context")
        )
        db.add(ai_message)
        db.commit()
        
        return {
            "message": ChatMessageSchema.from_orm(ai_message),
            "sources": ai_response.get("sources", [])
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate response: {str(e)}"
        )

@router.get("/search", response_model=SearchResult)
def search_stories(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db)
):
    # Simple text search - in production, use full-text search
    stories = db.query(Story).filter(
        Story.title.ilike(f"%{q}%") | 
        Story.summary_neutral.ilike(f"%{q}%") |
        Story.summary_modulated.ilike(f"%{q}%")
    ).limit(50).all()
    
    story_schemas = [StorySchema.from_orm(story) for story in stories]
    
    return SearchResult(
        stories=story_schemas,
        total=len(story_schemas)
    ) 