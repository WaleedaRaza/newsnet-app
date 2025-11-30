"""
LangChain-Powered Intelligent News Engine
Replaces static API approach with LLM-based intelligent retrieval
"""

import asyncio
import json
import logging
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import os

# LangChain imports
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS, Chroma
from langchain.retrievers import MultiQueryRetriever, EnsembleRetriever
from langchain.chains import RetrievalQA, LLMChain
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.memory import ConversationBufferMemory
from langchain.agents import Tool, AgentExecutor, create_openai_functions_agent
from langchain.tools import BaseTool

# News API imports
import aiohttp
import feedparser
from pygooglenews import GoogleNews
import requests

# Vector DB
import chromadb
from chromadb.config import Settings

logger = logging.getLogger(__name__)

@dataclass
class NewsArticle:
    """Structured news article with LLM analysis"""
    title: str
    content: str
    url: str
    source: str
    published_at: str
    llm_stance: Optional[str] = None
    llm_confidence: Optional[float] = None
    llm_bias_score: Optional[float] = None
    llm_framing: Optional[str] = None
    llm_omissions: Optional[List[str]] = None
    embedding: Optional[List[float]] = None

@dataclass
class UserQuery:
    """User query with bias preferences"""
    topic: str
    user_belief: str
    bias_slider: float  # 0.0 = challenge me, 1.0 = affirm me
    limit: int = 20

@dataclass
class NewsAnalysis:
    """Complete news analysis result"""
    articles: List[NewsArticle]
    summary: str
    stance_comparison: Dict[str, Any]
    narrative_fusion: str
    citations: List[str]
    bias_analysis: Dict[str, Any]

class LangChainNewsEngine:
    """
    Intelligent news engine using LangChain + LLMs
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
        
        # Initialize tools
        self._initialize_tools()
        
        logger.info("LangChain News Engine initialized")
    
    def _initialize_vector_store(self):
        """Initialize vector database"""
        try:
            # Try to load existing index
            if os.path.exists("news_vector_index"):
                self.vector_store = FAISS.load_local("news_vector_index", self.embeddings)
                logger.info("Loaded existing vector index")
            else:
                # Create new index
                self.vector_store = FAISS.from_texts(
                    ["Initial document"], 
                    self.embeddings
                )
                logger.info("Created new vector index")
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
            # Fallback to Chroma
            self.vector_store = Chroma(
                embedding_function=self.embeddings,
                persist_directory="./chroma_db"
            )
    
    def _initialize_chains(self):
        """Initialize LangChain chains"""
        
        # Stance detection chain
        stance_template = """
        Analyze if this article supports, opposes, or is neutral toward this belief:
        
        BELIEF: {belief}
        ARTICLE TITLE: {title}
        ARTICLE CONTENT: {content}
        
        Consider:
        1. Does the article explicitly support or oppose the belief?
        2. What is the tone and framing used?
        3. What facts or perspectives are emphasized or omitted?
        4. How confident are you in this assessment?
        
        Return JSON:
        {{
            "stance": "support/oppose/neutral",
            "confidence": 0.0-1.0,
            "reasoning": "detailed explanation",
            "framing": "how the topic is presented",
            "omissions": ["list of omitted facts/perspectives"],
            "tone": "objective/biased/sarcastic/alarmist/etc"
        }}
        """
        
        self.stance_chain = LLMChain(
            llm=self.llm,
            prompt=ChatPromptTemplate.from_template(stance_template)
        )
        
        # Search term generation chain
        search_template = """
        Generate intelligent search terms for finding news articles about: "{topic}"
        
        User belief: "{belief}"
        Bias preference: {bias} (0.0 = challenging views, 1.0 = supporting views)
        
        Generate 15 search terms that will find articles matching the user's bias preference.
        Mix exact phrases, keywords, and semantic variations.
        
        Return only the search terms, one per line.
        """
        
        self.search_chain = LLMChain(
            llm=self.llm,
            prompt=ChatPromptTemplate.from_template(search_template)
        )
        
        # Narrative fusion chain
        fusion_template = """
        Synthesize these articles about "{topic}" into a comprehensive analysis:
        
        USER BELIEF: "{belief}"
        BIAS PREFERENCE: {bias}
        
        ARTICLES:
        {articles}
        
        Provide:
        1. A balanced summary highlighting different perspectives
        2. Points of agreement and disagreement between sources
        3. Potential biases or omissions in each source
        4. Key facts and evidence presented
        5. How this relates to the user's belief
        
        Format as structured analysis with clear sections.
        """
        
        self.fusion_chain = LLMChain(
            llm=self.llm,
            prompt=ChatPromptTemplate.from_template(fusion_template)
        )
    
    def _initialize_tools(self):
        """Initialize LangChain tools for news retrieval"""
        
        # News API tool
        class NewsAPITool(BaseTool):
            name = "news_api_search"
            description = "Search for recent news articles using NewsAPI"
            
            def _run(self, query: str) -> List[Dict]:
                try:
                    # Implementation here
                    return []
                except Exception as e:
                    return []
        
        # Google News tool
        class GoogleNewsTool(BaseTool):
            name = "google_news_search"
            description = "Search for news articles using Google News"
            
            def _run(self, query: str) -> List[Dict]:
                try:
                    gn = GoogleNews()
                    result = gn.search(query, when='7d')
                    return result.get('entries', [])
                except Exception as e:
                    return []
        
        # RSS tool
        class RSSTool(BaseTool):
            name = "rss_feed_search"
            description = "Search RSS feeds for news articles"
            
            def _run(self, query: str) -> List[Dict]:
                try:
                    # RSS implementation
                    return []
                except Exception as e:
                    return []
        
        self.tools = [
            NewsAPITool(),
            GoogleNewsTool(),
            RSSTool()
        ]
        
        # Create agent
        self.agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self._create_agent_prompt()
        )
        
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True
        )
    
    def _create_agent_prompt(self):
        """Create prompt for the news retrieval agent"""
        return ChatPromptTemplate.from_template("""
        You are an intelligent news research assistant. Your task is to find relevant news articles based on user queries and bias preferences.
        
        USER QUERY: {query}
        USER BELIEF: {belief}
        BIAS PREFERENCE: {bias} (0.0 = challenging views, 1.0 = supporting views)
        
        Use the available tools to search for articles from multiple sources.
        Focus on finding articles that match the user's bias preference.
        Prioritize quality, relevance, and source diversity.
        
        Return a list of the most relevant articles with their URLs and brief descriptions.
        """)
    
    async def search_news_intelligent(self, user_query: UserQuery) -> NewsAnalysis:
        """
        Main method: Intelligent news search with LLM analysis
        """
        logger.info(f"Starting intelligent news search for: {user_query.topic}")
        
        # 1. Generate intelligent search terms
        search_terms = await self._generate_search_terms(user_query)
        logger.info(f"Generated {len(search_terms)} search terms")
        
        # 2. Retrieve articles from multiple sources
        articles = await self._retrieve_articles(search_terms, user_query.limit)
        logger.info(f"Retrieved {len(articles)} articles")
        
        # 3. Analyze articles with LLM
        analyzed_articles = await self._analyze_articles(articles, user_query)
        logger.info(f"Analyzed {len(analyzed_articles)} articles")
        
        # 4. Create vector embeddings and store
        await self._store_articles(analyzed_articles)
        
        # 5. Synthesize narrative
        synthesis = await self._synthesize_narrative(analyzed_articles, user_query)
        
        # 6. Create final analysis
        analysis = NewsAnalysis(
            articles=analyzed_articles,
            summary=synthesis['summary'],
            stance_comparison=synthesis['stance_comparison'],
            narrative_fusion=synthesis['narrative_fusion'],
            citations=synthesis['citations'],
            bias_analysis=synthesis['bias_analysis']
        )
        
        return analysis
    
    async def _generate_search_terms(self, user_query: UserQuery) -> List[str]:
        """Generate intelligent search terms using LLM"""
        try:
            response = await self.search_chain.arun(
                topic=user_query.topic,
                belief=user_query.user_belief,
                bias=user_query.bias_slider
            )
            
            # Parse response into search terms
            terms = [term.strip() for term in response.split('\n') if term.strip()]
            return terms[:15]  # Limit to 15 terms
            
        except Exception as e:
            logger.error(f"Error generating search terms: {e}")
            # Fallback to basic terms
            return [user_query.topic, f'"{user_query.topic}"']
    
    async def _retrieve_articles(self, search_terms: List[str], limit: int) -> List[NewsArticle]:
        """Retrieve articles from multiple sources"""
        all_articles = []
        
        for term in search_terms[:5]:  # Use top 5 terms
            try:
                # Use agent to search multiple sources
                result = await self.agent_executor.arun(
                    query=term,
                    belief="",  # Will be filled in later
                    bias=0.5
                )
                
                # Parse agent results into articles
                articles = self._parse_agent_results(result)
                all_articles.extend(articles)
                
                if len(all_articles) >= limit * 2:  # Get extra for filtering
                    break
                    
            except Exception as e:
                logger.error(f"Error retrieving articles for term '{term}': {e}")
                continue
        
        # Remove duplicates and limit
        unique_articles = self._deduplicate_articles(all_articles)
        return unique_articles[:limit]
    
    def _parse_agent_results(self, result: str) -> List[NewsArticle]:
        """Parse agent results into structured articles"""
        articles = []
        
        try:
            # This is a simplified parser - in production, use more robust parsing
            lines = result.split('\n')
            current_article = {}
            
            for line in lines:
                if 'Title:' in line:
                    if current_article:
                        articles.append(NewsArticle(**current_article))
                    current_article = {'title': line.split('Title:')[1].strip()}
                elif 'URL:' in line:
                    current_article['url'] = line.split('URL:')[1].strip()
                elif 'Source:' in line:
                    current_article['source'] = line.split('Source:')[1].strip()
                elif 'Content:' in line:
                    current_article['content'] = line.split('Content:')[1].strip()
            
            if current_article:
                articles.append(NewsArticle(**current_article))
                
        except Exception as e:
            logger.error(f"Error parsing agent results: {e}")
        
        return articles
    
    async def _analyze_articles(self, articles: List[NewsArticle], user_query: UserQuery) -> List[NewsArticle]:
        """Analyze articles with LLM for stance, bias, and framing"""
        analyzed_articles = []
        
        for article in articles:
            try:
                # Analyze stance
                stance_result = await self.stance_chain.arun(
                    belief=user_query.user_belief,
                    title=article.title,
                    content=article.content[:1000]  # Limit content length
                )
                
                # Parse stance result
                stance_data = json.loads(stance_result)
                
                # Update article with analysis
                article.llm_stance = stance_data.get('stance')
                article.llm_confidence = stance_data.get('confidence')
                article.llm_framing = stance_data.get('framing')
                article.llm_omissions = stance_data.get('omissions', [])
                
                # Calculate bias score based on stance and user preference
                article.llm_bias_score = self._calculate_bias_score(
                    stance_data, user_query.bias_slider, user_query.user_belief
                )
                
                analyzed_articles.append(article)
                
            except Exception as e:
                logger.error(f"Error analyzing article '{article.title}': {e}")
                analyzed_articles.append(article)  # Add without analysis
        
        return analyzed_articles
    
    def _calculate_bias_score(self, stance_data: Dict, bias_slider: float, user_belief: str) -> float:
        """Calculate bias score based on stance and user preference"""
        stance = stance_data.get('stance', 'neutral')
        confidence = stance_data.get('confidence', 0.5)
        
        # Determine if user has negative or positive view
        negative_words = ['hate', 'terrible', 'awful', 'bad', 'wrong', 'dislike']
        user_negative = any(word in user_belief.lower() for word in negative_words)
        
        if bias_slider == 0.0:  # User wants challenging views
            if user_negative:
                # User hates topic, so challenging = articles that support topic
                return 1.0 if stance == 'oppose' else 0.0
            else:
                # User likes topic, so challenging = articles that oppose topic
                return 1.0 if stance == 'oppose' else 0.0
        elif bias_slider == 1.0:  # User wants supporting views
            if user_negative:
                # User hates topic, so supporting = articles that also oppose topic
                return 1.0 if stance == 'support' else 0.0
            else:
                # User likes topic, so supporting = articles that also support topic
                return 1.0 if stance == 'support' else 0.0
        else:
            # Intermediate bias - linear interpolation
            if stance == 'support':
                return bias_slider * confidence
            elif stance == 'oppose':
                return (1.0 - bias_slider) * confidence
            else:
                return 0.5 * confidence
    
    async def _store_articles(self, articles: List[NewsArticle]):
        """Store articles in vector database"""
        try:
            # Create documents for vector store
            documents = []
            for article in articles:
                doc = Document(
                    page_content=f"{article.title}\n{article.content}",
                    metadata={
                        'title': article.title,
                        'url': article.url,
                        'source': article.source,
                        'published_at': article.published_at,
                        'stance': article.llm_stance,
                        'bias_score': article.llm_bias_score
                    }
                )
                documents.append(doc)
            
            # Add to vector store
            if documents:
                self.vector_store.add_documents(documents)
                self.vector_store.save_local("news_vector_index")
                logger.info(f"Stored {len(documents)} articles in vector database")
                
        except Exception as e:
            logger.error(f"Error storing articles: {e}")
    
    async def _synthesize_narrative(self, articles: List[NewsArticle], user_query: UserQuery) -> Dict:
        """Synthesize articles into narrative analysis"""
        try:
            # Prepare articles for synthesis
            articles_text = ""
            for i, article in enumerate(articles):
                articles_text += f"\nARTICLE {i+1}:\n"
                articles_text += f"Title: {article.title}\n"
                articles_text += f"Source: {article.source}\n"
                articles_text += f"Stance: {article.llm_stance} (confidence: {article.llm_confidence})\n"
                articles_text += f"Content: {article.content[:500]}...\n"
            
            # Generate synthesis
            synthesis_result = await self.fusion_chain.arun(
                topic=user_query.topic,
                belief=user_query.user_belief,
                bias=user_query.bias_slider,
                articles=articles_text
            )
            
            # Extract citations
            citations = [article.url for article in articles]
            
            # Create stance comparison
            stance_comparison = {}
            for article in articles:
                source = article.source
                if source not in stance_comparison:
                    stance_comparison[source] = []
                stance_comparison[source].append({
                    'title': article.title,
                    'stance': article.llm_stance,
                    'confidence': article.llm_confidence,
                    'bias_score': article.llm_bias_score
                })
            
            return {
                'summary': synthesis_result,
                'stance_comparison': stance_comparison,
                'narrative_fusion': synthesis_result,
                'citations': citations,
                'bias_analysis': {
                    'user_belief': user_query.user_belief,
                    'bias_preference': user_query.bias_slider,
                    'articles_analyzed': len(articles),
                    'stance_distribution': self._get_stance_distribution(articles)
                }
            }
            
        except Exception as e:
            logger.error(f"Error synthesizing narrative: {e}")
            return {
                'summary': "Error generating synthesis",
                'stance_comparison': {},
                'narrative_fusion': "Error generating fusion",
                'citations': [],
                'bias_analysis': {}
            }
    
    def _get_stance_distribution(self, articles: List[NewsArticle]) -> Dict[str, int]:
        """Get distribution of stances across articles"""
        distribution = {'support': 0, 'oppose': 0, 'neutral': 0}
        for article in articles:
            stance = article.llm_stance or 'neutral'
            distribution[stance] = distribution.get(stance, 0) + 1
        return distribution
    
    def _deduplicate_articles(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """Remove duplicate articles based on URL"""
        seen_urls = set()
        unique_articles = []
        
        for article in articles:
            if article.url not in seen_urls:
                seen_urls.add(article.url)
                unique_articles.append(article)
        
        return unique_articles
    
    async def query_vector_store(self, query: str, k: int = 10) -> List[Document]:
        """Query the vector store for similar articles"""
        try:
            retriever = self.vector_store.as_retriever(search_kwargs={"k": k})
            documents = await retriever.aget_relevant_documents(query)
            return documents
        except Exception as e:
            logger.error(f"Error querying vector store: {e}")
            return []
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        return {
            'vector_store_size': len(self.vector_store.index_to_docstore_id) if self.vector_store else 0,
            'llm_model': 'gpt-4',
            'embeddings_model': 'text-embedding-ada-002',
            'tools_available': len(self.tools)
        } 