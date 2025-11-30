"""
Simplified Debate RAG Engine
Uses existing working article retrieval + new debate-focused stance detection
"""

import asyncio
import json
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from dataclasses import dataclass

# LangChain imports
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

# Use existing working article retrieval
from .article_retrieval_service import ArticleRetrievalService

logger = logging.getLogger(__name__)

@dataclass
class DebateArticle:
    """Article with debate-focused analysis"""
    title: str
    content: str
    url: str
    source: str
    published_at: str
    stance: Optional[str] = None
    confidence: Optional[float] = None
    reasoning: Optional[str] = None
    debate_strength: Optional[float] = None
    killer_evidence: Optional[List[str]] = None
    bias_score: Optional[float] = None

@dataclass
class DebateResult:
    """Debate-focused stance detection result"""
    stance: str  # 'strong_support', 'support', 'weak_support', 'neutral', 'weak_oppose', 'oppose', 'strong_oppose'
    confidence: float
    reasoning: str
    debate_strength: float
    killer_evidence: List[str]

class DebateRAGEngine:
    """
    Simplified debate RAG engine using existing article retrieval
    """
    
    def __init__(self, openai_api_key: str):
        self.openai_api_key = openai_api_key
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.1,
            openai_api_key=openai_api_key
        )
        
        # Use existing working article retrieval
        self.article_retrieval = ArticleRetrievalService()
        
        # Initialize debate-focused chains
        self._initialize_chains()
        
        logger.info("Debate RAG Engine initialized")
    
    def _initialize_chains(self):
        """Initialize debate-focused LangChain chains"""
        
        # Debate-winning stance detection chain
        stance_template = """
        You are an expert debate coach and fact-checker. Analyze the stance of this article toward the user's belief, focusing on the strongest, most debate-winning arguments and evidence.

        USER BELIEF: "{belief}"
        USER POSITION: {user_position}
        ARTICLE TITLE: "{title}"
        ARTICLE CONTENT: "{content}"

        Steps:
        1. Identify the main claims and arguments in the article.
        2. Compare them to the user's belief.
        3. Extract the strongest, most debate-winning evidence, facts, or quotes ("killer evidence").
        4. Rate the "debate strength" of this article in challenging or supporting the user's view (0 = weak, 1 = destroys/defends the view).
        5. Give a detailed, step-by-step reasoning for your assessment.

        Return JSON:
        {{
            "stance": "strong_support|support|weak_support|neutral|weak_oppose|oppose|strong_oppose",
            "confidence": 0.0-1.0,
            "reasoning": "detailed debate-focused reasoning",
            "debate_strength": 0.0-1.0,
            "killer_evidence": ["killer fact or quote 1", "killer fact or quote 2"]
        }}
        """
        
        self.stance_chain = LLMChain(
            llm=self.llm,
            prompt=ChatPromptTemplate.from_template(stance_template)
        )
        
        # Query processing chain
        query_template = """
        Process this user query to extract structured information for debate analysis.
        
        QUERY: "{query}"
        
        Extract:
        1. Main topic
        2. User's belief/position
        3. User's emotional stance (positive/negative/neutral)
        4. Intent (inform, persuade, challenge, etc.)
        
        Return JSON:
        {{
            "topic": "main topic",
            "user_belief": "user's belief statement",
            "user_position": "positive|negative|neutral",
            "intent": "user's intent"
        }}
        """
        
        self.query_chain = LLMChain(
            llm=self.llm,
            prompt=ChatPromptTemplate.from_template(query_template)
        )
    
    async def process_query(self, query: str) -> Dict[str, Any]:
        """Process user query into structured format"""
        try:
            result = await self.query_chain.arun(query=query)
            return json.loads(result)
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            # Fallback processing
            return {
                'topic': query,
                'user_belief': query,
                'user_position': 'neutral',
                'intent': 'inform'
            }
    
    async def detect_debate_stance(self, article: Dict, user_belief: str, user_position: str) -> DebateResult:
        """Debate-winning stance detection with reasoning and killer evidence"""
        try:
            result = await self.stance_chain.arun(
                belief=user_belief,
                user_position=user_position,
                title=article.get('title', ''),
                content=article.get('content', '')[:2000]  # Limit content length
            )
            
            stance_data = json.loads(result)
            
            return DebateResult(
                stance=stance_data.get('stance', 'neutral'),
                confidence=stance_data.get('confidence', 0.5),
                reasoning=stance_data.get('reasoning', ''),
                debate_strength=stance_data.get('debate_strength', 0.0),
                killer_evidence=stance_data.get('killer_evidence', [])
            )
            
        except Exception as e:
            logger.error(f"Stance detection error: {e}")
            return DebateResult(
                stance='neutral',
                confidence=0.3,
                reasoning=f"Error in stance detection: {str(e)}",
                debate_strength=0.0,
                killer_evidence=[]
            )
    
    def calculate_bias_score(self, debate_result: DebateResult, user_position: str, bias_slider: float) -> float:
        """Calculate bias score with corrected logic"""
        stance = debate_result.stance
        confidence = debate_result.confidence
        debate_strength = debate_result.debate_strength
        
        # Define stance strength
        stance_strength = {
            'strong_support': 1.0,
            'support': 0.8,
            'weak_support': 0.6,
            'neutral': 0.5,
            'weak_oppose': 0.4,
            'oppose': 0.2,
            'strong_oppose': 0.0
        }
        
        stance_value = stance_strength.get(stance, 0.5)
        
        if user_position == 'positive':
            # User likes the topic
            if stance_value > 0.5:  # Supporting stance
                return bias_slider * confidence * debate_strength
            elif stance_value < 0.5:  # Opposing stance
                return (1.0 - bias_slider) * confidence * debate_strength
            else:  # Neutral
                return 0.5 * confidence * debate_strength
        elif user_position == 'negative':
            # User dislikes the topic
            if stance_value < 0.5:  # Opposing stance (agrees with user)
                return bias_slider * confidence * debate_strength
            elif stance_value > 0.5:  # Supporting stance (disagrees with user)
                return (1.0 - bias_slider) * confidence * debate_strength
            else:  # Neutral
                return 0.5 * confidence * debate_strength
        else:
            # Neutral user position
            return 0.5 * confidence * debate_strength
    
    async def search_and_debate(self, query: str, bias_slider: float = 0.5, limit: int = 10) -> Dict[str, Any]:
        """Complete search and debate analysis pipeline"""
        print(f"🧠 DEBATE RAG: Processing query: '{query}' with bias: {bias_slider}")
        
        # 1. Process query
        processed_query = await self.process_query(query)
        print(f"📝 Processed query - Topic: '{processed_query['topic']}', Position: {processed_query['user_position']}")
        
        # 2. Retrieve articles using existing working system
        print(f"🔍 Retrieving articles using existing system...")
        articles = await self.article_retrieval.search_articles(query, bias=bias_slider, limit=limit)
        print(f"📰 Retrieved {len(articles)} articles")
        
        # 3. Analyze articles with debate-focused stance detection
        print(f"🧠 Analyzing articles with debate-focused stance detection...")
        debate_articles = []
        
        for article in articles:
            try:
                # Detect debate stance
                debate_result = await self.detect_debate_stance(
                    article, 
                    processed_query['user_belief'], 
                    processed_query['user_position']
                )
                
                # Calculate bias score
                bias_score = self.calculate_bias_score(
                    debate_result, 
                    processed_query['user_position'], 
                    bias_slider
                )
                
                # Create debate article
                debate_article = DebateArticle(
                    title=article.get('title', ''),
                    content=article.get('content', ''),
                    url=article.get('url', ''),
                    source=article.get('source', {}).get('name', 'Unknown'),
                    published_at=article.get('publishedAt', datetime.now().isoformat()),
                    stance=debate_result.stance,
                    confidence=debate_result.confidence,
                    reasoning=debate_result.reasoning,
                    debate_strength=debate_result.debate_strength,
                    killer_evidence=debate_result.killer_evidence,
                    bias_score=bias_score
                )
                
                debate_articles.append(debate_article)
                
            except Exception as e:
                logger.error(f"Error analyzing article '{article.get('title', '')}': {e}")
                continue
        
        print(f"🧠 Analyzed {len(debate_articles)} articles")
        
        # 4. Sort by bias score and debate strength
        debate_articles.sort(key=lambda x: (x.bias_score or 0) * (x.debate_strength or 0), reverse=True)
        
        # 5. Prepare results
        results = {
            'query': query,
            'processed_query': processed_query,
            'articles': [
                {
                    'title': article.title,
                    'source': article.source,
                    'url': article.url,
                    'stance': article.stance,
                    'confidence': article.confidence,
                    'debate_strength': article.debate_strength,
                    'bias_score': article.bias_score,
                    'reasoning': article.reasoning,
                    'killer_evidence': article.killer_evidence
                }
                for article in debate_articles
            ],
            'summary': {
                'total_articles': len(debate_articles),
                'stance_distribution': self._get_stance_distribution(debate_articles),
                'average_confidence': sum(a.confidence or 0 for a in debate_articles) / len(debate_articles) if debate_articles else 0,
                'average_debate_strength': sum(a.debate_strength or 0 for a in debate_articles) / len(debate_articles) if debate_articles else 0
            }
        }
        
        return results
    
    def _get_stance_distribution(self, articles: List[DebateArticle]) -> Dict[str, int]:
        """Get distribution of stances across articles"""
        distribution = {}
        for article in articles:
            stance = article.stance or 'neutral'
            distribution[stance] = distribution.get(stance, 0) + 1
        return distribution 