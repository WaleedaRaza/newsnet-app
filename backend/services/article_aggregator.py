from typing import List, Dict, Optional
import asyncio
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from db.models import Article, UserBelief
from services.article_retrieval_service import ArticleRetrievalService
from services.bias_scoring_service import BiasScoringService
from services.nlp_service import NLPService
import uuid

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
            
            # Generate a unique ID for the article
            article_id = str(uuid.uuid4())
            
            return Article(
                id=article_id,
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
                final_score=0.0,
                created_at=datetime.now()
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
        """Aggregate articles by category with aggressive bias filtering for extreme viewpoints"""
        
        logger.info(f"Aggregating articles for categories: {categories}")
        logger.info(f"Bias slider setting: {bias_slider}")
        
        try:
            # Step 1: Retrieve articles for each category
            all_articles = []
            for category in categories:
                raw_articles = await self.retrieval_service.fetch_articles_for_category(
                    category, limit=limit_per_category * 3  # Get more for aggressive filtering
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
            
            # Step 2: Perform aggressive analysis on each article
            analyzed_articles = []
            for article in all_articles:
                try:
                    # Combine title and content for analysis
                    full_text = f"{article.title} {article.content}"
                    
                    # Perform aggressive NLP analysis
                    nlp_analysis = await self._analyze_article_nlp(full_text)
                    
                    # Calculate content bias using new aggressive detection
                    content_bias = self.bias_scoring_service.analyze_content_bias(full_text)
                    
                    # Calculate ideological score with new aggressive logic
                    ideological_score = self.bias_scoring_service.calculate_ideological_score(
                        article.source_domain, bias_slider
                    )
                    
                    # Calculate topical relevance
                    topical_score = await self._calculate_category_relevance(
                        full_text, article.topics[0], nlp_analysis
                    )
                    
                    # Calculate belief alignment (placeholder for now)
                    belief_alignment_score = 0.5
                    
                    # Calculate final score with aggressive bias weighting
                    final_score = self._calculate_final_score_aggressive(
                        topical_score=topical_score,
                        belief_alignment=belief_alignment_score,
                        ideological_score=ideological_score,
                        bias_slider=bias_slider,
                        nlp_analysis=nlp_analysis,
                        content_bias=content_bias
                    )
                    
                    # Update article with scores
                    article.topical_score = topical_score
                    article.belief_alignment_score = belief_alignment_score
                    article.ideological_score = ideological_score
                    article.final_score = final_score
                    
                    # Add comprehensive metadata
                    article.nlp_metadata = {
                        'sentiment': nlp_analysis.get('sentiment', {}),
                        'bias_analysis': nlp_analysis.get('bias', {}),
                        'content_bias': content_bias,
                        'topics': nlp_analysis.get('topics', []),
                        'semantic_features': nlp_analysis.get('semantic_features', {}),
                        'extremity_score': content_bias.get('extremity_score', 0.0),
                        'bias_direction': content_bias.get('bias_direction', 'neutral')
                    }
                    
                    analyzed_articles.append(article)
                    
                except Exception as e:
                    logger.error(f"Error analyzing article {article.id}: {e}")
                    continue
            
            # Step 3: Apply aggressive filtering based on bias slider
            filtered_articles = self._apply_aggressive_bias_filtering(
                analyzed_articles, bias_slider, categories, limit_per_category
            )
            
            logger.info(f"Returning {len(filtered_articles)} articles after aggressive bias filtering")
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
    
    def _calculate_final_score_aggressive(
        self,
        topical_score: float,
        belief_alignment: float,
        ideological_score: float,
        bias_slider: float,
        nlp_analysis: Dict,
        content_bias: Dict
    ) -> float:
        """Calculate final score for article ranking with aggressive bias weighting"""
        try:
            # Aggressive weighting for debate-focused users
            weights = {
                'topical': 0.3,  # Reduced weight
                'belief_alignment': 0.1,
                'ideological': 0.4,  # Increased weight for bias
                'extremity': 0.2  # New weight for extreme content
            }
            
            # Calculate extremity score from content bias
            extremity_score = content_bias.get('extremity_score', 0.0)
            
            # Calculate quality score based on NLP analysis
            quality_score = 0.5
            semantic_features = nlp_analysis.get('semantic_features', {})
            if semantic_features.get('word_count', 0) > 200:
                quality_score = 0.8
            elif semantic_features.get('word_count', 0) > 100:
                quality_score = 0.6
            
            # Calculate base weighted score
            base_score = (
                topical_score * weights['topical'] +
                belief_alignment * weights['belief_alignment'] +
                ideological_score * weights['ideological'] +
                extremity_score * weights['extremity']
            )
            
            # Apply bias slider adjustments
            if bias_slider <= 0.3:  # Challenge me - want opposite extreme views
                # Boost articles that strongly oppose user's likely position
                if content_bias.get('bias_direction') in ['far_right', 'pro_trump']:
                    base_score *= 1.5  # Boost right-wing content for left users
                elif content_bias.get('bias_direction') in ['far_left', 'anti_trump']:
                    base_score *= 1.5  # Boost left-wing content for right users
                    
            elif bias_slider >= 0.7:  # Prove me right - want aligned extreme views
                # Boost articles that strongly support user's likely position
                if content_bias.get('bias_direction') in ['far_left', 'anti_trump']:
                    base_score *= 1.5  # Boost left-wing content for left users
                elif content_bias.get('bias_direction') in ['far_right', 'pro_trump']:
                    base_score *= 1.5  # Boost right-wing content for right users
            
            # Apply extremity boost for extreme bias settings
            if bias_slider <= 0.2 or bias_slider >= 0.8:
                # User wants very extreme views, heavily boost extreme content
                if extremity_score > 0.5:
                    base_score *= 2.0
            
            return min(base_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating aggressive final score: {e}")
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
    
    def _apply_aggressive_bias_filtering(
        self, 
        articles: List[Article], 
        bias_slider: float, 
        categories: List[str], 
        limit_per_category: int
    ) -> List[Article]:
        """Apply aggressive bias filtering to articles for extreme viewpoints"""
        try:
            # First, sort all articles by final score
            articles.sort(key=lambda x: x.final_score, reverse=True)
            
            # Apply bias-based filtering
            filtered_articles = []
            
            for article in articles:
                content_bias = article.nlp_metadata.get('content_bias', {})
                bias_direction = content_bias.get('bias_direction', 'neutral')
                extremity_score = content_bias.get('extremity_score', 0.0)
                
                # Aggressive filtering based on bias slider
                if bias_slider <= 0.3:  # Challenge me - want opposite views
                    if bias_slider <= 0.1:  # Far left user
                        # Want far-right content
                        if bias_direction in ['far_right', 'pro_trump'] and extremity_score > 0.3:
                            filtered_articles.append(article)
                    elif bias_slider <= 0.2:  # Left user
                        # Want right content
                        if bias_direction in ['far_right', 'pro_trump', 'right'] and extremity_score > 0.2:
                            filtered_articles.append(article)
                    else:  # Center-left user
                        # Want center-right content
                        if bias_direction in ['right', 'pro_trump'] and extremity_score > 0.1:
                            filtered_articles.append(article)
                            
                elif bias_slider >= 0.7:  # Prove me right - want aligned views
                    if bias_slider >= 0.9:  # Far right user
                        # Want far-right content
                        if bias_direction in ['far_right', 'pro_trump'] and extremity_score > 0.3:
                            filtered_articles.append(article)
                    elif bias_slider >= 0.8:  # Right user
                        # Want right content
                        if bias_direction in ['far_right', 'pro_trump', 'right'] and extremity_score > 0.2:
                            filtered_articles.append(article)
                    else:  # Center-right user
                        # Want center-right content
                        if bias_direction in ['right', 'pro_trump'] and extremity_score > 0.1:
                            filtered_articles.append(article)
                            
                else:  # Center - want moderate content
                    if extremity_score < 0.4 and bias_direction == 'neutral':
                        filtered_articles.append(article)
            
            # If we don't have enough filtered articles, add some based on final score
            if len(filtered_articles) < limit_per_category * len(categories):
                remaining_articles = [a for a in articles if a not in filtered_articles]
                filtered_articles.extend(remaining_articles[:limit_per_category * len(categories) - len(filtered_articles)])
            
            # Apply category-based distribution
            final_articles = self._distribute_by_category(filtered_articles, categories, limit_per_category)
            
            return final_articles
            
        except Exception as e:
            logger.error(f"Error in aggressive bias filtering: {e}")
            return articles[:limit_per_category * len(categories)]
    
    def _distribute_by_category(
        self, 
        articles: List[Article], 
        categories: List[str], 
        limit_per_category: int
    ) -> List[Article]:
        """Distribute articles by category while maintaining bias preferences"""
        try:
            # Group articles by category
            articles_by_category = {}
            for article in articles:
                category = article.topics[0] if article.topics else 'unknown'
                if category not in articles_by_category:
                    articles_by_category[category] = []
                articles_by_category[category].append(article)
            
            # Take top articles from each category
            final_articles = []
            for category in categories:
                if category in articles_by_category:
                    category_articles = articles_by_category[category]
                    # Sort by final score and take top articles
                    category_articles.sort(key=lambda x: x.final_score, reverse=True)
                    final_articles.extend(category_articles[:limit_per_category])
            
            return final_articles
            
        except Exception as e:
            logger.error(f"Error in category distribution: {e}")
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