import asyncio
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
import openai
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.embeddings import OpenAIEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from db.models import Story, TimelineChunk
from config import settings

class FusionEngine:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        self.chat_model = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.7,
            openai_api_key=settings.openai_api_key
        )
        self.embeddings = OpenAIEmbeddings(openai_api_key=settings.openai_api_key)
        self.qdrant_client = QdrantClient(settings.qdrant_url)
        
        # Initialize Qdrant collection if it doesn't exist
        try:
            self.qdrant_client.get_collection(settings.qdrant_collection)
        except:
            self.qdrant_client.create_collection(
                collection_name=settings.qdrant_collection,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
            )
    
    async def fuse_narrative(
        self,
        story_id: str,
        bias: float,
        db: Session
    ) -> Dict:
        """Fuse multiple sources into a coherent narrative with bias modulation."""
        
        # Get story and timeline data
        story = db.query(Story).filter(Story.id == story_id).first()
        if not story:
            raise ValueError("Story not found")
        
        timeline_chunks = db.query(TimelineChunk).filter(
            TimelineChunk.story_id == story_id
        ).order_by(TimelineChunk.timestamp).all()
        
        # Prepare context for fusion
        context = self._prepare_fusion_context(story, timeline_chunks)
        
        # Generate fused narrative
        fused_narrative = await self._generate_fused_narrative(context)
        
        # Apply bias modulation
        modulated_narrative = await self._apply_bias_modulation(
            fused_narrative, bias, context
        )
        
        # Extract contradictions and entities
        contradictions = await self._extract_contradictions(context)
        entities = await self._extract_entities(fused_narrative)
        
        # Calculate confidence
        confidence = self._calculate_confidence(story, timeline_chunks)
        
        return {
            "fused_narrative": fused_narrative,
            "modulated_narrative": modulated_narrative,
            "contradictions": contradictions,
            "entities": entities,
            "confidence": confidence
        }
    
    async def generate_chat_response(
        self,
        story_id: str,
        user_message: str,
        bias: float,
        db: Session
    ) -> Dict:
        """Generate a conversational response about a story."""
        
        # Get story and fusion data
        story = db.query(Story).filter(Story.id == story_id).first()
        if not story:
            raise ValueError("Story not found")
        
        # Get or generate fusion result
        fusion_data = await self.fuse_narrative(story_id, bias, db)
        
        # Prepare chat context
        context = f"""
        Story: {story.title}
        
        Fused Narrative: {fusion_data['fused_narrative']}
        
        Sources: {', '.join(story.sources)}
        
        User Question: {user_message}
        
        Bias Level: {bias} (0=challenge, 1=affirm)
        """
        
        # Generate response
        messages = [
            SystemMessage(content=self._get_chat_system_prompt(bias)),
            HumanMessage(content=context)
        ]
        
        response = await self.chat_model.agenerate([messages])
        ai_response = response.generations[0][0].text
        
        return {
            "content": ai_response,
            "source_context": f"Based on {len(story.sources)} sources",
            "sources": story.sources
        }
    
    def _prepare_fusion_context(self, story: Story, timeline_chunks: List[TimelineChunk]) -> str:
        """Prepare context for narrative fusion."""
        
        context_parts = [
            f"Story Title: {story.title}",
            f"Event Key: {story.event_key}",
            f"Sources: {', '.join(story.sources)}",
            f"Topics: {', '.join(story.topics)}",
            "\nTimeline:"
        ]
        
        for chunk in timeline_chunks:
            context_parts.append(
                f"- {chunk.timestamp.strftime('%Y-%m-%d %H:%M')}: {chunk.content}"
            )
            if chunk.has_contradictions:
                context_parts.append(f"  Contradictions: {', '.join(chunk.contradictions)}")
        
        return "\n".join(context_parts)
    
    async def _generate_fused_narrative(self, context: str) -> str:
        """Generate a fused narrative from multiple sources."""
        
        prompt = f"""
        Given the following news sources and timeline, create a coherent, factual narrative that synthesizes all the information.
        
        Focus on:
        1. Chronological accuracy
        2. Factual consistency
        3. Clear cause-and-effect relationships
        4. Neutral, objective tone
        
        Context:
        {context}
        
        Provide a comprehensive narrative that tells the complete story:
        """
        
        messages = [
            SystemMessage(content="You are an expert news analyst specializing in narrative synthesis."),
            HumanMessage(content=prompt)
        ]
        
        response = await self.chat_model.agenerate([messages])
        return response.generations[0][0].text
    
    async def _apply_bias_modulation(self, narrative: str, bias: float, context: str) -> str:
        """Apply bias modulation to the narrative."""
        
        bias_descriptions = {
            0.0: "challenge the reader's assumptions and present counter-arguments",
            0.25: "question the narrative and present alternative viewpoints",
            0.5: "maintain neutral, balanced perspective",
            0.75: "support the main narrative while acknowledging nuances",
            1.0: "affirm the reader's likely beliefs and emphasize supporting evidence"
        }
        
        bias_desc = bias_descriptions[min(bias_descriptions.keys(), key=lambda x: abs(x - bias))]
        
        prompt = f"""
        Rewrite the following narrative with a bias level of {bias} ({bias_desc}).
        
        Original Narrative:
        {narrative}
        
        Context:
        {context}
        
        Instructions:
        - Maintain factual accuracy
        - Adjust tone, emphasis, and framing based on bias level
        - If bias is low (0-0.25), challenge assumptions and present counter-arguments
        - If bias is high (0.75-1.0), emphasize supporting evidence and minimize counter-arguments
        - If bias is neutral (0.5), maintain balanced perspective
        
        Rewritten narrative:
        """
        
        messages = [
            SystemMessage(content="You are an expert in narrative framing and bias modulation."),
            HumanMessage(content=prompt)
        ]
        
        response = await self.chat_model.agenerate([messages])
        return response.generations[0][0].text
    
    async def _extract_contradictions(self, context: str) -> List[Dict]:
        """Extract contradictions from the sources."""
        
        prompt = f"""
        Analyze the following news sources and timeline for contradictions or conflicting information.
        
        Context:
        {context}
        
        Identify any contradictions and provide:
        1. Description of the contradiction
        2. Sources involved
        3. Possible resolution or explanation
        
        Format as JSON list of objects with keys: description, sources, resolution, severity
        """
        
        messages = [
            SystemMessage(content="You are an expert fact-checker and contradiction detector."),
            HumanMessage(content=prompt)
        ]
        
        response = await self.chat_model.agenerate([messages])
        # Parse JSON response and return contradictions
        # This is a simplified version - in production, add proper JSON parsing
        return []
    
    async def _extract_entities(self, narrative: str) -> List[Dict]:
        """Extract key entities from the narrative."""
        
        prompt = f"""
        Extract key entities (people, organizations, locations, events) from the following narrative.
        
        Narrative:
        {narrative}
        
        For each entity, provide:
        1. Name
        2. Type (person, organization, location, event)
        3. Confidence level (0-1)
        4. Mentions in the text
        
        Format as JSON list of objects with keys: name, type, confidence, mentions
        """
        
        messages = [
            SystemMessage(content="You are an expert in named entity recognition."),
            HumanMessage(content=prompt)
        ]
        
        response = await self.chat_model.agenerate([messages])
        # Parse JSON response and return entities
        # This is a simplified version - in production, add proper JSON parsing
        return []
    
    def _calculate_confidence(self, story: Story, timeline_chunks: List[TimelineChunk]) -> float:
        """Calculate confidence level based on source quality and consistency."""
        
        # Base confidence on number of sources
        source_confidence = min(len(story.sources) / 5.0, 1.0)
        
        # Adjust based on timeline consistency
        contradiction_penalty = sum(
            0.1 for chunk in timeline_chunks if chunk.has_contradictions
        )
        
        # Adjust based on source reliability (simplified)
        reliability_bonus = 0.1 if len(story.sources) >= 3 else 0.0
        
        confidence = source_confidence - contradiction_penalty + reliability_bonus
        return max(0.0, min(1.0, confidence))
    
    def _get_chat_system_prompt(self, bias: float) -> str:
        """Get system prompt for chat responses based on bias level."""
        
        if bias <= 0.25:
            return """You are a challenging news analyst who questions assumptions and presents alternative viewpoints. 
            Be skeptical, ask probing questions, and highlight potential biases or missing context."""
        elif bias <= 0.5:
            return """You are a balanced news analyst who presents multiple perspectives fairly. 
            Acknowledge different viewpoints and provide nuanced analysis."""
        else:
            return """You are a supportive news analyst who helps users understand the main narrative. 
            Emphasize key points and provide clear explanations while acknowledging complexity.""" 