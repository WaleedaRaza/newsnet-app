from typing import Literal, Dict, List
import re
from transformers import pipeline
import logging

logger = logging.getLogger(__name__)

class StanceDetector:
    """Detect stance (support/oppose/neutral) of articles toward user beliefs"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._initialize_models()
        self._load_stance_indicators()
    
    def _initialize_models(self):
        """Initialize stance detection models"""
        try:
            # Use zero-shot classification for stance detection
            self.zero_shot_classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=-1  # Use CPU for now
            )
            self.logger.info("Stance detector initialized with BART-MNLI")
        except Exception as e:
            self.logger.error(f"Failed to initialize stance detector: {e}")
            self.zero_shot_classifier = None
    
    def _load_stance_indicators(self):
        """Load stance indicators for rule-based fallback"""
        self.stance_indicators = {
            "support": [
                # Agreement indicators
                "supports", "agrees", "backs", "endorses", "approves", "favors",
                "advocates", "champions", "defends", "upholds", "maintains",
                "confirms", "validates", "proves", "demonstrates", "shows",
                "evidence", "study finds", "research shows", "analysis reveals",
                # Positive framing
                "success", "achievement", "progress", "improvement", "growth",
                "benefit", "advantage", "positive", "good", "effective", "working",
                # Action indicators
                "implements", "enacts", "establishes", "creates", "builds",
                "develops", "expands", "increases", "strengthens", "enhances"
            ],
            "oppose": [
                # Disagreement indicators
                "opposes", "disagrees", "rejects", "denies", "contradicts",
                "challenges", "questions", "criticizes", "condemns", "attacks",
                "refutes", "debunks", "disproves", "undermines", "weakens",
                # Negative framing
                "failure", "problem", "issue", "concern", "risk", "danger",
                "harm", "damage", "negative", "bad", "ineffective", "failing",
                # Action indicators
                "repeals", "removes", "eliminates", "reduces", "cuts",
                "restricts", "limits", "blocks", "prevents", "stops"
            ],
            "neutral": [
                # Neutral indicators
                "reports", "states", "says", "announces", "declares",
                "notes", "mentions", "describes", "explains", "details",
                "according to", "as reported", "it is reported", "sources say"
            ]
        }
    
    def classify_stance(self, article_text: str, user_belief: str) -> Dict:
        """
        Classify stance of article toward user belief
        
        Returns:
            {
                "stance": "support" | "oppose" | "neutral",
                "confidence": float,
                "method": "ml" | "rule_based",
                "evidence": List[str]  # Supporting phrases
            }
        """
        try:
            # Try ML-based classification first
            if self.zero_shot_classifier:
                return self._ml_stance_classification(article_text, user_belief)
            else:
                return self._rule_based_stance_classification(article_text, user_belief)
        except Exception as e:
            self.logger.error(f"Stance classification failed: {e}")
            return self._rule_based_stance_classification(article_text, user_belief)
    
    def _ml_stance_classification(self, article_text: str, user_belief: str) -> Dict:
        """Use zero-shot classification for stance detection"""
        try:
            # Prepare candidate labels
            candidate_labels = [
                "This article supports the belief",
                "This article opposes the belief", 
                "This article is neutral toward the belief"
            ]
            
            # Create hypothesis template
            hypothesis_template = f"Given the belief: '{user_belief}', this article:"
            
            # Classify
            result = self.zero_shot_classifier(
                article_text[:500],  # Limit text length
                candidate_labels,
                hypothesis_template=hypothesis_template
            )
            
            # Map results to stance
            stance_map = {
                "This article supports the belief": "support",
                "This article opposes the belief": "oppose", 
                "This article is neutral toward the belief": "neutral"
            }
            
            stance = stance_map.get(result['labels'][0], "neutral")
            confidence = result['scores'][0]
            
            return {
                "stance": stance,
                "confidence": confidence,
                "method": "ml",
                "evidence": [f"ML classification: {result['labels'][0]}"]
            }
            
        except Exception as e:
            self.logger.error(f"ML stance classification failed: {e}")
            return self._rule_based_stance_classification(article_text, user_belief)
    
    def _rule_based_stance_classification(self, article_text: str, user_belief: str) -> Dict:
        """Rule-based stance classification using keyword matching"""
        article_lower = article_text.lower()
        belief_lower = user_belief.lower()
        
        # Count stance indicators
        stance_counts = {}
        evidence = []
        
        for stance, indicators in self.stance_indicators.items():
            count = 0
            found_indicators = []
            
            for indicator in indicators:
                if indicator in article_lower:
                    count += 1
                    found_indicators.append(indicator)
            
            stance_counts[stance] = count
            if found_indicators:
                evidence.extend(found_indicators[:3])  # Limit evidence
        
        # Determine stance based on counts
        if stance_counts["support"] > stance_counts["oppose"] and stance_counts["support"] > 0:
            stance = "support"
            confidence = min(0.8, stance_counts["support"] / 5.0)  # Cap confidence
        elif stance_counts["oppose"] > stance_counts["support"] and stance_counts["oppose"] > 0:
            stance = "oppose"
            confidence = min(0.8, stance_counts["oppose"] / 5.0)
        else:
            stance = "neutral"
            confidence = 0.5
        
        return {
            "stance": stance,
            "confidence": confidence,
            "method": "rule_based",
            "evidence": evidence[:5]  # Limit evidence
        }
    
    def batch_classify_stances(self, articles: List[Dict], user_belief: str) -> List[Dict]:
        """Classify stance for multiple articles"""
        results = []
        
        for article in articles:
            # Combine title and description for analysis
            content = f"{article.get('title', '')} {article.get('description', '')}"
            
            stance_result = self.classify_stance(content, user_belief)
            
            # Add stance info to article
            article['stance_analysis'] = stance_result
            results.append(article)
        
        return results

# Global instance
stance_detector = StanceDetector() 