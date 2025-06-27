"""
Advanced Stance Detection Service

This service detects whether an article supports, opposes, or is neutral toward a specific belief statement.
Uses a hybrid approach:
1. HuggingFace NLI models for semantic entailment
2. Rule-based patterns for edge cases
3. Keyword-based fallback for robustness

The core question: "Does this article support/oppose THIS specific belief statement?"
"""

import asyncio
import logging
import time
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import numpy as np

# HuggingFace imports
try:
    from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
    from sentence_transformers import SentenceTransformer
    import torch
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    HUGGINGFACE_AVAILABLE = False
    logging.warning("HuggingFace not available - using rule-based stance detection")

logger = logging.getLogger(__name__)

@dataclass
class StanceResult:
    """Result of stance detection"""
    belief: str
    article_text: str
    stance: str  # 'support', 'oppose', 'neutral'
    confidence: float
    method: str  # 'nli', 'rules', 'keywords', 'fallback'
    evidence: List[str]  # Supporting evidence from the text
    processing_time: float
    metadata: Dict[str, Any] = None

class AdvancedStanceDetector:
    """
    Advanced stance detection using multiple methods
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize models
        self.nli_pipeline = None
        self.sentence_transformer = None
        self.device = "cpu"
        
        # Rule-based patterns
        self.support_patterns = self._load_support_patterns()
        self.oppose_patterns = self._load_oppose_patterns()
        
        # Metrics
        self.metrics = {
            'total_analyses': 0,
            'nli_analyses': 0,
            'rule_analyses': 0,
            'keyword_analyses': 0,
            'fallback_analyses': 0,
            'average_processing_time': 0.0
        }
        
        # Initialize models
        self._initialize_models()
        
        self.logger.info("AdvancedStanceDetector initialized")
    
    def _initialize_models(self):
        """Initialize HuggingFace models"""
        if not HUGGINGFACE_AVAILABLE:
            self.logger.warning("HuggingFace not available - using rule-based detection")
            return
        
        try:
            # Initialize NLI pipeline for entailment detection
            self.nli_pipeline = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=0 if torch.cuda.is_available() else -1
            )
            self.logger.info("NLI pipeline initialized with facebook/bart-large-mnli")
            
            # Initialize sentence transformer for semantic similarity
            self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
            self.logger.info("Sentence transformer initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize models: {e}")
            self.nli_pipeline = None
            self.sentence_transformer = None
    
    def _load_support_patterns(self) -> List[Tuple[str, float]]:
        """Load patterns that indicate support for a belief"""
        return [
            # Direct support patterns
            (r'\b(supports?|backs?|endorses?|agrees? with|confirms?|validates?)\b', 0.8),
            (r'\b(evidence|proves?|demonstrates?|shows?)\s+(that|how)\b', 0.7),
            (r'\b(clearly|obviously|undoubtedly|certainly)\s+(supports?|shows?)\b', 0.9),
            (r'\b(study|research|analysis)\s+(confirms?|shows?|demonstrates?)\b', 0.6),
            (r'\b(found|discovered|revealed)\s+(that|how)\b', 0.5),
            
            # Positive framing patterns
            (r'\b(beneficial|positive|good|effective|successful)\b', 0.4),
            (r'\b(improves?|enhances?|strengthens?|boosts?)\b', 0.5),
            (r'\b(necessary|essential|important|crucial)\b', 0.4),
            
            # Agreement patterns
            (r'\b(agree|concur|accept|acknowledge)\b', 0.6),
            (r'\b(consistent with|in line with|aligned with)\b', 0.7),
        ]
    
    def _load_oppose_patterns(self) -> List[Tuple[str, float]]:
        """Load patterns that indicate opposition to a belief"""
        return [
            # Direct opposition patterns
            (r'\b(opposes?|rejects?|denies?|disagrees? with|contradicts?|refutes?)\b', 0.8),
            (r'\b(debunks?|disproves?|invalidates?|challenges?)\b', 0.9),
            (r'\b(no evidence|lack of evidence|insufficient evidence)\b', 0.7),
            (r'\b(disputes?|questions?|doubts?|skeptical)\b', 0.6),
            
            # Negative framing patterns
            (r'\b(harmful|negative|bad|ineffective|unsuccessful)\b', 0.4),
            (r'\b(worsens?|weakens?|undermines?|damages?)\b', 0.5),
            (r'\b(unnecessary|unimportant|irrelevant)\b', 0.4),
            
            # Disagreement patterns
            (r'\b(disagree|dissent|reject|deny)\b', 0.6),
            (r'\b(inconsistent with|contrary to|against)\b', 0.7),
            
            # Counter-arguments
            (r'\b(however|but|nevertheless|on the other hand)\b', 0.3),
            (r'\b(alternative|different|opposing|contrary)\s+(view|perspective|argument)\b', 0.6),
        ]
    
    async def detect_stance(
        self, 
        belief: str, 
        article_text: str,
        method_preference: str = "auto"
    ) -> StanceResult:
        """
        Detect stance of article toward a specific belief
        
        Args:
            belief: The specific belief statement
            article_text: The article text to analyze
            method_preference: Preferred method ('nli', 'rules', 'auto')
            
        Returns:
            StanceResult with stance classification and evidence
        """
        start_time = time.time()
        
        self.logger.info(f"Detecting stance for belief: {belief[:100]}...")
        self.logger.info(f"Article text length: {len(article_text)} chars")
        
        self.metrics['total_analyses'] += 1
        
        try:
            # Try NLI method first (most accurate)
            if method_preference in ['auto', 'nli'] and self.nli_pipeline:
                result = await self._detect_stance_nli(belief, article_text)
                if result and result.confidence > 0.6:
                    self.metrics['nli_analyses'] += 1
                    return result
            
            # Try rule-based method
            if method_preference in ['auto', 'rules']:
                result = await self._detect_stance_rules(belief, article_text)
                if result and result.confidence > 0.5:
                    self.metrics['rule_analyses'] += 1
                    return result
            
            # Try keyword-based method
            if method_preference in ['auto', 'keywords']:
                result = await self._detect_stance_keywords(belief, article_text)
                if result and result.confidence > 0.4:
                    self.metrics['keyword_analyses'] += 1
                    return result
            
            # Fallback to neutral
            self.metrics['fallback_analyses'] += 1
            processing_time = time.time() - start_time
            
            return StanceResult(
                belief=belief,
                article_text=article_text[:500],  # Truncate for logging
                stance="neutral",
                confidence=0.3,
                method="fallback",
                evidence=["No clear stance detected"],
                processing_time=processing_time,
                metadata={'reason': 'fallback_to_neutral'}
            )
            
        except Exception as e:
            self.logger.error(f"Error in stance detection: {e}")
            processing_time = time.time() - start_time
            
            return StanceResult(
                belief=belief,
                article_text=article_text[:500],
                stance="neutral",
                confidence=0.1,
                method="error",
                evidence=[f"Error: {str(e)}"],
                processing_time=processing_time,
                metadata={'error': str(e)}
            )
    
    async def _detect_stance_nli(self, belief: str, article_text: str) -> Optional[StanceResult]:
        """Detect stance using Natural Language Inference"""
        
        if not self.nli_pipeline:
            return None
        
        try:
            # Prepare candidate labels for NLI
            candidate_labels = [
                "This text supports the claim",
                "This text opposes the claim", 
                "This text is neutral toward the claim"
            ]
            
            # Create hypothesis for NLI
            hypothesis = f"Claim: {belief}"
            
            # Run NLI classification
            result = self.nli_pipeline(
                sequences=article_text,
                candidate_labels=candidate_labels,
                hypothesis=hypothesis,
                multi_label=False
            )
            
            # Map results to stance
            label_to_stance = {
                "This text supports the claim": "support",
                "This text opposes the claim": "oppose", 
                "This text is neutral toward the claim": "neutral"
            }
            
            stance = label_to_stance.get(result['labels'][0], "neutral")
            confidence = result['scores'][0]
            
            # Extract evidence (simplified)
            evidence = [f"NLI confidence: {confidence:.3f}"]
            
            return StanceResult(
                belief=belief,
                article_text=article_text[:500],
                stance=stance,
                confidence=confidence,
                method="nli",
                evidence=evidence,
                processing_time=0.0,  # Will be set by caller
                metadata={'nli_scores': result['scores']}
            )
            
        except Exception as e:
            self.logger.error(f"NLI stance detection failed: {e}")
            return None
    
    async def _detect_stance_rules(self, belief: str, article_text: str) -> Optional[StanceResult]:
        """Detect stance using rule-based patterns"""
        
        try:
            # Extract key terms from belief for context
            belief_terms = self._extract_key_terms(belief)
            
            # Check support patterns
            support_score = 0.0
            support_evidence = []
            
            for pattern, weight in self.support_patterns:
                matches = re.finditer(pattern, article_text, re.IGNORECASE)
                for match in matches:
                    # Check if match is contextually relevant to belief
                    if self._is_contextually_relevant(match.group(), belief_terms, article_text, match.start()):
                        support_score += weight
                        support_evidence.append(f"Support pattern: '{match.group()}'")
            
            # Check oppose patterns
            oppose_score = 0.0
            oppose_evidence = []
            
            for pattern, weight in self.oppose_patterns:
                matches = re.finditer(pattern, article_text, re.IGNORECASE)
                for match in matches:
                    # Check if match is contextually relevant to belief
                    if self._is_contextually_relevant(match.group(), belief_terms, article_text, match.start()):
                        oppose_score += weight
                        oppose_evidence.append(f"Oppose pattern: '{match.group()}'")
            
            # Determine stance
            if support_score > oppose_score and support_score > 0.5:
                stance = "support"
                confidence = min(support_score / 2.0, 0.9)  # Normalize
                evidence = support_evidence[:3]  # Top 3 pieces of evidence
            elif oppose_score > support_score and oppose_score > 0.5:
                stance = "oppose"
                confidence = min(oppose_score / 2.0, 0.9)  # Normalize
                evidence = oppose_evidence[:3]  # Top 3 pieces of evidence
            else:
                stance = "neutral"
                confidence = 0.5
                evidence = ["No strong support or opposition patterns found"]
            
            return StanceResult(
                belief=belief,
                article_text=article_text[:500],
                stance=stance,
                confidence=confidence,
                method="rules",
                evidence=evidence,
                processing_time=0.0,  # Will be set by caller
                metadata={
                    'support_score': support_score,
                    'oppose_score': oppose_score,
                    'belief_terms': belief_terms
                }
            )
            
        except Exception as e:
            self.logger.error(f"Rule-based stance detection failed: {e}")
            return None
    
    async def _detect_stance_keywords(self, belief: str, article_text: str) -> Optional[StanceResult]:
        """Detect stance using keyword analysis"""
        
        try:
            # Extract key terms from belief
            belief_terms = self._extract_key_terms(belief)
            
            # Define positive and negative keywords
            positive_keywords = ['good', 'beneficial', 'effective', 'successful', 'positive', 'improve', 'help']
            negative_keywords = ['bad', 'harmful', 'ineffective', 'unsuccessful', 'negative', 'worse', 'hurt']
            
            # Count keyword occurrences near belief terms
            support_score = 0.0
            oppose_score = 0.0
            evidence = []
            
            # Simple keyword counting with proximity check
            for term in belief_terms:
                if term.lower() in article_text.lower():
                    # Check for positive keywords near the term
                    for keyword in positive_keywords:
                        if keyword in article_text.lower():
                            support_score += 0.3
                            evidence.append(f"Positive keyword '{keyword}' found")
                    
                    # Check for negative keywords near the term
                    for keyword in negative_keywords:
                        if keyword in article_text.lower():
                            oppose_score += 0.3
                            evidence.append(f"Negative keyword '{keyword}' found")
            
            # Determine stance
            if support_score > oppose_score and support_score > 0.3:
                stance = "support"
                confidence = min(support_score, 0.7)
            elif oppose_score > support_score and oppose_score > 0.3:
                stance = "oppose"
                confidence = min(oppose_score, 0.7)
            else:
                stance = "neutral"
                confidence = 0.4
            
            return StanceResult(
                belief=belief,
                article_text=article_text[:500],
                stance=stance,
                confidence=confidence,
                method="keywords",
                evidence=evidence[:3],  # Top 3 pieces of evidence
                processing_time=0.0,  # Will be set by caller
                metadata={
                    'support_score': support_score,
                    'oppose_score': oppose_score,
                    'belief_terms': belief_terms
                }
            )
            
        except Exception as e:
            self.logger.error(f"Keyword stance detection failed: {e}")
            return None
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms from text for contextual analysis"""
        # Simple extraction - can be enhanced with NLP
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter out common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can'}
        
        key_terms = [word for word in words if word not in stop_words and len(word) > 3]
        
        # Return unique terms, limited to top 5
        return list(set(key_terms))[:5]
    
    def _is_contextually_relevant(self, match_text: str, belief_terms: List[str], article_text: str, match_position: int) -> bool:
        """Check if a pattern match is contextually relevant to the belief"""
        
        # Simple proximity check - if belief terms are near the match
        context_window = 100  # characters
        
        start = max(0, match_position - context_window)
        end = min(len(article_text), match_position + len(match_text) + context_window)
        
        context = article_text[start:end].lower()
        
        # Check if any belief terms appear in the context
        for term in belief_terms:
            if term.lower() in context:
                return True
        
        return False
    
    async def batch_detect_stances(
        self, 
        belief_article_pairs: List[Tuple[str, str]],
        method_preference: str = "auto"
    ) -> List[StanceResult]:
        """Detect stances for multiple belief-article pairs"""
        
        self.logger.info(f"Batch stance detection for {len(belief_article_pairs)} pairs")
        
        tasks = [
            self.detect_stance(belief, article, method_preference)
            for belief, article in belief_article_pairs
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"Batch stance detection failed for pair {i}: {result}")
                # Create fallback result
                belief, article = belief_article_pairs[i]
                processed_results.append(StanceResult(
                    belief=belief,
                    article_text=article[:500],
                    stance="neutral",
                    confidence=0.1,
                    method="error",
                    evidence=[f"Error: {str(result)}"],
                    processing_time=0.0,
                    metadata={'error': str(result)}
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get service metrics"""
        return {
            'metrics': self.metrics.copy(),
            'models_available': {
                'nli_pipeline': self.nli_pipeline is not None,
                'sentence_transformer': self.sentence_transformer is not None
            },
            'patterns_loaded': {
                'support_patterns': len(self.support_patterns),
                'oppose_patterns': len(self.oppose_patterns)
            },
            'timestamp': datetime.now().isoformat()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for the stance detector"""
        try:
            # Test with a simple case
            test_belief = "Technology is beneficial"
            test_article = "This study shows that technology improves productivity."
            
            result = await self.detect_stance(test_belief, test_article)
            
            return {
                'status': 'healthy' if result.stance in ['support', 'oppose', 'neutral'] else 'degraded',
                'nli_available': self.nli_pipeline is not None,
                'test_stance': result.stance,
                'test_confidence': result.confidence,
                'metrics': self.get_metrics()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'metrics': self.get_metrics()
            }

# Global instance
advanced_stance_detector = AdvancedStanceDetector() 