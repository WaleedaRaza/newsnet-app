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
    """Advanced article aggregator with NLP-powered analysis"""
    
    def __init__(self):
        self.retrieval_service = ArticleRetrievalService()
        self.bias_scoring_service = BiasScoringService()
        self.nlp_service = NLPService()
        logger.info("ArticleAggregator initialized with NLP capabilities")
    
    def _convert_raw_article_to_model(self, raw_article: Dict) -> Article:
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
                topics=[],  # Will be extracted by NLP
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
    
    async def aggregate_articles(
        self,
        topics: List[str],
        beliefs: Dict[str, List[str]],
        bias_slider: float,
        limit_per_topic: int = 10,
        db: Session = None
    ) -> List[Article]:
        """Aggregate articles with advanced NLP analysis"""
        
        logger.info(f"Aggregating articles for topics: {topics}")
        logger.info(f"User bias setting: {bias_slider}")
        
        try:
            # Step 1: Retrieve articles for each topic
            all_articles = []
            for topic in topics:
                raw_articles = await self.retrieval_service.fetch_articles_for_topic(
                    topic, limit=limit_per_topic * 2  # Get more for filtering
                )
                
                # Convert raw articles to Article objects
                for raw_article in raw_articles:
                    article = self._convert_raw_article_to_model(raw_article)
                    if article:
                        all_articles.append(article)
            
            if not all_articles:
                logger.warning("No articles retrieved")
                return []
            
            logger.info(f"Retrieved {len(all_articles)} articles for analysis")
            
            # Step 2: Perform advanced NLP analysis on each article
            analyzed_articles = []
            for article in all_articles:
                try:
                    # Combine title and content for analysis
                    full_text = f"{article.title} {article.content}"
                    
                    # Perform NLP analysis
                    nlp_analysis = await self._analyze_article_nlp(full_text)
                    
                    # Calculate belief alignment using NLP
                    belief_alignment = await self._calculate_belief_alignment(
                        full_text, beliefs, nlp_analysis
                    )
                    
                    # Calculate ideological proximity
                    ideological_score = await self._calculate_ideological_proximity(
                        nlp_analysis, beliefs, bias_slider
                    )
                    
                    # Enhanced topical relevance with NLP
                    topical_score = await self._calculate_enhanced_topical_relevance(
                        full_text, topic, nlp_analysis
                    )
                    
                    # Calculate final score with NLP insights
                    final_score = self._calculate_final_score_with_nlp(
                        topical_score=topical_score,
                        belief_alignment=belief_alignment,
                        ideological_score=ideological_score,
                        bias_slider=bias_slider,
                        nlp_analysis=nlp_analysis
                    )
                    
                    # Update article with NLP analysis
                    article.topical_score = topical_score
                    article.belief_alignment_score = belief_alignment
                    article.ideological_score = ideological_score
                    article.final_score = final_score
                    
                    # Add NLP metadata
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
            
            # Step 3: Sort by final score and apply bias filtering
            analyzed_articles.sort(key=lambda x: x.final_score, reverse=True)
            
            # Apply bias-aware filtering
            filtered_articles = self._apply_bias_filtering(
                analyzed_articles, bias_slider, limit_per_topic
            )
            
            logger.info(f"Returning {len(filtered_articles)} articles after NLP analysis")
            return filtered_articles
            
        except Exception as e:
            logger.error(f"Error in article aggregation: {e}")
            return []
    
    async def _analyze_article_nlp(self, text: str) -> Dict:
        """Perform comprehensive NLP analysis on article text"""
        try:
            # Sentiment analysis
            sentiment = self.nlp_service.analyze_article_sentiment(text)
            
            # Bias detection
            bias = self.nlp_service.detect_bias(text)
            
            # Topic extraction
            topics = self.nlp_service.extract_topics(text, num_topics=3)
            
            # Semantic features
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
    
    async def _calculate_belief_alignment(
        self, 
        article_text: str, 
        user_beliefs: Dict[str, List[str]], 
        nlp_analysis: Dict
    ) -> float:
        """Calculate belief alignment using semantic similarity"""
        try:
            if not user_beliefs:
                return 0.5
            
            # Get user beliefs as text
            all_beliefs = []
            for topic, beliefs in user_beliefs.items():
                all_beliefs.extend(beliefs)
            
            if not all_beliefs:
                return 0.5
            
            # Calculate semantic similarity between article and beliefs
            similarities = []
            for belief in all_beliefs:
                similarity = self.nlp_service.calculate_semantic_similarity(
                    article_text, belief
                )
                similarities.append(similarity)
            
            # Return average similarity
            return sum(similarities) / len(similarities) if similarities else 0.5
            
        except Exception as e:
            logger.error(f"Error calculating belief alignment: {e}")
            return 0.5
    
    async def _calculate_ideological_proximity(
        self, 
        nlp_analysis: Dict, 
        user_beliefs: Dict[str, List[str]], 
        bias_slider: float
    ) -> float:
        """Calculate ideological proximity using NLP analysis"""
        try:
            # Get bias analysis
            bias_analysis = nlp_analysis.get('bias', {})
            bias_direction = bias_analysis.get('bias_direction', 'neutral')
            bias_score = bias_analysis.get('overall_bias_score', 0.3)
            
            # Analyze user beliefs for ideological positioning
            belief_analysis = self.nlp_service.analyze_user_beliefs(user_beliefs)
            
            # Calculate ideological alignment
            if bias_direction == 'left' and bias_slider < 0.5:
                # User prefers left-leaning content, article is left-leaning
                alignment = 1.0 - bias_slider
            elif bias_direction == 'right' and bias_slider > 0.5:
                # User prefers right-leaning content, article is right-leaning
                alignment = bias_slider
            else:
                # Mismatch or neutral
                alignment = 0.5
            
            # Adjust based on bias intensity
            intensity_factor = bias_score * 0.5 + 0.5
            
            return alignment * intensity_factor
            
        except Exception as e:
            logger.error(f"Error calculating ideological proximity: {e}")
            return 0.5
    
    async def _calculate_enhanced_topical_relevance(
        self, 
        article_text: str, 
        target_topic: str, 
        nlp_analysis: Dict
    ) -> float:
        """Calculate enhanced topical relevance using NLP"""
        try:
            # Get extracted topics
            extracted_topics = nlp_analysis.get('topics', [])
            
            # Calculate similarity with target topic
            topic_similarity = 0.0
            for topic in extracted_topics:
                topic_text = topic.get('main_theme', '')
                if topic_text:
                    similarity = self.nlp_service.calculate_semantic_similarity(
                        target_topic, topic_text
                    )
                    topic_similarity = max(topic_similarity, similarity)
            
            # Base topical score (from original method)
            base_score = self.bias_scoring_service.calculate_topical_relevance(
                article_text, target_topic
            )
            
            # Combine base score with NLP-enhanced score
            enhanced_score = (base_score * 0.6) + (topic_similarity * 0.4)
            
            return min(enhanced_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating enhanced topical relevance: {e}")
            return 0.5
    
    def _calculate_final_score_with_nlp(
        self,
        topical_score: float,
        belief_alignment: float,
        ideological_score: float,
        bias_slider: float,
        nlp_analysis: Dict
    ) -> float:
        """Calculate final score incorporating NLP insights"""
        try:
            # Get NLP insights
            sentiment = nlp_analysis.get('sentiment', {})
            bias = nlp_analysis.get('bias', {})
            
            # Sentiment factor (prefer articles matching user's emotional state)
            sentiment_score = sentiment.get('polarity', 0.0)
            sentiment_factor = 1.0 + (sentiment_score * 0.2)  # ±20% adjustment
            
            # Bias consistency factor
            bias_consistency = 1.0 - bias.get('overall_bias_score', 0.3)
            bias_factor = 0.8 + (bias_consistency * 0.4)  # 0.8-1.2 range
            
            # Calculate weighted score
            base_score = (
                topical_score * 0.3 +
                belief_alignment * 0.3 +
                ideological_score * 0.4
            )
            
            # Apply NLP factors
            final_score = base_score * sentiment_factor * bias_factor
            
            # Normalize to 0-1 range
            return max(0.0, min(1.0, final_score))
            
        except Exception as e:
            logger.error(f"Error calculating final score: {e}")
            return 0.5
    
    def _calculate_text_complexity(self, text: str) -> float:
        """Calculate text complexity score"""
        try:
            words = text.split()
            sentences = text.split('.')
            
            if not words or not sentences:
                return 0.5
            
            avg_sentence_length = len(words) / len(sentences)
            avg_word_length = sum(len(word) for word in words) / len(words)
            
            # Normalize complexity (0-1 scale)
            complexity = (avg_sentence_length / 20.0 + avg_word_length / 8.0) / 2
            return min(complexity, 1.0)
            
        except Exception:
            return 0.5
    
    def _apply_bias_filtering(
        self, 
        articles: List[Article], 
        bias_slider: float, 
        limit_per_topic: int
    ) -> List[Article]:
        """Apply bias-aware filtering to articles"""
        try:
            # Separate articles by bias direction
            left_articles = []
            right_articles = []
            neutral_articles = []
            
            for article in articles:
                bias_direction = article.nlp_metadata.get('bias_analysis', {}).get('bias_direction', 'neutral')
                
                if bias_direction == 'left':
                    left_articles.append(article)
                elif bias_direction == 'right':
                    right_articles.append(article)
                else:
                    neutral_articles.append(article)
            
            # Calculate distribution based on bias slider
            if bias_slider < 0.3:
                # Prefer left-leaning content
                left_ratio = 0.6
                right_ratio = 0.2
                neutral_ratio = 0.2
            elif bias_slider > 0.7:
                # Prefer right-leaning content
                left_ratio = 0.2
                right_ratio = 0.6
                neutral_ratio = 0.2
            else:
                # Balanced distribution
                left_ratio = 0.3
                right_ratio = 0.3
                neutral_ratio = 0.4
            
            # Select articles based on distribution
            selected_articles = []
            
            left_count = int(limit_per_topic * left_ratio)
            right_count = int(limit_per_topic * right_ratio)
            neutral_count = limit_per_topic - left_count - right_count
            
            selected_articles.extend(left_articles[:left_count])
            selected_articles.extend(right_articles[:right_count])
            selected_articles.extend(neutral_articles[:neutral_count])
            
            # Sort by final score
            selected_articles.sort(key=lambda x: x.final_score, reverse=True)
            
            return selected_articles[:limit_per_topic]
            
        except Exception as e:
            logger.error(f"Error in bias filtering: {e}")
            return articles[:limit_per_topic]
    
    async def save_articles_to_db(self, articles: List[Article], db: Session) -> List[Article]:
        """Save articles to database"""
        try:
            for article in articles:
                db.add(article)
            db.commit()
            
            # Refresh articles to get IDs
            for article in articles:
                db.refresh(article)
            
            return articles
        except Exception as e:
            db.rollback()
            print(f"Error saving articles to database: {e}")
            return articles 