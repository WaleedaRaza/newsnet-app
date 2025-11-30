"""
Advanced RAG Engine with Improved Stance Detection
Replaces the problematic stance detection with a more robust system
"""

import asyncio
import json
import logging
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass
import os

# LangChain imports
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS, Chroma
from langchain.schema import Document
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

# News API imports
import aiohttp
import feedparser
from pygooglenews import GoogleNews
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

@dataclass
class ProcessedQuery:
    """Structured query with user context"""
    topic: str
    user_belief: str
    user_position: str  # 'positive', 'negative', 'neutral'
    bias_slider: float
    context: Dict[str, Any]
    intent: str

@dataclass
class Article:
    """Enhanced article with analysis"""
    title: str
    content: str
    url: str
    source: str
    published_at: str
    stance: Optional[str] = None
    confidence: Optional[float] = None
    reasoning: Optional[str] = None
    evidence: Optional[List[str]] = None
    bias_score: Optional[float] = None
    uncertainty: Optional[float] = None

@dataclass
class StanceResult:
    """Improved stance detection result"""
    stance: str  # 'strong_support', 'support', 'weak_support', 'neutral', 'weak_oppose', 'oppose', 'strong_oppose'
    confidence: float
    reasoning: str
    evidence: List[str]
    uncertainty: float
    alternative_stances: List[str]
    debate_strength: float
    killer_evidence: List[str]

class AdvancedRAGEngine:
    """
    Advanced RAG engine with improved stance detection
    """
    
    def __init__(self, openai_api_key: str):
        self.openai_api_key = openai_api_key
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.1,
            openai_api_key=openai_api_key
        )
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        
        # Initialize vector store
        self.vector_store = None
        self._initialize_vector_store()
        
        # Initialize chains
        self._initialize_chains()
        
        logger.info("Advanced RAG Engine initialized")
    
    def _initialize_vector_store(self):
        """Initialize vector database"""
        try:
            if os.path.exists("advanced_rag_index"):
                self.vector_store = FAISS.load_local("advanced_rag_index", self.embeddings)
                logger.info("Loaded existing advanced RAG index")
            else:
                self.vector_store = FAISS.from_texts(
                    ["Initial document"], 
                    self.embeddings
                )
                logger.info("Created new advanced RAG index")
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
            self.vector_store = Chroma(
                embedding_function=self.embeddings,
                persist_directory="./advanced_rag_db"
            )
    
    def _initialize_chains(self):
        """Initialize LangChain chains for different tasks"""
        
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
            "evidence": ["supporting or opposing evidence"],
            "uncertainty": 0.0-1.0,
            "alternative_stances": ["other possible stances"],
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
        Process this user query to extract structured information.
        
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
        
        # Debate-focused search term generation
        search_template = """
        Generate 10 search terms for finding news articles about: "{topic}"
        User belief: "{belief}"
        User position: {user_position}
        Bias preference: {bias} (0.0 = challenge, 1.0 = affirm)

        If bias is < 0.5, focus on terms like 'debate', 'refutation', 'criticism', 'rebuttal', 'counterargument', 'evidence against', 'disproving', 'destroying', 'demolishing', 'debunking', etc.
        If bias is > 0.5, focus on terms like 'best arguments for', 'proof', 'supporting evidence', 'defense of', 'making the case for', 'strongest support', etc.
        Mix exact phrases, keywords, and semantic variations.
        Return only the search terms, one per line.
        """
        
        self.search_chain = LLMChain(
            llm=self.llm,
            prompt=ChatPromptTemplate.from_template(search_template)
        )
    
    async def process_query(self, query: str, bias_slider: float = 0.5) -> ProcessedQuery:
        """Process user query into structured format"""
        try:
            # Use LLM to process query
            result = await self.query_chain.arun(query=query)
            query_data = json.loads(result)
            
            return ProcessedQuery(
                topic=query_data.get('topic', ''),
                user_belief=query_data.get('user_belief', ''),
                user_position=query_data.get('user_position', 'neutral'),
                bias_slider=bias_slider,
                context={},
                intent=query_data.get('intent', 'inform')
            )
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            # Fallback processing
            return ProcessedQuery(
                topic=query,
                user_belief=query,
                user_position='neutral',
                bias_slider=bias_slider,
                context={},
                intent='inform'
            )
    
    async def generate_search_terms(self, processed_query: ProcessedQuery) -> List[str]:
        """Generate intelligent search terms"""
        try:
            result = await self.search_chain.arun(
                topic=processed_query.topic,
                belief=processed_query.user_belief,
                user_position=processed_query.user_position,
                bias=processed_query.bias_slider
            )
            
            # Parse search terms
            search_terms = [term.strip() for term in result.strip().split('\n') if term.strip()]
            return search_terms[:10]  # Limit to 10 terms
            
        except Exception as e:
            logger.error(f"Error generating search terms: {e}")
            # Fallback search terms
            return [processed_query.topic]
    
    async def retrieve_articles(self, search_terms: List[str], limit: int = 20) -> List[Article]:
        """Retrieve articles using only open/free sources and scraping"""
        all_articles = []
        for search_term in search_terms:
            try:
                # Google News (pygooglenews, scraping)
                articles = await self._search_google_news(search_term, limit // len(search_terms))
                all_articles.extend(articles)
                # RSS Feeds (direct HTTP)
                articles = await self._search_rss_feeds(search_term, limit // len(search_terms))
                all_articles.extend(articles)
            except Exception as e:
                logger.error(f"Error retrieving articles for '{search_term}': {e}")
                continue
        # Fallback: DuckDuckGo web search scraping
        if len(all_articles) < 3:
            for search_term in search_terms:
                try:
                    articles = self._search_duckduckgo(search_term, limit=3)
                    all_articles.extend(articles)
                except Exception as e:
                    logger.error(f"DuckDuckGo fallback error: {e}")
        # Remove duplicates and limit
        unique_articles = self._deduplicate_articles(all_articles)
        return unique_articles[:limit]
    
    async def _search_google_news(self, search_term: str, limit: int) -> List[Article]:
        """Search Google News"""
        try:
            gn = GoogleNews(lang='en', country='US')
            results = gn.search(search_term, when='7d')
            
            articles = []
            for item in results['entries'][:limit]:
                articles.append(Article(
                    title=item.get('title', ''),
                    content=item.get('summary', ''),
                    url=item.get('link', ''),
                    source=item.get('source', {}).get('title', 'Google News'),
                    published_at=item.get('published', datetime.now().isoformat())
                ))
            
            return articles
            
        except Exception as e:
            logger.error(f"Google News search error: {e}")
            return []
    
    async def _search_rss_feeds(self, search_term: str, limit: int) -> List[Article]:
        """Search RSS feeds"""
        try:
            # Major news RSS feeds
            rss_feeds = [
                'http://feeds.bbci.co.uk/news/rss.xml',
                'http://rss.cnn.com/rss/edition.rss',
                'http://feeds.reuters.com/reuters/topNews',
                'http://feeds.npr.org/1001/rss.xml'
            ]
            
            articles = []
            for feed_url in rss_feeds:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(feed_url) as response:
                            if response.status == 200:
                                content = await response.text()
                                feed_articles = self._parse_rss_content(content, search_term, feed_url)
                                articles.extend(feed_articles)
                except Exception as e:
                    logger.error(f"RSS feed error for {feed_url}: {e}")
                    continue
            
            return articles[:limit]
            
        except Exception as e:
            logger.error(f"RSS search error: {e}")
            return []
    
    def _parse_rss_content(self, content: str, search_term: str, feed_url: str) -> List[Article]:
        """Parse RSS content and filter for relevance"""
        articles = []
        
        try:
            import re
            
            # Extract items from RSS
            item_pattern = r'<item>(.*?)</item>'
            items = re.findall(item_pattern, content, re.DOTALL)
            
            # Clean search terms
            search_words = [word.lower().strip() for word in search_term.lower().split() if len(word) > 2]
            
            for item in items:
                # Extract title
                title_match = re.search(r'<title>(.*?)</title>', item, re.DOTALL)
                title = title_match.group(1).strip() if title_match else ''
                
                # Extract description
                desc_match = re.search(r'<description>(.*?)</description>', item, re.DOTALL)
                description = desc_match.group(1).strip() if desc_match else ''
                
                # Extract link
                link_match = re.search(r'<link>(.*?)</link>', item, re.DOTALL)
                link = link_match.group(1).strip() if link_match else ''
                
                # Clean HTML tags
                title_clean = re.sub(r'<[^>]+>', '', title)
                desc_clean = re.sub(r'<[^>]+>', '', description)
                
                # Check relevance
                full_text = f"{title_clean} {desc_clean}".lower()
                word_matches = sum(1 for word in search_words if word in full_text)
                
                if word_matches >= 2:  # At least 2 word matches
                    articles.append(Article(
                        title=title_clean,
                        content=desc_clean,
                        url=link,
                        source=self._get_source_name(feed_url),
                        published_at=datetime.now().isoformat()
                    ))
        
        except Exception as e:
            logger.error(f"RSS parsing error: {e}")
        
        return articles
    
    def _get_source_name(self, feed_url: str) -> str:
        """Extract source name from feed URL"""
        if 'bbci.co.uk' in feed_url:
            return 'BBC News'
        elif 'cnn.com' in feed_url:
            return 'CNN'
        elif 'reuters.com' in feed_url:
            return 'Reuters'
        elif 'npr.org' in feed_url:
            return 'NPR'
        else:
            return 'RSS Feed'
    
    def _deduplicate_articles(self, articles: List[Article]) -> List[Article]:
        """Remove duplicate articles based on URL"""
        seen_urls = set()
        unique_articles = []
        
        for article in articles:
            if article.url not in seen_urls:
                seen_urls.add(article.url)
                unique_articles.append(article)
        
        return unique_articles
    
    async def detect_stance(self, article: Article, processed_query: ProcessedQuery) -> StanceResult:
        """Debate-winning stance detection with reasoning and killer evidence"""
        try:
            result = await self.stance_chain.arun(
                belief=processed_query.user_belief,
                user_position=processed_query.user_position,
                title=article.title,
                content=article.content[:2000]  # Limit content length
            )
            stance_data = json.loads(result)
            return StanceResult(
                stance=stance_data.get('stance', 'neutral'),
                confidence=stance_data.get('confidence', 0.5),
                reasoning=stance_data.get('reasoning', ''),
                evidence=stance_data.get('evidence', []),
                uncertainty=stance_data.get('uncertainty', 0.5),
                alternative_stances=stance_data.get('alternative_stances', []),
                debate_strength=stance_data.get('debate_strength', 0.0),
                killer_evidence=stance_data.get('killer_evidence', [])
            )
        except Exception as e:
            logger.error(f"Stance detection error: {e}")
            return StanceResult(
                stance='neutral',
                confidence=0.3,
                reasoning=f"Error in stance detection: {str(e)}",
                evidence=[],
                uncertainty=0.8,
                alternative_stances=[],
                debate_strength=0.0,
                killer_evidence=[]
            )
    
    def calculate_bias_score(self, stance_result: StanceResult, processed_query: ProcessedQuery) -> float:
        """Calculate bias score with corrected logic"""
        stance = stance_result.stance
        confidence = stance_result.confidence
        user_position = processed_query.user_position
        bias_slider = processed_query.bias_slider
        
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
                return bias_slider * confidence
            elif stance_value < 0.5:  # Opposing stance
                return (1.0 - bias_slider) * confidence
            else:  # Neutral
                return 0.5 * confidence
        elif user_position == 'negative':
            # User dislikes the topic
            if stance_value < 0.5:  # Opposing stance (agrees with user)
                return bias_slider * confidence
            elif stance_value > 0.5:  # Supporting stance (disagrees with user)
                return (1.0 - bias_slider) * confidence
            else:  # Neutral
                return 0.5 * confidence
        else:
            # Neutral user position
            return 0.5 * confidence
    
    async def analyze_articles(self, articles: List[Article], processed_query: ProcessedQuery) -> List[Article]:
        """Analyze articles with advanced stance detection"""
        analyzed_articles = []
        
        for article in articles:
            try:
                # Detect stance
                stance_result = await self.detect_stance(article, processed_query)
                
                # Calculate bias score
                bias_score = self.calculate_bias_score(stance_result, processed_query)
                
                # Update article
                article.stance = stance_result.stance
                article.confidence = stance_result.confidence
                article.reasoning = stance_result.reasoning
                article.evidence = stance_result.evidence
                article.bias_score = bias_score
                article.uncertainty = stance_result.uncertainty
                
                analyzed_articles.append(article)
                
            except Exception as e:
                logger.error(f"Error analyzing article '{article.title}': {e}")
                analyzed_articles.append(article)  # Add without analysis
        
        return analyzed_articles
    
    async def search_and_analyze(self, query: str, bias_slider: float = 0.5, limit: int = 20) -> Dict[str, Any]:
        """Complete search and analysis pipeline"""
        print(f"🔍 ADVANCED RAG: Processing query: '{query}' with bias: {bias_slider}")
        
        # 1. Process query
        processed_query = await self.process_query(query, bias_slider)
        print(f"📝 Processed query - Topic: '{processed_query.topic}', Position: {processed_query.user_position}")
        
        # 2. Generate search terms
        search_terms = await self.generate_search_terms(processed_query)
        print(f"🔍 Generated {len(search_terms)} search terms: {search_terms[:3]}...")
        
        # 3. Retrieve articles
        articles = await self.retrieve_articles(search_terms, limit)
        print(f"📰 Retrieved {len(articles)} articles")
        
        # 4. Analyze articles
        analyzed_articles = await self.analyze_articles(articles, processed_query)
        print(f"🧠 Analyzed {len(analyzed_articles)} articles")
        
        # 5. Sort by bias score
        analyzed_articles.sort(key=lambda x: x.bias_score or 0, reverse=True)
        
        # 6. Prepare results
        results = {
            'query': query,
            'processed_query': {
                'topic': processed_query.topic,
                'user_belief': processed_query.user_belief,
                'user_position': processed_query.user_position,
                'bias_slider': processed_query.bias_slider
            },
            'articles': [
                {
                    'title': article.title,
                    'source': article.source,
                    'url': article.url,
                    'stance': article.stance,
                    'confidence': article.confidence,
                    'bias_score': article.bias_score,
                    'uncertainty': article.uncertainty,
                    'reasoning': article.reasoning,
                    'evidence': article.evidence
                }
                for article in analyzed_articles
            ],
            'summary': {
                'total_articles': len(analyzed_articles),
                'stance_distribution': self._get_stance_distribution(analyzed_articles),
                'average_confidence': sum(a.confidence or 0 for a in analyzed_articles) / len(analyzed_articles) if analyzed_articles else 0,
                'average_uncertainty': sum(a.uncertainty or 0 for a in analyzed_articles) / len(analyzed_articles) if analyzed_articles else 0
            }
        }
        
        return results
    
    def _get_stance_distribution(self, articles: List[Article]) -> Dict[str, int]:
        """Get distribution of stances across articles"""
        distribution = {}
        for article in articles:
            stance = article.stance or 'neutral'
            distribution[stance] = distribution.get(stance, 0) + 1
        return distribution

    def _search_duckduckgo(self, search_term: str, limit: int = 3) -> List[Article]:
        """Scrape DuckDuckGo search results for news articles (no API key)"""
        articles = []
        try:
            url = f"https://duckduckgo.com/html/?q={requests.utils.quote(search_term + ' news')}"
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(resp.text, "html.parser")
            results = soup.find_all('a', class_='result__a', limit=limit)
            for result in results:
                title = result.get_text()
                link = result['href']
                articles.append(Article(
                    title=title,
                    content="",  # No summary from DDG
                    url=link,
                    source="DuckDuckGo",
                    published_at=datetime.now().isoformat()
                ))
        except Exception as e:
            logger.error(f"DuckDuckGo scraping error: {e}")
        return articles 