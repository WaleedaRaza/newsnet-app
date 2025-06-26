from typing import List, Dict, Tuple
import json
import numpy as np
from services.fusion_engine import FusionEngine

class BiasScoringService:
    def __init__(self):
        self.fusion_engine = FusionEngine()
        self.source_bias_map = self._load_source_bias_map()
    
    def _load_source_bias_map(self) -> Dict[str, Dict]:
        """Load source bias mappings"""
        return {
            "reuters.com": {"bias": "Center", "reliability": 0.9},
            "ap.org": {"bias": "Center", "reliability": 0.9},
            "bbc.com": {"bias": "Center", "reliability": 0.8},
            "cnn.com": {"bias": "Left", "reliability": 0.7},
            "foxnews.com": {"bias": "Right", "reliability": 0.7},
            "msnbc.com": {"bias": "Left", "reliability": 0.7},
            "nytimes.com": {"bias": "Left", "reliability": 0.8},
            "wsj.com": {"bias": "Right", "reliability": 0.8},
            "washingtonpost.com": {"bias": "Left", "reliability": 0.8},
            "usatoday.com": {"bias": "Center", "reliability": 0.7},
            "nbcnews.com": {"bias": "Left", "reliability": 0.7},
            "abcnews.go.com": {"bias": "Center", "reliability": 0.7},
            "cbsnews.com": {"bias": "Center", "reliability": 0.7},
            "npr.org": {"bias": "Left", "reliability": 0.8},
            "pbs.org": {"bias": "Center", "reliability": 0.8},
            "bloomberg.com": {"bias": "Center", "reliability": 0.8},
            "forbes.com": {"bias": "Right", "reliability": 0.7},
            "techcrunch.com": {"bias": "Center", "reliability": 0.7},
            "theverge.com": {"bias": "Center", "reliability": 0.7},
            "ars-technica.com": {"bias": "Center", "reliability": 0.8},
        }
    
    async def calculate_topical_score(self, article_content: str, topic: str) -> float:
        """Calculate topical relevance score using embeddings"""
        try:
            # Use existing fusion engine embeddings
            article_embedding = await self.fusion_engine.embeddings.aembed_query(article_content[:1000])  # Limit content length
            topic_embedding = await self.fusion_engine.embeddings.aembed_query(topic)
            
            # Calculate cosine similarity
            similarity = self._cosine_similarity(article_embedding, topic_embedding)
            return similarity
        except Exception as e:
            print(f"Error calculating topical score: {e}")
            return 0.5
    
    async def calculate_belief_alignment_score(
        self, 
        article_content: str, 
        beliefs: List[str]
    ) -> float:
        """Calculate belief alignment score using semantic similarity"""
        try:
            if not beliefs:
                return 0.5
            
            # Get embeddings for article and beliefs
            article_embedding = await self.fusion_engine.embeddings.aembed_query(article_content[:1000])
            
            belief_scores = []
            for belief in beliefs:
                belief_embedding = await self.fusion_engine.embeddings.aembed_query(belief)
                similarity = self._cosine_similarity(article_embedding, belief_embedding)
                belief_scores.append(similarity)
            
            # Return average belief alignment score
            return sum(belief_scores) / len(belief_scores)
        except Exception as e:
            print(f"Error calculating belief alignment: {e}")
            return 0.5
    
    def calculate_ideological_score(self, source_domain: str, bias_slider: float) -> float:
        """Calculate ideological proximity score based on source bias and user preference"""
        source_info = self.source_bias_map.get(source_domain, {"bias": "Center", "reliability": 0.5})
        source_bias = source_info["bias"]
        
        # Map bias labels to numerical values
        bias_values = {"Left": 0.0, "Center": 0.5, "Right": 1.0}
        source_bias_value = bias_values.get(source_bias, 0.5)
        
        # Calculate distance from user preference
        distance = abs(bias_slider - source_bias_value)
        
        # Convert distance to score (closer = higher score)
        # For bias=0.0 (challenge me), we want opposite sources
        # For bias=1.0 (prove me right), we want aligned sources
        if bias_slider <= 0.5:
            # Challenge mode: prefer opposite sources
            ideological_score = 1.0 - distance
        else:
            # Affirm mode: prefer aligned sources
            ideological_score = 1.0 - distance
        
        return max(0.0, min(1.0, ideological_score))
    
    def get_source_bias_info(self, source_domain: str) -> Dict:
        """Get bias and reliability information for a source"""
        return self.source_bias_map.get(source_domain, {
            "bias": "Center", 
            "reliability": 0.5
        })
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2) 