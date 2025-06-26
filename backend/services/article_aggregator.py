from typing import List, Dict, Optional
import asyncio
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from db.models import Article, UserBelief
from services.article_retrieval_service import ArticleRetrievalService
from services.bias_scoring_service import BiasScoringService
from services.nlp_service import NLPService

logger = logging.getLogger(__name__)

class ArticleAggregator:
    """Advanced article aggregator with category-based filtering and bias-aware scoring"""
    
    def __init__(self):
        self.retrieval_service = ArticleRetrievalService()
        self.bias_scoring_service = BiasScoringService()
        self.nlp_service = NLPService()
        logger.info("ArticleAggregator initialized with category-based filtering")
    
    def _convert_raw_article_to_model(self, raw_article: Dict, category: str) -> Article:
        """Convert raw NewsAPI article to Article model"""
        try:
            # Parse published date
            published_at = datetime.now()
            if raw_article.get('publishedAt'):
                try:
                    published_at = datetime.fromisoformat(raw_article['publishedAt'].replace('Z', '+00:00'))
                except:
                    pass
            
            # Extract source information
            source_name = raw_article.get('source', {}).get('name', 'Unknown')
            source_domain = self.retrieval_service.extract_domain_from_url(raw_article.get('url', ''))
            
            # Clean content
            content = self.retrieval_service.clean_article_content(raw_article.get('content', ''))
            
            return Article(
                title=raw_article.get('title', ''),
                content=content,
                url=raw_article.get('url', ''),
                source_name=source_name,
                source_domain=source_domain,
                source_bias=None,  # Will be determined by bias scoring
                source_reliability=0.5,  # Default value
                topics=[category],  # Use category as topic for now
                published_at=published_at,
                embedding_id=None,
                topical_score=0.0,
                belief_alignment_score=0.0,
                ideological_score=0.0,
                final_score=0.0
            )
        except Exception as e:
            logger.error(f"Error converting raw article: {e}")
            return None
    
    async def aggregate_articles_by_category(
        self,
        categories: List[str],
        bias_slider: float = 0.5,
        limit_per_category: int = 10,
        db: Session = None
    ) -> List[Article]:
        """Aggregate articles by category with basic bias filtering"""
        
        logger.info(f"Aggregating articles for categories: {categories}")
        logger.info(f"Bias slider setting: {bias_slider}")
        
        try:
            # Step 1: Retrieve articles for each category
            all_articles = []
            for category in categories:
                raw_articles = await self.retrieval_service.fetch_articles_for_category(
                    category, limit=limit_per_category * 2  # Get more for filtering
                )
                
                # Convert raw articles to Article objects
                for raw_article in raw_articles:
                    article = self._convert_raw_article_to_model(raw_article, category)
                    if article:
                        all_articles.append(article)
            
            if not all_articles:
                logger.warning("No articles retrieved")
                return []
            
            logger.info(f"Retrieved {len(all_articles)} articles for analysis")
            
            # Step 2: Perform basic analysis on each article
            analyzed_articles = []
            for article in all_articles:
                try:
                    # Combine title and content for analysis
                    full_text = f"{article.title} {article.content}"
                    
                    # Perform basic NLP analysis
                    nlp_analysis = await self._analyze_article_nlp(full_text)
                    
                    # Calculate basic topical relevance
                    topical_score = await self._calculate_category_relevance(
                        full_text, article.topics[0], nlp_analysis
                    )
                    
                    # For now, set other scores to neutral values
                    # These will be enhanced in the next iteration with bias-based filtering
                    belief_alignment_score = 0.5  # Neutral for now
                    ideological_score = 0.5  # Neutral for now
                    
                    # Calculate final score (mostly based on topical relevance for now)
                    final_score = self._calculate_final_score(
                        topical_score=topical_score,
                        belief_alignment=belief_alignment_score,
                        ideological_score=ideological_score,
                        bias_slider=bias_slider,
                        nlp_analysis=nlp_analysis
                    )
                    
                    # Update article with scores
                    article.topical_score = topical_score
                    article.belief_alignment_score = belief_alignment_score
                    article.ideological_score = ideological_score
                    article.final_score = final_score
                    
                    # Add basic NLP metadata
                    article.nlp_metadata = {
                        'sentiment': nlp_analysis.get('sentiment', {}),
                        'bias_analysis': nlp_analysis.get('bias', {}),
                        'topics': nlp_analysis.get('topics', []),
                        'semantic_features': nlp_analysis.get('semantic_features', {})
                    }
                    
                    analyzed_articles.append(article)
                    
                except Exception as e:
                    logger.error(f"Error analyzing article {article.id}: {e}")
                    continue
            
            # Step 3: Sort by final score and apply basic filtering
            analyzed_articles.sort(key=lambda x: x.final_score, reverse=True)
            
            # Apply basic category-based filtering
            filtered_articles = self._apply_category_filtering(
                analyzed_articles, categories, limit_per_category
            )
            
            logger.info(f"Returning {len(filtered_articles)} articles after category filtering")
            return filtered_articles
            
        except Exception as e:
            logger.error(f"Error in article aggregation: {e}")
            return []
    
    async def _analyze_article_nlp(self, text: str) -> Dict:
        """Perform basic NLP analysis on article text"""
        try:
            # Basic sentiment analysis
            sentiment = self.nlp_service.analyze_article_sentiment(text)
            
            # Basic bias detection
            bias = self.nlp_service.detect_bias(text)
            
            # Basic topic extraction
            topics = self.nlp_service.extract_topics(text, num_topics=3)
            
            # Basic semantic features
            semantic_features = {
                'text_length': len(text),
                'sentence_count': len(text.split('.')),
                'word_count': len(text.split()),
                'complexity_score': self._calculate_text_complexity(text)
            }
            
            return {
                'sentiment': sentiment,
                'bias': bias,
                'topics': topics,
                'semantic_features': semantic_features
            }
            
        except Exception as e:
            logger.error(f"Error in NLP analysis: {e}")
            return {
                'sentiment': {'sentiment': 'NEUTRAL', 'confidence': 0.5},
                'bias': {'overall_bias_score': 0.3, 'bias_direction': 'neutral'},
                'topics': [],
                'semantic_features': {}
            }
    
    async def _calculate_category_relevance(
        self, 
        article_text: str, 
        category: str, 
        nlp_analysis: Dict
    ) -> float:
        """Calculate how relevant an article is to its category"""
        try:
            # Get category keywords
            category_config = self.retrieval_service.category_mappings.get(category, {})
            category_keywords = category_config.get('keywords', [])
            
            if not category_keywords:
                return 0.5  # Default relevance
            
            # Count keyword matches in article text
            text_lower = article_text.lower()
            matches = sum(1 for keyword in category_keywords if keyword.lower() in text_lower)
            
            # Calculate relevance score (0-1)
            relevance_score = min(matches / len(category_keywords), 1.0)
            
            # Boost score if article has good semantic features
            semantic_features = nlp_analysis.get('semantic_features', {})
            if semantic_features.get('word_count', 0) > 100:  # Good length
                relevance_score *= 1.1
            
            return min(relevance_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating category relevance: {e}")
            return 0.5
    
    def _calculate_final_score(
        self,
        topical_score: float,
        belief_alignment: float,
        ideological_score: float,
        bias_slider: float,
        nlp_analysis: Dict
    ) -> float:
        """Calculate final score for article ranking"""
        try:
            # For now, mostly weight by topical relevance
            # This will be enhanced in the next iteration with bias-based filtering
            weights = {
                'topical': 0.7,
                'belief_alignment': 0.1,  # Low weight for now
                'ideological': 0.1,  # Low weight for now
                'quality': 0.1
            }
            
            # Calculate quality score based on NLP analysis
            quality_score = 0.5
            semantic_features = nlp_analysis.get('semantic_features', {})
            if semantic_features.get('word_count', 0) > 200:
                quality_score = 0.8
            elif semantic_features.get('word_count', 0) > 100:
                quality_score = 0.6
            
            # Calculate weighted final score
            final_score = (
                topical_score * weights['topical'] +
                belief_alignment * weights['belief_alignment'] +
                ideological_score * weights['ideological'] +
                quality_score * weights['quality']
            )
            
            return min(final_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating final score: {e}")
            return 0.5
    
    def _calculate_text_complexity(self, text: str) -> float:
        """Calculate text complexity score"""
        try:
            words = text.split()
            if not words:
                return 0.0
            
            # Simple complexity based on average word length
            avg_word_length = sum(len(word) for word in words) / len(words)
            complexity = min(avg_word_length / 8.0, 1.0)  # Normalize to 0-1
            
            return complexity
        except:
            return 0.5
    
    def _apply_category_filtering(
        self, 
        articles: List[Article], 
        categories: List[str], 
        limit_per_category: int
    ) -> List[Article]:
        """Apply category-based filtering to articles"""
        try:
            filtered_articles = []
            
            # Group articles by category
            articles_by_category = {}
            for article in articles:
                category = article.topics[0] if article.topics else 'unknown'
                if category not in articles_by_category:
                    articles_by_category[category] = []
                articles_by_category[category].append(article)
            
            # Take top articles from each category
            for category in categories:
                if category in articles_by_category:
                    category_articles = articles_by_category[category]
                    # Sort by final score and take top articles
                    category_articles.sort(key=lambda x: x.final_score, reverse=True)
                    filtered_articles.extend(category_articles[:limit_per_category])
            
            return filtered_articles
            
        except Exception as e:
            logger.error(f"Error in category filtering: {e}")
            return articles[:limit_per_category * len(categories)]
    
    async def save_articles_to_db(self, articles: List[Article], db: Session) -> List[Article]:
        """Save articles to database"""
        try:
            saved_articles = []
            for article in articles:
                db.add(article)
                saved_articles.append(article)
            
            db.commit()
            logger.info(f"Saved {len(saved_articles)} articles to database")
            return saved_articles
            
        except Exception as e:
            logger.error(f"Error saving articles to database: {e}")
            db.rollback()
            return [] 