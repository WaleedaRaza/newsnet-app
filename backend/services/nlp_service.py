import numpy as np
from typing import List, Dict, Tuple, Optional
import re
from collections import Counter
import json
import logging
from datetime import datetime

# NLP Libraries
try:
    from transformers import pipeline, AutoTokenizer, AutoModel
    from sentence_transformers import SentenceTransformer
    import torch
    from textblob import TextBlob
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.decomposition import LatentDirichletAllocation
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.stem import WordNetLemmatizer
    NLP_AVAILABLE = True
except ImportError:
    NLP_AVAILABLE = False
    logging.warning("NLP libraries not available. Install with: pip install transformers sentence-transformers textblob scikit-learn nltk")

class NLPService:
    """Advanced NLP service for news analysis and bias detection"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        if not NLP_AVAILABLE:
            self.logger.error("NLP libraries not available")
            return
            
        try:
            # Initialize models
            self._initialize_models()
            self.logger.info("NLP Service initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize NLP Service: {e}")
    
    def _initialize_models(self):
        """Initialize all NLP models"""
        # Sentiment analysis
        self.sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-roberta-base-sentiment-latest",
            device=0 if torch.cuda.is_available() else -1
        )
        
        # Sentence embeddings for semantic similarity
        self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Topic modeling
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        # LDA for topic modeling
        self.lda_model = LatentDirichletAllocation(
            n_components=10,
            random_state=42,
            max_iter=10
        )
        
        # NLTK setup
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('wordnet', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
        except:
            pass
        
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        
        # Load bias indicators
        self._load_bias_indicators()
    
    def _load_bias_indicators(self):
        """Load bias indicators and political leanings"""
        self.bias_indicators = {
            'left_indicators': [
                'progressive', 'liberal', 'democratic', 'socialist', 'equality',
                'climate change', 'renewable energy', 'universal healthcare',
                'minimum wage', 'workers rights', 'social justice'
            ],
            'right_indicators': [
                'conservative', 'republican', 'free market', 'deregulation',
                'tax cuts', 'border security', 'traditional values',
                'second amendment', 'pro-life', 'small government'
            ],
            'emotional_indicators': [
                'outrageous', 'shocking', 'devastating', 'amazing', 'incredible',
                'terrible', 'wonderful', 'horrible', 'fantastic', 'disgusting'
            ],
            'certainty_indicators': [
                'definitely', 'certainly', 'absolutely', 'clearly', 'obviously',
                'undoubtedly', 'without doubt', 'proven', 'fact', 'truth'
            ]
        }
    
    def analyze_article_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of article text"""
        if not NLP_AVAILABLE:
            return self._fallback_sentiment_analysis(text)
        
        try:
            # Clean text
            clean_text = self._preprocess_text(text)
            
            # Get sentiment scores
            sentiment_result = self.sentiment_analyzer(clean_text[:512])[0]
            
            # Additional sentiment analysis with TextBlob
            blob = TextBlob(clean_text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            return {
                'sentiment': sentiment_result['label'],
                'confidence': sentiment_result['score'],
                'polarity': polarity,
                'subjectivity': subjectivity,
                'emotional_intensity': abs(polarity),
                'is_emotional': subjectivity > 0.5
            }
        except Exception as e:
            self.logger.error(f"Sentiment analysis failed: {e}")
            return self._fallback_sentiment_analysis(text)
    
    def detect_bias(self, text: str) -> Dict:
        """Detect bias in article text"""
        if not NLP_AVAILABLE:
            return self._fallback_bias_detection(text)
        
        try:
            clean_text = self._preprocess_text(text)
            
            # Count bias indicators
            bias_scores = self._count_bias_indicators(clean_text)
            
            # Analyze language patterns
            language_patterns = self._analyze_language_patterns(clean_text)
            
            # Check for loaded language
            loaded_language = self._detect_loaded_language(clean_text)
            
            # Calculate overall bias score
            total_bias_score = (
                bias_scores['political_bias'] * 0.4 +
                language_patterns['emotional_intensity'] * 0.3 +
                loaded_language['score'] * 0.3
            )
            
            return {
                'overall_bias_score': total_bias_score,
                'political_bias': bias_scores['political_bias'],
                'emotional_bias': language_patterns['emotional_intensity'],
                'loaded_language': loaded_language['score'],
                'bias_direction': bias_scores['bias_direction'],
                'indicators': bias_scores['indicators'],
                'loaded_terms': loaded_language['terms']
            }
        except Exception as e:
            self.logger.error(f"Bias detection failed: {e}")
            return self._fallback_bias_detection(text)
    
    def extract_topics(self, text: str, num_topics: int = 5) -> List[Dict]:
        """Extract main topics from text using LDA"""
        if not NLP_AVAILABLE:
            return self._fallback_topic_extraction(text)
        
        try:
            # Preprocess text
            sentences = sent_tokenize(text)
            processed_sentences = [self._preprocess_text(sent) for sent in sentences]
            
            # Create TF-IDF matrix
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(processed_sentences)
            
            # Apply LDA
            lda_output = self.lda_model.fit_transform(tfidf_matrix)
            
            # Extract topics
            feature_names = self.tfidf_vectorizer.get_feature_names_out()
            topics = []
            
            for topic_idx, topic in enumerate(self.lda_model.components_):
                top_words = [feature_names[i] for i in topic.argsort()[-10:]]
                topic_score = np.mean(lda_output[:, topic_idx])
                
                topics.append({
                    'topic_id': topic_idx,
                    'words': top_words,
                    'score': float(topic_score),
                    'main_theme': ' '.join(top_words[:3])
                })
            
            # Sort by score and return top topics
            topics.sort(key=lambda x: x['score'], reverse=True)
            return topics[:num_topics]
            
        except Exception as e:
            self.logger.error(f"Topic extraction failed: {e}")
            return self._fallback_topic_extraction(text)
    
    def calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts"""
        if not NLP_AVAILABLE:
            return self._fallback_similarity(text1, text2)
        
        try:
            # Get embeddings
            embedding1 = self.sentence_transformer.encode(text1)
            embedding2 = self.sentence_transformer.encode(text2)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(
                [embedding1], [embedding2]
            )[0][0]
            
            return float(similarity)
        except Exception as e:
            self.logger.error(f"Semantic similarity failed: {e}")
            return self._fallback_similarity(text1, text2)
    
    def analyze_user_beliefs(self, beliefs: Dict[str, List[str]]) -> Dict:
        """Analyze user beliefs for ideological positioning"""
        if not NLP_AVAILABLE:
            return self._fallback_belief_analysis(beliefs)
        
        try:
            all_beliefs = []
            for topic, belief_list in beliefs.items():
                all_beliefs.extend(belief_list)
            
            # Get embeddings for all beliefs
            belief_embeddings = self.sentence_transformer.encode(all_beliefs)
            
            # Calculate ideological positioning
            ideological_scores = self._calculate_ideological_positioning(belief_embeddings)
            
            # Analyze belief consistency
            consistency_score = self._analyze_belief_consistency(belief_embeddings)
            
            return {
                'ideological_position': ideological_scores,
                'belief_consistency': consistency_score,
                'belief_complexity': len(all_beliefs),
                'topic_coverage': len(beliefs)
            }
        except Exception as e:
            self.logger.error(f"Belief analysis failed: {e}")
            return self._fallback_belief_analysis(beliefs)
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for NLP analysis"""
        # Remove special characters and normalize
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove stop words and lemmatize
        words = word_tokenize(text)
        words = [self.lemmatizer.lemmatize(word) for word in words 
                if word not in self.stop_words and len(word) > 2]
        
        return ' '.join(words)
    
    def _count_bias_indicators(self, text: str) -> Dict:
        """Count bias indicators in text"""
        text_lower = text.lower()
        
        left_count = sum(1 for indicator in self.bias_indicators['left_indicators'] 
                        if indicator in text_lower)
        right_count = sum(1 for indicator in self.bias_indicators['right_indicators'] 
                         if indicator in text_lower)
        emotional_count = sum(1 for indicator in self.bias_indicators['emotional_indicators'] 
                             if indicator in text_lower)
        
        total_indicators = left_count + right_count + emotional_count
        political_bias = (right_count - left_count) / max(total_indicators, 1)
        
        bias_direction = 'neutral'
        if political_bias > 0.2:
            bias_direction = 'right'
        elif political_bias < -0.2:
            bias_direction = 'left'
        
        return {
            'political_bias': abs(political_bias),
            'bias_direction': bias_direction,
            'left_indicators': left_count,
            'right_indicators': right_count,
            'emotional_indicators': emotional_count,
            'indicators': {
                'left': left_count,
                'right': right_count,
                'emotional': emotional_count
            }
        }
    
    def _analyze_language_patterns(self, text: str) -> Dict:
        """Analyze language patterns for bias detection"""
        sentences = sent_tokenize(text)
        
        # Count certainty indicators
        certainty_count = sum(1 for indicator in self.bias_indicators['certainty_indicators'] 
                             if indicator in text.lower())
        
        # Calculate emotional intensity
        emotional_intensity = certainty_count / max(len(sentences), 1)
        
        return {
            'emotional_intensity': min(emotional_intensity, 1.0),
            'certainty_indicators': certainty_count,
            'sentence_count': len(sentences)
        }
    
    def _detect_loaded_language(self, text: str) -> Dict:
        """Detect loaded or emotionally charged language"""
        loaded_terms = []
        text_lower = text.lower()
        
        # Check for loaded terms
        for term in self.bias_indicators['emotional_indicators']:
            if term in text_lower:
                loaded_terms.append(term)
        
        # Calculate loaded language score
        score = len(loaded_terms) / max(len(text.split()), 1)
        
        return {
            'score': min(score, 1.0),
            'terms': loaded_terms,
            'count': len(loaded_terms)
        }
    
    def _calculate_ideological_positioning(self, embeddings: np.ndarray) -> Dict:
        """Calculate ideological positioning from belief embeddings"""
        # This is a simplified version - in production you'd use more sophisticated methods
        mean_embedding = np.mean(embeddings, axis=0)
        
        # Calculate variance to measure ideological spread
        variance = np.var(embeddings, axis=0).mean()
        
        return {
            'ideological_center': mean_embedding.tolist(),
            'ideological_variance': float(variance),
            'positioning_score': float(np.linalg.norm(mean_embedding))
        }
    
    def _analyze_belief_consistency(self, embeddings: np.ndarray) -> float:
        """Analyze consistency of beliefs"""
        if len(embeddings) < 2:
            return 1.0
        
        # Calculate pairwise similarities
        similarities = cosine_similarity(embeddings)
        
        # Get upper triangle (excluding diagonal)
        upper_triangle = similarities[np.triu_indices_from(similarities, k=1)]
        
        # Return mean consistency
        return float(np.mean(upper_triangle))
    
    # Fallback methods for when NLP libraries aren't available
    def _fallback_sentiment_analysis(self, text: str) -> Dict:
        """Simple fallback sentiment analysis"""
        positive_words = ['good', 'great', 'excellent', 'positive', 'happy', 'success']
        negative_words = ['bad', 'terrible', 'negative', 'sad', 'failure', 'problem']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = 'POSITIVE'
        elif negative_count > positive_count:
            sentiment = 'NEGATIVE'
        else:
            sentiment = 'NEUTRAL'
        
        return {
            'sentiment': sentiment,
            'confidence': 0.6,
            'polarity': (positive_count - negative_count) / max(len(text.split()), 1),
            'subjectivity': 0.5,
            'emotional_intensity': 0.3,
            'is_emotional': False
        }
    
    def _fallback_bias_detection(self, text: str) -> Dict:
        """Simple fallback bias detection"""
        return {
            'overall_bias_score': 0.3,
            'political_bias': 0.2,
            'emotional_bias': 0.3,
            'loaded_language': 0.2,
            'bias_direction': 'neutral',
            'indicators': {'left': 0, 'right': 0, 'emotional': 0},
            'loaded_terms': []
        }
    
    def _fallback_topic_extraction(self, text: str) -> List[Dict]:
        """Simple fallback topic extraction"""
        words = text.lower().split()
        word_freq = Counter(words)
        top_words = word_freq.most_common(5)
        
        return [{
            'topic_id': 0,
            'words': [word for word, _ in top_words],
            'score': 0.5,
            'main_theme': ' '.join([word for word, _ in top_words[:3]])
        }]
    
    def _fallback_similarity(self, text1: str, text2: str) -> float:
        """Simple fallback similarity calculation"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def _fallback_belief_analysis(self, beliefs: Dict[str, List[str]]) -> Dict:
        """Simple fallback belief analysis"""
        return {
            'ideological_position': {'ideological_center': [], 'ideological_variance': 0.5, 'positioning_score': 0.5},
            'belief_consistency': 0.7,
            'belief_complexity': sum(len(beliefs) for beliefs in beliefs.values()),
            'topic_coverage': len(beliefs)
        }
