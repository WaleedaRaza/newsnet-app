"""
User Belief Fingerprinting Service

This service creates and manages user belief fingerprints - semantic representations
of user beliefs that can be used for personalized content filtering and scoring.

Features:
- Belief vectorization using semantic embeddings
- Ideological proximity calculation
- Source bias scoring
- Personalized content recommendations
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

@dataclass
class BeliefStatement:
    """A single belief statement with metadata"""
    text: str
    category: str  # e.g., 'politics', 'climate', 'healthcare'
    strength: float  # 0.0 to 1.0, how strongly the user holds this belief
    source: str  # 'user_input', 'inferred', 'survey'
    timestamp: datetime
    metadata: Dict[str, Any] = None

@dataclass
class UserBeliefFingerprint:
    """Complete user belief fingerprint"""
    user_id: str
    beliefs: List[BeliefStatement]
    belief_vectors: np.ndarray  # Semantic embeddings of beliefs
    categories: List[str]
    last_updated: datetime
    metadata: Dict[str, Any] = None

@dataclass
class ContentScore:
    """Score for content based on user beliefs"""
    content_id: str
    content_type: str  # 'article', 'source', 'topic'
    proximity_score: float  # 0.0 to 1.0, how close to user beliefs
    stance_alignment: float  # -1.0 to 1.0, stance alignment with beliefs
    overall_score: float  # Combined score
    evidence: List[str]  # Supporting evidence
    metadata: Dict[str, Any] = None

class UserBeliefFingerprintService:
    """
    Service for creating and managing user belief fingerprints
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize sentence transformer for semantic embeddings
        try:
            self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
            self.logger.info("Sentence transformer initialized for belief fingerprinting")
        except Exception as e:
            self.logger.error(f"Failed to initialize sentence transformer: {e}")
            self.sentence_transformer = None
        
        # Belief categories and their weights
        self.category_weights = {
            'politics': 1.0,
            'climate': 0.8,
            'healthcare': 0.8,
            'economy': 0.9,
            'social_issues': 0.9,
            'foreign_policy': 0.7,
            'science': 0.6,
            'religion': 0.5,
            'education': 0.7,
            'technology': 0.6
        }
        
        # Predefined belief templates for common topics
        self.belief_templates = {
            'politics': [
                "Democracy is the best form of government",
                "Government should play a larger role in the economy",
                "Free markets are the best way to organize society",
                "Individual rights are more important than collective welfare",
                "Social programs are necessary for a just society"
            ],
            'climate': [
                "Climate change is primarily caused by human activities",
                "Renewable energy should replace fossil fuels",
                "Economic growth is more important than environmental protection",
                "Government regulation is necessary to address climate change",
                "Individual actions can significantly impact climate change"
            ],
            'healthcare': [
                "Universal healthcare would improve health outcomes",
                "Healthcare should be a right, not a privilege",
                "Private healthcare is more efficient than government-run systems",
                "Healthcare costs are too high in the current system",
                "Preventive care should be prioritized over treatment"
            ]
        }
        
        # Storage for user fingerprints (in production, use database)
        self.user_fingerprints: Dict[str, UserBeliefFingerprint] = {}
        
        self.logger.info("UserBeliefFingerprintService initialized")
    
    async def create_user_fingerprint(
        self, 
        user_id: str, 
        beliefs: List[Dict[str, Any]]
    ) -> UserBeliefFingerprint:
        """
        Create a new user belief fingerprint from belief statements
        
        Args:
            user_id: Unique user identifier
            beliefs: List of belief dictionaries with 'text', 'category', 'strength'
            
        Returns:
            UserBeliefFingerprint object
        """
        if not self.sentence_transformer:
            raise ValueError("Sentence transformer not available")
        
        belief_statements = []
        for belief_data in beliefs:
            belief = BeliefStatement(
                text=belief_data['text'],
                category=belief_data.get('category', 'general'),
                strength=belief_data.get('strength', 0.5),
                source=belief_data.get('source', 'user_input'),
                timestamp=datetime.now(),
                metadata=belief_data.get('metadata', {})
            )
            belief_statements.append(belief)
        
        # Generate semantic embeddings for beliefs
        belief_texts = [belief.text for belief in belief_statements]
        belief_vectors = self.sentence_transformer.encode(belief_texts)
        
        # Get unique categories
        categories = list(set(belief.category for belief in belief_statements))
        
        fingerprint = UserBeliefFingerprint(
            user_id=user_id,
            beliefs=belief_statements,
            belief_vectors=belief_vectors,
            categories=categories,
            last_updated=datetime.now()
        )
        
        # Store fingerprint
        self.user_fingerprints[user_id] = fingerprint
        
        self.logger.info(f"Created belief fingerprint for user {user_id} with {len(belief_statements)} beliefs")
        return fingerprint
    
    async def update_user_fingerprint(
        self, 
        user_id: str, 
        new_beliefs: List[Dict[str, Any]]
    ) -> UserBeliefFingerprint:
        """
        Update an existing user belief fingerprint
        
        Args:
            user_id: User identifier
            new_beliefs: New belief statements to add/update
            
        Returns:
            Updated UserBeliefFingerprint
        """
        if user_id not in self.user_fingerprints:
            return await self.create_user_fingerprint(user_id, new_beliefs)
        
        fingerprint = self.user_fingerprints[user_id]
        
        # Add new beliefs
        for belief_data in new_beliefs:
            belief = BeliefStatement(
                text=belief_data['text'],
                category=belief_data.get('category', 'general'),
                strength=belief_data.get('strength', 0.5),
                source=belief_data.get('source', 'user_input'),
                timestamp=datetime.now(),
                metadata=belief_data.get('metadata', {})
            )
            fingerprint.beliefs.append(belief)
        
        # Regenerate embeddings
        belief_texts = [belief.text for belief in fingerprint.beliefs]
        fingerprint.belief_vectors = self.sentence_transformer.encode(belief_texts)
        fingerprint.categories = list(set(belief.category for belief in fingerprint.beliefs))
        fingerprint.last_updated = datetime.now()
        
        self.logger.info(f"Updated belief fingerprint for user {user_id}")
        return fingerprint
    
    async def score_content_for_user(
        self, 
        user_id: str, 
        content_text: str,
        content_metadata: Dict[str, Any] = None
    ) -> ContentScore:
        """
        Score content based on user's belief fingerprint
        
        Args:
            user_id: User identifier
            content_text: Text content to score
            content_metadata: Additional content metadata
            
        Returns:
            ContentScore with proximity and alignment scores
        """
        if user_id not in self.user_fingerprints:
            raise ValueError(f"No belief fingerprint found for user {user_id}")
        
        fingerprint = self.user_fingerprints[user_id]
        
        # Encode content
        content_vector = self.sentence_transformer.encode([content_text])[0]
        
        # Calculate proximity scores for each belief
        proximity_scores = []
        stance_alignments = []
        evidence = []
        
        for i, belief in enumerate(fingerprint.beliefs):
            belief_vector = fingerprint.belief_vectors[i]
            
            # Calculate cosine similarity
            similarity = self._cosine_similarity(content_vector, belief_vector)
            
            # Weight by belief strength and category importance
            category_weight = self.category_weights.get(belief.category, 0.5)
            weighted_similarity = similarity * belief.strength * category_weight
            
            proximity_scores.append(weighted_similarity)
            
            # Estimate stance alignment (simplified - in practice, use stance detection)
            if similarity > 0.7:
                stance_alignments.append(1.0)  # Strong support
                evidence.append(f"Strong alignment with: {belief.text[:50]}...")
            elif similarity > 0.5:
                stance_alignments.append(0.5)  # Moderate support
                evidence.append(f"Moderate alignment with: {belief.text[:50]}...")
            elif similarity < 0.3:
                stance_alignments.append(-0.5)  # Opposition
                evidence.append(f"Opposition to: {belief.text[:50]}...")
            else:
                stance_alignments.append(0.0)  # Neutral
        
        # Calculate overall scores
        avg_proximity = np.mean(proximity_scores) if proximity_scores else 0.0
        avg_stance_alignment = np.mean(stance_alignments) if stance_alignments else 0.0
        
        # Combined score (weighted average)
        overall_score = (0.6 * avg_proximity) + (0.4 * (avg_stance_alignment + 1) / 2)
        
        return ContentScore(
            content_id=content_metadata.get('id', 'unknown'),
            content_type=content_metadata.get('type', 'article'),
            proximity_score=avg_proximity,
            stance_alignment=avg_stance_alignment,
            overall_score=overall_score,
            evidence=evidence[:3],  # Top 3 pieces of evidence
            metadata={
                'belief_scores': dict(zip([b.text[:30] for b in fingerprint.beliefs], proximity_scores)),
                'categories_covered': list(set(b.category for b in fingerprint.beliefs if any(s > 0.5 for s in proximity_scores)))
            }
        )
    
    async def get_personalized_recommendations(
        self, 
        user_id: str, 
        content_list: List[Dict[str, Any]],
        limit: int = 10
    ) -> List[Tuple[Dict[str, Any], ContentScore]]:
        """
        Get personalized content recommendations for a user
        
        Args:
            user_id: User identifier
            content_list: List of content items to rank
            limit: Maximum number of recommendations
            
        Returns:
            List of (content, score) tuples, sorted by relevance
        """
        scored_content = []
        
        for content in content_list:
            try:
                score = await self.score_content_for_user(
                    user_id, 
                    content.get('text', ''),
                    content
                )
                scored_content.append((content, score))
            except Exception as e:
                self.logger.warning(f"Failed to score content: {e}")
                continue
        
        # Sort by overall score (descending)
        scored_content.sort(key=lambda x: x[1].overall_score, reverse=True)
        
        return scored_content[:limit]
    
    async def analyze_user_beliefs(
        self, 
        user_id: str
    ) -> Dict[str, Any]:
        """
        Analyze user beliefs and provide insights
        
        Args:
            user_id: User identifier
            
        Returns:
            Analysis results
        """
        if user_id not in self.user_fingerprints:
            raise ValueError(f"No belief fingerprint found for user {user_id}")
        
        fingerprint = self.user_fingerprints[user_id]
        
        # Category analysis
        category_counts = {}
        category_strengths = {}
        
        for belief in fingerprint.beliefs:
            category = belief.category
            category_counts[category] = category_counts.get(category, 0) + 1
            category_strengths[category] = category_strengths.get(category, 0) + belief.strength
        
        # Calculate average strengths
        for category in category_strengths:
            category_strengths[category] /= category_counts[category]
        
        # Belief diversity (using vector similarity)
        belief_diversity = self._calculate_belief_diversity(fingerprint.belief_vectors)
        
        return {
            'user_id': user_id,
            'total_beliefs': len(fingerprint.beliefs),
            'categories': fingerprint.categories,
            'category_distribution': category_counts,
            'category_strengths': category_strengths,
            'belief_diversity': belief_diversity,
            'last_updated': fingerprint.last_updated.isoformat(),
            'recommendations': {
                'strongest_category': max(category_strengths.items(), key=lambda x: x[1])[0] if category_strengths else None,
                'most_diverse_category': max(category_counts.items(), key=lambda x: x[1])[0] if category_counts else None,
                'suggested_categories': [cat for cat in self.category_weights.keys() if cat not in fingerprint.categories]
            }
        }
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def _calculate_belief_diversity(self, belief_vectors: np.ndarray) -> float:
        """Calculate diversity of beliefs (lower = more diverse)"""
        if len(belief_vectors) < 2:
            return 1.0
        
        # Calculate average pairwise similarity
        similarities = []
        for i in range(len(belief_vectors)):
            for j in range(i + 1, len(belief_vectors)):
                similarity = self._cosine_similarity(belief_vectors[i], belief_vectors[j])
                similarities.append(similarity)
        
        return np.mean(similarities) if similarities else 0.0
    
    async def get_belief_templates(self, categories: List[str] = None) -> Dict[str, List[str]]:
        """Get belief templates for specified categories"""
        if categories is None:
            return self.belief_templates
        
        return {cat: self.belief_templates.get(cat, []) for cat in categories}
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for the service"""
        return {
            'service': 'UserBeliefFingerprintService',
            'status': 'healthy',
            'sentence_transformer_available': self.sentence_transformer is not None,
            'users_registered': len(self.user_fingerprints),
            'categories_supported': list(self.category_weights.keys()),
            'timestamp': datetime.now().isoformat()
        }

# Global instance
user_belief_fingerprint_service = UserBeliefFingerprintService() 