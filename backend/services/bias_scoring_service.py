from typing import List, Dict, Tuple
import json
import numpy as np
import re
from textblob import TextBlob
# from services.fusion_engine import FusionEngine  # Temporarily disabled due to LangChain dependency issues

class BiasScoringService:
    def __init__(self):
        # self.fusion_engine = FusionEngine()  # Temporarily disabled
        self.source_bias_map = self._load_source_bias_map()
        self.extreme_keywords = self._load_extreme_keywords()
        self.polarizing_phrases = self._load_polarizing_phrases()
    
    def _load_source_bias_map(self) -> Dict[str, Dict]:
        """Load comprehensive source bias mappings with extreme sources"""
        return {
            # Mainstream sources (moderate bias)
            "reuters.com": {"bias": "Center", "reliability": 0.9, "extremity": 0.2},
            "ap.org": {"bias": "Center", "reliability": 0.9, "extremity": 0.2},
            "bbc.com": {"bias": "Center", "reliability": 0.8, "extremity": 0.3},
            "cnn.com": {"bias": "Left", "reliability": 0.7, "extremity": 0.4},
            "foxnews.com": {"bias": "Right", "reliability": 0.7, "extremity": 0.6},
            "msnbc.com": {"bias": "Left", "reliability": 0.7, "extremity": 0.5},
            "nytimes.com": {"bias": "Left", "reliability": 0.8, "extremity": 0.4},
            "wsj.com": {"bias": "Right", "reliability": 0.8, "extremity": 0.4},
            "washingtonpost.com": {"bias": "Left", "reliability": 0.8, "extremity": 0.4},
            
            # More extreme sources
            "breitbart.com": {"bias": "Far-Right", "reliability": 0.4, "extremity": 0.9},
            "infowars.com": {"bias": "Far-Right", "reliability": 0.2, "extremity": 1.0},
            "dailywire.com": {"bias": "Far-Right", "reliability": 0.5, "extremity": 0.8},
            "theblaze.com": {"bias": "Far-Right", "reliability": 0.4, "extremity": 0.8},
            "townhall.com": {"bias": "Far-Right", "reliability": 0.5, "extremity": 0.7},
            "nationalreview.com": {"bias": "Right", "reliability": 0.6, "extremity": 0.6},
            
            # Far-left sources
            "jacobinmag.com": {"bias": "Far-Left", "reliability": 0.5, "extremity": 0.8},
            "commondreams.org": {"bias": "Far-Left", "reliability": 0.4, "extremity": 0.8},
            "truthout.org": {"bias": "Far-Left", "reliability": 0.4, "extremity": 0.8},
            "alternet.org": {"bias": "Far-Left", "reliability": 0.4, "extremity": 0.7},
            "democracynow.org": {"bias": "Far-Left", "reliability": 0.5, "extremity": 0.7},
            "theintercept.com": {"bias": "Far-Left", "reliability": 0.6, "extremity": 0.6},
            
            # Other sources
            "usatoday.com": {"bias": "Center", "reliability": 0.7, "extremity": 0.3},
            "nbcnews.com": {"bias": "Left", "reliability": 0.7, "extremity": 0.4},
            "abcnews.go.com": {"bias": "Center", "reliability": 0.7, "extremity": 0.3},
            "cbsnews.com": {"bias": "Center", "reliability": 0.7, "extremity": 0.3},
            "npr.org": {"bias": "Left", "reliability": 0.8, "extremity": 0.4},
            "pbs.org": {"bias": "Center", "reliability": 0.8, "extremity": 0.3},
            "bloomberg.com": {"bias": "Center", "reliability": 0.8, "extremity": 0.3},
            "forbes.com": {"bias": "Right", "reliability": 0.7, "extremity": 0.4},
        }
    
    def _load_extreme_keywords(self) -> Dict[str, List[str]]:
        """Load extreme keywords for content analysis"""
        return {
            "far_right": [
                "deep state", "globalist", "elite", "establishment", "mainstream media", "fake news",
                "woke", "cancel culture", "critical race theory", "socialism", "communism",
                "illegal aliens", "border crisis", "gun control", "second amendment", "patriot",
                "maga", "trump", "conservative", "traditional values", "religious freedom",
                "pro-life", "pro-choice", "abortion", "lgbtq", "transgender", "gender ideology",
                "climate hoax", "global warming", "vaccine", "mandate", "freedom", "liberty"
            ],
            "far_left": [
                "systemic racism", "white privilege", "defund police", "abolish police", "reparations",
                "socialism", "communism", "capitalism", "billionaire", "wealth inequality",
                "climate emergency", "climate crisis", "green new deal", "medicare for all",
                "universal basic income", "progressive", "liberal", "woke", "social justice",
                "lgbtq rights", "trans rights", "feminism", "patriarchy", "toxic masculinity",
                "microaggression", "safe space", "trigger warning", "cultural appropriation"
            ],
            "anti_trump": [
                "trump", "maga", "republican", "conservative", "right-wing", "fascist", "authoritarian",
                "dictator", "corruption", "impeachment", "insurrection", "january 6", "capitol riot",
                "election fraud", "big lie", "qanon", "conspiracy", "cult", "cult leader"
            ],
            "pro_trump": [
                "biden", "democrat", "liberal", "left-wing", "socialist", "communist", "radical left",
                "antifa", "blm", "defund police", "cancel culture", "woke", "critical race theory",
                "deep state", "swamp", "drain the swamp", "fake news", "mainstream media",
                "election fraud", "stolen election", "patriot", "freedom", "america first"
            ]
        }
    
    def _load_polarizing_phrases(self) -> Dict[str, List[str]]:
        """Load polarizing phrases that indicate extreme viewpoints"""
        return {
            "far_right_phrases": [
                "radical left agenda", "socialist takeover", "communist infiltration",
                "destroy america", "end of democracy", "tyranny", "dictatorship",
                "woke mob", "cancel culture warriors", "thought police",
                "globalist conspiracy", "new world order", "great reset"
            ],
            "far_left_phrases": [
                "fascist regime", "authoritarian rule", "dictatorship", "tyranny",
                "systemic oppression", "white supremacy", "racist system",
                "climate emergency", "existential threat", "extinction",
                "revolution", "overthrow", "abolish capitalism"
            ]
        }
    
    async def calculate_topical_score(self, article_content: str, topic: str) -> float:
        """Calculate topical relevance score using embeddings"""
        try:
            # Temporarily return a mock score since FusionEngine is disabled
            # article_embedding = await self.fusion_engine.embeddings.aembed_query(article_content[:1000])
            # topic_embedding = await self.fusion_engine.embeddings.aembed_query(topic)
            # similarity = self._cosine_similarity(article_embedding, topic_embedding)
            # return similarity
            return 0.7  # Mock score
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
            
            # Temporarily return a mock score since FusionEngine is disabled
            # article_embedding = await self.fusion_engine.embeddings.aembed_query(article_content[:1000])
            # belief_scores = []
            # for belief in beliefs:
            #     belief_embedding = await self.fusion_engine.embeddings.aembed_query(belief)
            #     similarity = self._cosine_similarity(article_embedding, belief_embedding)
            #     belief_scores.append(similarity)
            # return sum(belief_scores) / len(belief_scores)
            return 0.6  # Mock score
        except Exception as e:
            print(f"Error calculating belief alignment: {e}")
            return 0.5
    
    def calculate_ideological_score(self, source_domain: str, bias_slider: float) -> float:
        """Calculate ideological proximity score with aggressive bias detection"""
        source_info = self.source_bias_map.get(source_domain, {"bias": "Center", "reliability": 0.5, "extremity": 0.3})
        source_bias = source_info["bias"]
        source_extremity = source_info.get("extremity", 0.3)
        
        # Map bias labels to numerical values with more extreme ranges
        bias_values = {
            "Far-Left": 0.0, 
            "Left": 0.2, 
            "Center": 0.5, 
            "Right": 0.8, 
            "Far-Right": 1.0
        }
        source_bias_value = bias_values.get(source_bias, 0.5)
        
        # Calculate ideological score based on bias slider
        if bias_slider <= 0.3:  # "Challenge me" - want opposite extreme views
            # Prefer sources on the opposite end of the spectrum
            if bias_slider <= 0.1:  # Far left - want far right sources
                target_bias = 1.0
            elif bias_slider <= 0.2:  # Left - want right sources
                target_bias = 0.8
            else:  # Center-left - want center-right sources
                target_bias = 0.7
        elif bias_slider >= 0.7:  # "Prove me right" - want aligned extreme views
            # Prefer sources on the same end of the spectrum
            if bias_slider >= 0.9:  # Far right - want far right sources
                target_bias = 1.0
            elif bias_slider >= 0.8:  # Right - want right sources
                target_bias = 0.8
            else:  # Center-right - want center-right sources
                target_bias = 0.7
        else:  # Center - prefer moderate sources
            target_bias = 0.5
        
        # Calculate distance from target bias
        distance = abs(source_bias_value - target_bias)
        
        # Convert distance to score (closer = higher score)
        # Boost score for extreme sources when user wants extreme views
        base_score = 1.0 - distance
        
        # Apply extremity boost
        if bias_slider <= 0.3 or bias_slider >= 0.7:
            # User wants extreme views, boost extreme sources
            extremity_boost = source_extremity * 0.3
            base_score += extremity_boost
        
        return max(0.0, min(1.0, base_score))
    
    def analyze_content_bias(self, article_text: str) -> Dict:
        """Analyze article content for bias indicators"""
        text_lower = article_text.lower()
        
        # Count extreme keywords
        keyword_counts = {}
        for category, keywords in self.extreme_keywords.items():
            count = sum(1 for keyword in keywords if keyword.lower() in text_lower)
            keyword_counts[category] = count
        
        # Count polarizing phrases
        phrase_counts = {}
        for category, phrases in self.polarizing_phrases.items():
            count = sum(1 for phrase in phrases if phrase.lower() in text_lower)
            phrase_counts[category] = count
        
        # Calculate sentiment
        blob = TextBlob(article_text)
        sentiment_score = blob.sentiment.polarity
        
        # Determine overall bias direction
        far_right_score = keyword_counts.get("far_right", 0) + phrase_counts.get("far_right_phrases", 0)
        far_left_score = keyword_counts.get("far_left", 0) + phrase_counts.get("far_left_phrases", 0)
        anti_trump_score = keyword_counts.get("anti_trump", 0)
        pro_trump_score = keyword_counts.get("pro_trump", 0)
        
        # Calculate extremity score
        total_extreme_keywords = sum(keyword_counts.values())
        extremity_score = min(total_extreme_keywords / 10.0, 1.0)  # Normalize to 0-1
        
        # Determine bias direction
        if far_right_score > far_left_score and far_right_score > 2:
            bias_direction = "far_right"
        elif far_left_score > far_right_score and far_left_score > 2:
            bias_direction = "far_left"
        elif anti_trump_score > pro_trump_score and anti_trump_score > 1:
            bias_direction = "anti_trump"
        elif pro_trump_score > anti_trump_score and pro_trump_score > 1:
            bias_direction = "pro_trump"
        else:
            bias_direction = "neutral"
        
        return {
            "keyword_counts": keyword_counts,
            "phrase_counts": phrase_counts,
            "sentiment_score": sentiment_score,
            "extremity_score": extremity_score,
            "bias_direction": bias_direction,
            "far_right_score": far_right_score,
            "far_left_score": far_left_score,
            "anti_trump_score": anti_trump_score,
            "pro_trump_score": pro_trump_score
        }
    
    def get_source_bias_info(self, source_domain: str) -> Dict:
        """Get bias and reliability information for a source"""
        return self.source_bias_map.get(source_domain, {
            "bias": "Center", 
            "reliability": 0.5,
            "extremity": 0.3
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