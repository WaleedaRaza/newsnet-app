from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ContradictionBase(BaseModel):
    description: str
    sources: List[str] = []
    resolution: str = ""
    severity: float = 0.5

class Contradiction(ContradictionBase):
    id: str
    
    class Config:
        from_attributes = True

class EntityBase(BaseModel):
    name: str
    type: str
    confidence: float = 1.0
    mentions: List[str] = []

class Entity(EntityBase):
    id: str
    
    class Config:
        from_attributes = True

class FusionResultBase(BaseModel):
    fused_narrative: str
    modulated_narrative: str
    bias_level: float
    contradictions: List[Contradiction] = []
    entities: List[Entity] = []
    confidence: float = 1.0

class FusionResultCreate(FusionResultBase):
    story_id: str

class FusionResult(FusionResultBase):
    id: str
    story_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ChatMessageBase(BaseModel):
    content: str
    is_user: bool = True
    source_context: Optional[str] = None

class ChatMessageCreate(ChatMessageBase):
    story_id: str

class ChatMessage(ChatMessageBase):
    id: str
    story_id: str
    timestamp: datetime
    
    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    message: str
    bias: float 