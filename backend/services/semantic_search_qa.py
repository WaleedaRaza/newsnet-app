"""
Semantic Search & Q&A Service

This service provides semantic search capabilities over news articles and
can answer questions about the news corpus using semantic embeddings and LLMs.

Features:
- Semantic search over article content
- Question answering with source attribution
- Multi-source answer synthesis
- Confidence scoring for answers
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import numpy as np
from sentence_transformers import SentenceTransformer
import re

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Result from semantic search"""
    article_id: str
    title: str
    content: str
    source: str
    similarity_score: float
    metadata: Dict[str, Any] = None

@dataclass
class QAResult:
    """Result from question answering"""
    question: str
    answer: str
    confidence: float
    sources: List[SearchResult]
    evidence: List[str]
    metadata: Dict[str, Any] = None

class SemanticSearchQAService:
    """
    Service for semantic search and question answering over news articles
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize sentence transformer for semantic embeddings
        try:
            self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
            self.logger.info("Sentence transformer initialized for semantic search")
        except Exception as e:
            self.logger.error(f"Failed to initialize sentence transformer: {e}")
            self.sentence_transformer = None
        
        # Article storage (in production, use vector database)
        self.articles: List[Dict[str, Any]] = []
        self.article_embeddings: Optional[np.ndarray] = None
        
        # Search configuration
        self.max_results = 10
        self.similarity_threshold = 0.3
        
        # Q&A configuration
        self.max_sources = 5
        self.min_confidence = 0.5
        
        self.logger.info("SemanticSearchQAService initialized")
    
    async def add_articles(self, articles: List[Dict[str, Any]]) -> None:
        """
        Add articles to the search index
        
        Args:
            articles: List of article dictionaries with 'id', 'title', 'content', 'source'
        """
        if not self.sentence_transformer:
            raise ValueError("Sentence transformer not available")
        
        # Add articles
        self.articles.extend(articles)
        
        # Generate embeddings for all articles
        article_texts = []
        for article in self.articles:
            # Combine title and content for better search
            text = f"{article.get('title', '')} {article.get('content', '')}"
            article_texts.append(text)
        
        self.article_embeddings = self.sentence_transformer.encode(article_texts)
        
        self.logger.info(f"Added {len(articles)} articles to search index. Total: {len(self.articles)}")
    
    async def semantic_search(
        self, 
        query: str, 
        max_results: int = None,
        similarity_threshold: float = None
    ) -> List[SearchResult]:
        """
        Perform semantic search over articles
        
        Args:
            query: Search query
            max_results: Maximum number of results
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of SearchResult objects
        """
        if not self.sentence_transformer or self.article_embeddings is None:
            raise ValueError("Search index not available")
        
        max_results = max_results or self.max_results
        similarity_threshold = similarity_threshold or self.similarity_threshold
        
        # Encode query
        query_embedding = self.sentence_transformer.encode([query])[0]
        
        # Calculate similarities
        similarities = []
        for i, article_embedding in enumerate(self.article_embeddings):
            similarity = self._cosine_similarity(query_embedding, article_embedding)
            similarities.append((i, similarity))
        
        # Sort by similarity and filter by threshold
        similarities.sort(key=lambda x: x[1], reverse=True)
        filtered_results = [(idx, score) for idx, score in similarities if score >= similarity_threshold]
        
        # Create search results
        results = []
        for idx, score in filtered_results[:max_results]:
            article = self.articles[idx]
            result = SearchResult(
                article_id=article.get('id', f'article_{idx}'),
                title=article.get('title', ''),
                content=article.get('content', ''),
                source=article.get('source', ''),
                similarity_score=score,
                metadata={
                    'url': article.get('url', ''),
                    'published_at': article.get('published_at', ''),
                    'category': article.get('category', '')
                }
            )
            results.append(result)
        
        self.logger.info(f"Semantic search for '{query}' returned {len(results)} results")
        return results
    
    async def answer_question(
        self, 
        question: str,
        max_sources: int = None,
        min_confidence: float = None
    ) -> QAResult:
        """
        Answer a question using semantic search and content analysis
        
        Args:
            question: The question to answer
            max_sources: Maximum number of sources to use
            min_confidence: Minimum confidence threshold
            
        Returns:
            QAResult with answer and sources
        """
        max_sources = max_sources or self.max_sources
        min_confidence = min_confidence or self.min_confidence
        
        # Search for relevant articles
        search_results = await self.semantic_search(question, max_results=max_sources * 2)
        
        if not search_results:
            return QAResult(
                question=question,
                answer="I couldn't find any relevant information to answer your question.",
                confidence=0.0,
                sources=[],
                evidence=[],
                metadata={'reason': 'no_relevant_sources'}
            )
        
        # Analyze top sources
        top_sources = search_results[:max_sources]
        answer, confidence, evidence = await self._synthesize_answer(question, top_sources)
        
        # Check confidence threshold
        if confidence < min_confidence:
            answer = "I found some information but I'm not confident enough to provide a definitive answer."
            confidence = 0.0
        
        return QAResult(
            question=question,
            answer=answer,
            confidence=confidence,
            sources=top_sources,
            evidence=evidence,
            metadata={
                'sources_used': len(top_sources),
                'total_sources_available': len(search_results),
                'synthesis_method': 'semantic_analysis'
            }
        )
    
    async def _synthesize_answer(
        self, 
        question: str, 
        sources: List[SearchResult]
    ) -> Tuple[str, float, List[str]]:
        """
        Synthesize an answer from multiple sources
        
        Args:
            question: The original question
            sources: List of relevant sources
            
        Returns:
            Tuple of (answer, confidence, evidence)
        """
        # Extract key information from sources
        key_points = []
        evidence = []
        
        for source in sources:
            # Extract relevant sentences from source content
            relevant_sentences = self._extract_relevant_sentences(question, source.content)
            
            for sentence in relevant_sentences:
                key_points.append({
                    'text': sentence,
                    'source': source.title,
                    'similarity': source.similarity_score
                })
                evidence.append(f"From {source.title}: {sentence}")
        
        # Sort by relevance
        key_points.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Generate answer (simplified synthesis)
        if not key_points:
            return "I couldn't extract specific information to answer your question.", 0.0, []
        
        # Take top 3 most relevant points
        top_points = key_points[:3]
        
        # Simple answer synthesis
        answer_parts = []
        for point in top_points:
            answer_parts.append(point['text'])
        
        answer = " ".join(answer_parts)
        
        # Calculate confidence based on source quality and relevance
        avg_similarity = np.mean([point['similarity'] for point in top_points])
        source_count = len(sources)
        
        # Confidence formula: average similarity * source coverage factor
        confidence = avg_similarity * min(source_count / 3.0, 1.0)
        
        return answer, confidence, evidence[:3]  # Top 3 pieces of evidence
    
    def _extract_relevant_sentences(self, question: str, content: str) -> List[str]:
        """
        Extract sentences relevant to the question from content
        
        Args:
            question: The question
            content: The content to analyze
            
        Returns:
            List of relevant sentences
        """
        # Simple sentence extraction
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # For now, return first few sentences (in production, use more sophisticated extraction)
        return sentences[:2]
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    async def get_search_statistics(self) -> Dict[str, Any]:
        """Get statistics about the search index"""
        return {
            'total_articles': len(self.articles),
            'embeddings_available': self.article_embeddings is not None,
            'embedding_dimensions': self.article_embeddings.shape[1] if self.article_embeddings is not None else 0,
            'sources': list(set(article.get('source', '') for article in self.articles)),
            'categories': list(set(article.get('category', '') for article in self.articles if article.get('category'))),
            'last_updated': datetime.now().isoformat()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for the service"""
        return {
            'service': 'SemanticSearchQAService',
            'status': 'healthy',
            'sentence_transformer_available': self.sentence_transformer is not None,
            'articles_indexed': len(self.articles),
            'embeddings_generated': self.article_embeddings is not None,
            'timestamp': datetime.now().isoformat()
        }

# Global instance
semantic_search_qa_service = SemanticSearchQAService() 