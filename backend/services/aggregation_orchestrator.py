"""
Aggregation Orchestrator - Main pipeline coordinator for belief-aware article aggregation

This module orchestrates the entire pipeline:
1. Multi-source news fetching
2. Semantic embedding and storage
3. Belief-based retrieval
4. Stance detection
5. Ideology classification
6. Final scoring and ranking
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from uuid import uuid4
from datetime import datetime

# Import our services
from .multi_source_news_service import multi_source_news_service, RawArticle
from .semantic_embedding_service import semantic_embedding_service

logger = logging.getLogger(__name__)

@dataclass
class PipelineTask:
    """Represents a single aggregation request"""
    request_id: str
    topics: List[str]
    beliefs: Dict[str, List[str]]
    bias_slider: float
    user_id: Optional[str] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class PipelineResult:
    """Result of a pipeline execution"""
    task: PipelineTask
    articles: List[Dict[str, Any]]
    execution_time: float
    success: bool
    error_message: Optional[str] = None
    pipeline_metrics: Dict[str, float] = None

@dataclass
class ProcessedArticle:
    """Article with semantic processing results"""
    raw_article: RawArticle
    embedding: Optional[Any] = None
    semantic_score: float = 0.0
    stance: str = "neutral"
    stance_confidence: float = 0.5
    ideology: str = "center"
    final_score: float = 0.0
    processing_metadata: Dict[str, Any] = None

class AggregationOrchestrator:
    """
    Main orchestrator for the belief-aware article aggregation pipeline
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing AggregationOrchestrator")
        
        # Pipeline metrics
        self.metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_execution_time': 0.0,
            'articles_fetched': 0,
            'articles_processed': 0,
            'embedding_time': 0.0,
            'similarity_search_time': 0.0
        }
    
    async def aggregate_articles(
        self,
        topics: List[str],
        beliefs: Dict[str, List[str]],
        bias_slider: float,
        user_id: Optional[str] = None,
        limit_per_topic: int = 10
    ) -> PipelineResult:
        """
        Main entry point for article aggregation
        
        Args:
            topics: List of topics to search for
            beliefs: Dict mapping topics to lists of user beliefs
            bias_slider: User's bias preference (0.0 = challenge, 1.0 = affirm)
            user_id: Optional user ID for caching
            limit_per_topic: Number of articles to return per topic
            
        Returns:
            PipelineResult with articles and metadata
        """
        start_time = time.time()
        
        # Create pipeline task
        task = PipelineTask(
            request_id=str(uuid4()),
            topics=topics,
            beliefs=beliefs,
            bias_slider=bias_slider,
            user_id=user_id
        )
        
        self.logger.info(f"Starting aggregation pipeline for request {task.request_id}")
        self.logger.info(f"Topics: {topics}")
        self.logger.info(f"Beliefs: {beliefs}")
        self.logger.info(f"Bias slider: {bias_slider}")
        
        try:
            # Update metrics
            self.metrics['total_requests'] += 1
            
            # Execute pipeline
            result = await self._execute_pipeline(task, limit_per_topic)
            
            # Update success metrics
            self.metrics['successful_requests'] += 1
            execution_time = time.time() - start_time
            
            # Update average execution time
            total_successful = self.metrics['successful_requests']
            current_avg = self.metrics['average_execution_time']
            self.metrics['average_execution_time'] = (
                (current_avg * (total_successful - 1) + execution_time) / total_successful
            )
            
            self.logger.info(f"Pipeline completed successfully in {execution_time:.2f}s")
            self.logger.info(f"Returning {len(result.articles)} articles")
            
            return PipelineResult(
                task=task,
                articles=result.articles,
                execution_time=execution_time,
                success=True,
                pipeline_metrics=self.metrics.copy()
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.metrics['failed_requests'] += 1
            
            self.logger.error(f"Pipeline failed after {execution_time:.2f}s: {str(e)}")
            self.logger.exception("Pipeline execution error")
            
            return PipelineResult(
                task=task,
                articles=[],
                execution_time=execution_time,
                success=False,
                error_message=str(e),
                pipeline_metrics=self.metrics.copy()
            )
    
    async def _execute_pipeline(
        self, 
        task: PipelineTask, 
        limit_per_topic: int
    ) -> PipelineResult:
        """
        Execute the full aggregation pipeline
        
        This orchestrates all the pipeline modules:
        1. News aggregation
        2. Semantic processing
        3. Stance detection
        4. Ideology classification
        5. Final scoring
        """
        self.logger.info(f"Executing pipeline for task {task.request_id}")
        
        # Step 1: Multi-source news fetching
        self.logger.info("Step 1: Fetching articles from multiple sources")
        raw_articles = await self._fetch_articles_from_multiple_sources(task.topics)
        self.metrics['articles_fetched'] += len(raw_articles)
        
        if not raw_articles:
            self.logger.warning("No articles fetched - returning empty result")
            return PipelineResult(
                task=task,
                articles=[],
                execution_time=0.0,
                success=True
            )
        
        # Step 2: Semantic embedding and belief-based retrieval
        self.logger.info("Step 2: Processing articles semantically")
        processed_articles = await self._process_articles_semantically(raw_articles, task.beliefs)
        self.metrics['articles_processed'] += len(processed_articles)
        
        # Step 3: Stance detection (placeholder for now)
        self.logger.info("Step 3: Detecting stances (placeholder)")
        stance_analyzed_articles = await self._detect_stances(processed_articles, task.beliefs)
        
        # Step 4: Ideology classification (placeholder for now)
        self.logger.info("Step 4: Classifying ideologies (placeholder)")
        ideology_analyzed_articles = await self._classify_ideologies(stance_analyzed_articles)
        
        # Step 5: Final scoring and ranking
        self.logger.info("Step 5: Scoring and ranking articles")
        final_articles = await self._score_and_rank_articles(
            ideology_analyzed_articles, 
            task.bias_slider, 
            limit_per_topic
        )
        
        return PipelineResult(
            task=task,
            articles=final_articles,
            execution_time=0.0,
            success=True
        )
    
    async def _fetch_articles_from_multiple_sources(self, topics: List[str]) -> List[RawArticle]:
        """Step 1: Fetch articles from multiple news sources"""
        self.logger.info(f"Fetching articles for topics: {topics}")
        
        async with multi_source_news_service as news_service:
            articles = await news_service.fetch_articles_for_topics(
                topics=topics,
                max_articles_per_topic=20,
                days_back=7
            )
        
        self.logger.info(f"Fetched {len(articles)} articles from multiple sources")
        return articles
    
    async def _process_articles_semantically(
        self, 
        raw_articles: List[RawArticle], 
        beliefs: Dict[str, List[str]]
    ) -> List[ProcessedArticle]:
        """Step 2: Process articles semantically and find belief-relevant ones"""
        
        self.logger.info(f"Processing {len(raw_articles)} articles semantically")
        
        # Prepare article texts for embedding
        article_texts = []
        for article in raw_articles:
            # Combine title and content for better semantic matching
            text = f"{article.title}. {article.content[:500]}"  # Limit content length
            article_texts.append(text)
        
        # Generate embeddings for all articles
        embedding_start = time.time()
        embedding_results = await semantic_embedding_service.embed_batch(article_texts)
        embedding_time = time.time() - embedding_start
        self.metrics['embedding_time'] += embedding_time
        
        self.logger.info(f"Generated embeddings for {len(embedding_results)} articles in {embedding_time:.2f}s")
        
        # Process each article with its embedding
        processed_articles = []
        for i, (article, embedding_result) in enumerate(zip(raw_articles, embedding_results)):
            processed_article = ProcessedArticle(
                raw_article=article,
                embedding=embedding_result.embedding if embedding_result.success else None,
                processing_metadata={
                    'embedding_success': embedding_result.success,
                    'embedding_time': embedding_result.processing_time,
                    'embedding_model': embedding_result.model_name
                }
            )
            processed_articles.append(processed_article)
        
        # Find belief-relevant articles using similarity search
        belief_relevant_articles = await self._find_belief_relevant_articles(
            processed_articles, beliefs
        )
        
        self.logger.info(f"Found {len(belief_relevant_articles)} belief-relevant articles")
        return belief_relevant_articles
    
    async def _find_belief_relevant_articles(
        self, 
        processed_articles: List[ProcessedArticle], 
        beliefs: Dict[str, List[str]]
    ) -> List[ProcessedArticle]:
        """Find articles that are semantically relevant to user beliefs"""
        
        if not beliefs:
            return processed_articles
        
        # Flatten all beliefs into a single list
        all_beliefs = []
        for topic_beliefs in beliefs.values():
            all_beliefs.extend(topic_beliefs)
        
        self.logger.info(f"Finding articles relevant to {len(all_beliefs)} beliefs")
        
        # Prepare article texts for similarity search
        article_texts = []
        valid_articles = []
        
        for article in processed_articles:
            if article.embedding is not None:
                text = f"{article.raw_article.title}. {article.raw_article.content[:300]}"
                article_texts.append(text)
                valid_articles.append(article)
        
        if not article_texts:
            return processed_articles
        
        # Find similar articles for each belief
        similarity_start = time.time()
        relevant_articles = set()
        
        for belief in all_beliefs:
            similarity_result = await semantic_embedding_service.find_similar_texts(
                query_text=belief,
                candidate_texts=article_texts,
                top_k=10,
                threshold=0.3
            )
            
            # Add relevant articles to set
            for text, score in similarity_result.matches:
                # Find the corresponding article
                for i, article_text in enumerate(article_texts):
                    if article_text == text:
                        relevant_articles.add(i)
                        # Update semantic score
                        valid_articles[i].semantic_score = max(valid_articles[i].semantic_score, score)
                        break
        
        similarity_time = time.time() - similarity_start
        self.metrics['similarity_search_time'] += similarity_time
        
        self.logger.info(f"Similarity search completed in {similarity_time:.2f}s")
        self.logger.info(f"Found {len(relevant_articles)} relevant articles")
        
        # Return relevant articles, sorted by semantic score
        relevant_processed_articles = [valid_articles[i] for i in relevant_articles]
        relevant_processed_articles.sort(key=lambda x: x.semantic_score, reverse=True)
        
        return relevant_processed_articles
    
    async def _detect_stances(
        self, 
        processed_articles: List[ProcessedArticle], 
        beliefs: Dict[str, List[str]]
    ) -> List[ProcessedArticle]:
        """Step 3: Detect stance of articles toward user beliefs (placeholder)"""
        
        self.logger.info(f"Detecting stances for {len(processed_articles)} articles")
        
        # TODO: Implement stance detection
        # For now, assign mock stances based on semantic score
        for article in processed_articles:
            if article.semantic_score > 0.7:
                article.stance = "support"
                article.stance_confidence = min(article.semantic_score, 0.9)
            elif article.semantic_score < 0.4:
                article.stance = "oppose"
                article.stance_confidence = 0.6
            else:
                article.stance = "neutral"
                article.stance_confidence = 0.5
        
        self.logger.info("Stance detection completed (mock implementation)")
        return processed_articles
    
    async def _classify_ideologies(self, processed_articles: List[ProcessedArticle]) -> List[ProcessedArticle]:
        """Step 4: Classify ideology of articles and sources (placeholder)"""
        
        self.logger.info(f"Classifying ideologies for {len(processed_articles)} articles")
        
        # TODO: Implement ideology classification
        # For now, assign mock ideologies
        ideologies = ["left", "center", "right"]
        for article in processed_articles:
            # Simple hash-based assignment for consistency
            source_hash = hash(article.raw_article.source_domain or "unknown")
            article.ideology = ideologies[source_hash % 3]
        
        self.logger.info("Ideology classification completed (mock implementation)")
        return processed_articles
    
    async def _score_and_rank_articles(
        self, 
        processed_articles: List[ProcessedArticle], 
        bias_slider: float, 
        limit_per_topic: int
    ) -> List[Dict[str, Any]]:
        """Step 5: Score and rank articles based on bias slider"""
        
        self.logger.info(f"Scoring and ranking {len(processed_articles)} articles")
        self.logger.info(f"Bias slider: {bias_slider}")
        
        # Calculate final scores
        for article in processed_articles:
            # Base score from semantic similarity
            base_score = article.semantic_score
            
            # Stance adjustment based on bias slider
            stance_score = 0.5  # neutral
            if article.stance == "support":
                stance_score = bias_slider  # Higher bias = higher score for supporting articles
            elif article.stance == "oppose":
                stance_score = 1.0 - bias_slider  # Higher bias = lower score for opposing articles
            
            # Ideology adjustment (simplified)
            ideology_score = 0.5  # neutral for now
            
            # Final weighted score
            article.final_score = (
                0.4 * base_score + 
                0.4 * stance_score + 
                0.2 * ideology_score
            )
        
        # Sort by final score
        processed_articles.sort(key=lambda x: x.final_score, reverse=True)
        
        # Convert to dictionary format for API response
        final_articles = []
        for article in processed_articles[:limit_per_topic]:
            article_dict = {
                'id': f"{article.raw_article.source_name}_{hash(article.raw_article.url)}",
                'title': article.raw_article.title,
                'content': article.raw_article.content,
                'url': article.raw_article.url,
                'source': article.raw_article.source_domain or article.raw_article.source_name,
                'author': article.raw_article.author,
                'published_at': article.raw_article.published_at.isoformat() if article.raw_article.published_at else None,
                'semantic_score': article.semantic_score,
                'stance': article.stance,
                'stance_confidence': article.stance_confidence,
                'ideology': article.ideology,
                'final_score': article.final_score,
                'pipeline_metadata': {
                    'embedding_model': article.processing_metadata.get('embedding_model', 'unknown'),
                    'embedding_success': article.processing_metadata.get('embedding_success', False),
                    'processing_stage': 'pipeline_complete'
                }
            }
            final_articles.append(article_dict)
        
        self.logger.info(f"Ranked and returned {len(final_articles)} articles")
        return final_articles
    
    def get_pipeline_metrics(self) -> Dict[str, Any]:
        """Get current pipeline metrics"""
        return {
            'metrics': self.metrics.copy(),
            'timestamp': datetime.now().isoformat(),
            'status': 'operational'
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for the pipeline"""
        return {
            'status': 'healthy',
            'pipeline_ready': True,
            'metrics': self.get_pipeline_metrics(),
            'timestamp': datetime.now().isoformat()
        }

# Global instance
aggregation_orchestrator = AggregationOrchestrator() 