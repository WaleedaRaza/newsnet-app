from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    interests = Column(JSON, default=list)
    belief_fingerprint = Column(JSON, default=dict)
    bias_setting = Column(Float, default=0.5)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    stories = relationship("Story", back_populates="user")
    chat_messages = relationship("ChatMessage", back_populates="user")
    beliefs = relationship("UserBelief", back_populates="user")

class Story(Base):
    __tablename__ = "stories"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    event_key = Column(String, index=True, nullable=False)
    title = Column(String, nullable=False)
    summary_neutral = Column(Text, nullable=False)
    summary_modulated = Column(Text, nullable=False)
    sources = Column(JSON, default=list)
    topics = Column(JSON, default=list)
    confidence = Column(Float, default=1.0)
    embedding_id = Column(String, nullable=True)
    published_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="stories")
    timeline_chunks = relationship("TimelineChunk", back_populates="story")
    fusion_results = relationship("FusionResult", back_populates="story")
    chat_messages = relationship("ChatMessage", back_populates="story")

class TimelineChunk(Base):
    __tablename__ = "timeline_chunks"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    story_id = Column(String, ForeignKey("stories.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    content = Column(Text, nullable=False)
    sources = Column(JSON, default=list)
    confidence = Column(Float, default=1.0)
    has_contradictions = Column(Boolean, default=False)
    contradictions = Column(JSON, default=list)
    
    # Relationships
    story = relationship("Story", back_populates="timeline_chunks")

class FusionResult(Base):
    __tablename__ = "fusion_results"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    story_id = Column(String, ForeignKey("stories.id"), nullable=False)
    fused_narrative = Column(Text, nullable=False)
    modulated_narrative = Column(Text, nullable=False)
    bias_level = Column(Float, nullable=False)
    contradictions = Column(JSON, default=list)
    entities = Column(JSON, default=list)
    confidence = Column(Float, default=1.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    story = relationship("Story", back_populates="fusion_results")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    story_id = Column(String, ForeignKey("stories.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    content = Column(Text, nullable=False)
    is_user = Column(Boolean, default=True)
    source_context = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    story = relationship("Story", back_populates="chat_messages")
    user = relationship("User", back_populates="chat_messages")

class Source(Base):
    __tablename__ = "sources"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    icon = Column(String, nullable=True)
    reliability = Column(Float, default=0.5)
    bias = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Article(Base):
    __tablename__ = "articles"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    url = Column(String, nullable=False)
    source_name = Column(String, nullable=False)
    source_domain = Column(String, nullable=False)
    source_bias = Column(String, nullable=True)  # "Left", "Center", "Right"
    source_reliability = Column(Float, default=0.5)
    topics = Column(JSON, default=list)
    published_at = Column(DateTime(timezone=True), nullable=False)
    embedding_id = Column(String, nullable=True)
    
    # Scoring fields
    topical_score = Column(Float, default=0.0)
    belief_alignment_score = Column(Float, default=0.0)
    ideological_score = Column(Float, default=0.0)
    final_score = Column(Float, default=0.0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UserBelief(Base):
    __tablename__ = "user_beliefs"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    topic = Column(String, nullable=False)
    belief_text = Column(Text, nullable=False)
    stance_value = Column(Float, nullable=False)  # 1-10 scale
    confidence_level = Column(Float, default=0.5)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="beliefs") 