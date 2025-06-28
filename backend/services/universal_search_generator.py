from typing import List, Dict
from datetime import datetime
import re

# Universal stance patterns that work for ANY topic
UNIVERSAL_STANCE_PATTERNS = {
    "criticism": [
        "abuse", "abuses", "war crimes", "apartheid", "criticism", "controversy", 
        "illegal", "oppression", "human rights violations", "corruption", "scandal",
        "injustice", "discrimination", "exploitation", "violence", "aggression",
        "atrocities", "genocide", "ethnic cleansing", "war crimes", "crimes against humanity",
        "wrong", "bad", "terrible", "awful", "horrible", "disgusting", "shameful",
        "unacceptable", "unjust", "unfair", "biased", "prejudiced", "racist", "sexist",
        "homophobic", "transphobic", "xenophobic", "fascist", "authoritarian", "dictatorial",
        "tyrannical", "oppressive", "repressive", "suppressive", "censorship", "propaganda",
        "lies", "deception", "manipulation", "brainwashing", "indoctrination", "radicalization"
    ],
    "support": [
        "success", "achievement", "progress", "innovation", "development", "growth",
        "improvement", "advancement", "breakthrough", "victory", "triumph", "excellence",
        "leadership", "expertise", "authority", "legitimacy", "righteousness", "justice",
        "good", "great", "amazing", "wonderful", "fantastic", "excellent", "outstanding",
        "brilliant", "genius", "revolutionary", "groundbreaking", "pioneering", "cutting-edge",
        "state-of-the-art", "world-class", "premier", "premium", "elite", "superior",
        "beneficial", "helpful", "useful", "valuable", "important", "essential", "necessary",
        "vital", "crucial", "critical", "indispensable", "irreplaceable", "unique"
    ],
    "debate": [
        "debate", "discussion", "analysis", "perspective", "viewpoint", "opinion",
        "argument", "controversy", "dispute", "conflict", "tension", "division",
        "polarization", "partisan", "bipartisan", "consensus", "agreement", "disagreement",
        "pros and cons", "advantages and disadvantages", "benefits and drawbacks",
        "strengths and weaknesses", "opportunities and threats", "risks and rewards",
        "challenges and solutions", "problems and answers", "questions and answers",
        "myths and facts", "truth and lies", "reality and fiction", "science and pseudoscience"
    ],
    "evidence": [
        "evidence", "proof", "data", "statistics", "research", "study", "report",
        "investigation", "findings", "conclusions", "facts", "truth", "reality",
        "documentation", "testimony", "witness", "expert", "authority", "source",
        "peer-reviewed", "scientific", "academic", "scholarly", "empirical", "experimental",
        "observational", "longitudinal", "cross-sectional", "meta-analysis", "systematic review",
        "randomized controlled trial", "double-blind", "placebo-controlled", "statistically significant"
    ],
    "impact": [
        "impact", "effect", "consequence", "result", "outcome", "influence",
        "change", "transformation", "evolution", "development", "progress",
        "regression", "decline", "improvement", "deterioration", "growth", "shrinkage",
        "increase", "decrease", "rise", "fall", "surge", "plunge", "spike", "drop",
        "boost", "reduction", "enhancement", "degradation", "optimization", "deterioration"
    ]
}

# Universal context patterns
UNIVERSAL_CONTEXT_PATTERNS = {
    "historical": ["history", "historical", "tradition", "legacy", "heritage", "past", "ancient", "century", "decade", "era", "period"],
    "current": ["current", "present", "now", "today", "recent", "latest", "modern", "contemporary", "ongoing", "active"],
    "future": ["future", "planning", "forecast", "prediction", "projection", "tomorrow", "upcoming", "forthcoming", "anticipated"],
    "global": ["global", "international", "worldwide", "universal", "cross-border", "multinational", "transnational", "intercontinental"],
    "local": ["local", "regional", "national", "domestic", "community", "neighborhood", "city", "state", "province", "county"],
    "political": ["politics", "government", "policy", "legislation", "regulation", "administration", "bureaucracy", "democracy", "republic", "monarchy"],
    "economic": ["economy", "financial", "economic", "business", "market", "commerce", "trade", "industry", "commerce", "fiscal", "monetary"],
    "social": ["social", "society", "community", "culture", "demographics", "population", "public", "civil", "civic", "communal"],
    "environmental": ["environment", "climate", "sustainability", "ecological", "green", "renewable", "conservation", "preservation", "biodiversity"],
    "technological": ["technology", "innovation", "digital", "automation", "AI", "artificial intelligence", "machine learning", "automation", "robotics"]
}

class UniversalSearchGenerator:
    def __init__(self):
        self.stance_patterns = UNIVERSAL_STANCE_PATTERNS
        self.context_patterns = UNIVERSAL_CONTEXT_PATTERNS
    
    def generate_search_terms(self, query: str, user_view: str, bias: float) -> List[str]:
        """Generate targeted search terms for any topic"""
        try:
            print(f"🔍 UNIVERSAL GENERATOR: Generating terms for query: '{query}'")
            print(f"🔍 UNIVERSAL GENERATOR: User view: '{user_view}'")
            print(f"🔍 UNIVERSAL GENERATOR: Bias: {bias}")
            
            # Extract the main topic (first few words)
            topic = self._extract_main_topic(query)
            print(f"🔍 UNIVERSAL GENERATOR: Extracted topic: '{topic}'")
            
            # Generate focused search terms
            search_terms = []
            
            # 1. Direct topic searches
            search_terms.extend([
                topic,
                f'"{topic}"',
                f'{topic} news',
                f'{topic} latest',
                f'{topic} today'
            ])
            
            # 2. Topic + stance combinations
            if user_view:
                search_terms.extend([
                    f'{topic} {user_view}',
                    f'"{topic}" "{user_view}"',
                    f'{topic} {user_view} news',
                    f'{topic} {user_view} latest'
                ])
            
            # 3. Topic + context (if we can extract context)
            context_words = self._extract_context_words(query)
            if context_words:
                for context in context_words[:3]:  # Limit to top 3 contexts
                    search_terms.extend([
                        f'{topic} {context}',
                        f'"{topic}" "{context}"',
                        f'{topic} {context} news'
                    ])
            
            # 4. Recent news patterns
            search_terms.extend([
                f'{topic} 2025',
                f'{topic} this week',
                f'{topic} recent',
                f'{topic} breaking'
            ])
            
            # 5. Source-specific patterns (for major news sources)
            major_sources = ['CNN', 'BBC', 'Reuters', 'NPR', 'Fox News', 'MSNBC']
            for source in major_sources[:2]:  # Limit to top 2 sources
                search_terms.extend([
                    f'{topic} {source}',
                    f'"{topic}" site:{source.lower().replace(" ", "")}.com'
                ])
            
            # Remove duplicates and limit to reasonable number
            unique_terms = list(dict.fromkeys(search_terms))  # Preserve order
            final_terms = unique_terms[:15]  # Limit to top 15 terms
            
            print(f"🔍 UNIVERSAL GENERATOR: Generated {len(final_terms)} focused search terms")
            print(f"🔍 UNIVERSAL GENERATOR: Sample terms: {final_terms[:5]}")
            
            return final_terms
            
        except Exception as e:
            print(f"🔍 UNIVERSAL GENERATOR: Error generating terms: {e}")
            # Fallback to simple topic search
            topic = query.split()[0] if query else "news"
            return [topic, f'"{topic}"', f'{topic} news']
    
    def _extract_main_topic(self, query: str) -> str:
        """Extract the main topic from the query"""
        words = query.split()
        
        # Look for the first significant word (not common words)
        common_words = {'i', 'am', 'is', 'are', 'was', 'were', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'up', 'down', 'out', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'can', 'may', 'must', 'shall', 'this', 'that', 'these', 'those'}
        
        for word in words:
            clean_word = word.lower().strip('.,!?;:')
            if clean_word and clean_word not in common_words and len(clean_word) > 2:
                return clean_word
        
        # Fallback to first word
        return words[0] if words else "news"
    
    def _extract_context_words(self, query: str) -> List[str]:
        """Extract context words from the query"""
        words = query.lower().split()
        context_words = []
        
        # Look for words that might indicate context
        context_indicators = ['support', 'oppose', 'against', 'for', 'pro', 'anti', 'ruining', 'destroying', 'helping', 'improving', 'changing', 'reforming', 'ending', 'starting', 'banning', 'allowing', 'legalizing', 'criminalizing']
        
        for word in words:
            clean_word = word.strip('.,!?;:')
            if clean_word in context_indicators:
                context_words.append(clean_word)
        
        return context_words
    
    def _extract_primary_topic(self, query: str) -> str:
        """Extract the main topic from any query"""
        # Simple extraction - look for the first noun phrase or key terms
        words = query.lower().split()
        
        # Remove common words
        stop_words = {'i', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'from', 'up', 'down', 'out', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'you', 'your', 'yours', 'yourself', 'yourselves', 'we', 'our', 'ours', 'ourselves', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'me', 'him', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself'}
        
        # Find the first significant word (not a stop word)
        for word in words:
            if word not in stop_words and len(word) > 2:
                return word
        
        # Fallback: return first word
        return words[0] if words else "news"
    
    def _analyze_user_sentiment(self, user_view: str) -> Dict[str, float]:
        """Analyze user sentiment to determine stance direction"""
        user_view_lower = user_view.lower()
        
        # Count positive and negative words
        positive_words = ['love', 'like', 'good', 'great', 'amazing', 'wonderful', 'fantastic', 'excellent', 'support', 'agree', 'right', 'correct', 'true', 'necessary', 'important', 'essential', 'beneficial', 'helpful', 'useful', 'valuable']
        negative_words = ['hate', 'dislike', 'bad', 'terrible', 'awful', 'horrible', 'wrong', 'incorrect', 'false', 'oppose', 'disagree', 'against', 'harmful', 'dangerous', 'risky', 'problematic', 'concerning', 'worried', 'scared', 'angry']
        
        positive_count = sum(1 for word in positive_words if word in user_view_lower)
        negative_count = sum(1 for word in negative_words if word in user_view_lower)
        
        total_words = len(user_view_lower.split())
        if total_words == 0:
            return {'positive': 0.0, 'negative': 0.0, 'neutral': 1.0}
        
        positive_score = positive_count / total_words
        negative_score = negative_count / total_words
        neutral_score = 1.0 - positive_score - negative_score
        
        return {
            'positive': positive_score,
            'negative': negative_score,
            'neutral': neutral_score
        }
    
    def _extract_context(self, query: str) -> List[str]:
        """Extract contextual clues from the query"""
        query_lower = query.lower()
        contexts = []
        
        for context_name, context_words in self.context_patterns.items():
            if any(word in query_lower for word in context_words):
                contexts.append(context_name)
        
        return contexts
    
    def _generate_base_terms(self, topic: str, user_view: str) -> List[str]:
        """Generate base search terms"""
        terms = [topic, f'"{topic}"']
        
        if user_view:
            terms.extend([
                f'{topic} {user_view}',
                f'"{topic}" "{user_view}"',
                f'{topic} {user_view.strip()}',
                f'"{topic}" {user_view.strip()}'
            ])
        
        return terms
    
    def _generate_stance_terms(self, topic: str, sentiment: Dict, bias: float) -> List[str]:
        """Generate stance-specific terms based on user sentiment and bias preference"""
        terms = []
        
        # Determine what stance the user wants based on sentiment + bias
        if sentiment['negative'] > 0.1 and bias > 0.7:
            # User has negative view and wants supporting content
            # = Find content that criticizes/opposes the topic
            stance_category = "criticism"
        elif sentiment['positive'] > 0.1 and bias > 0.7:
            # User has positive view and wants supporting content
            # = Find content that praises/supports the topic
            stance_category = "support"
        elif bias < 0.3:
            # User wants challenging views (opposite of their sentiment)
            stance_category = "criticism" if sentiment['positive'] > sentiment['negative'] else "support"
        else:
            # User wants balanced/debate content
            stance_category = "debate"
        
        print(f"🔍 UNIVERSAL GENERATOR: Using stance category: {stance_category}")
        
        # Generate terms using universal patterns
        for pattern in self.stance_patterns[stance_category]:
            terms.append(f"{topic} {pattern}")
            terms.append(f'"{topic}" "{pattern}"')
        
        # Also add evidence terms for any stance
        for pattern in self.stance_patterns["evidence"]:
            terms.append(f"{topic} {pattern}")
        
        return terms
    
    def _generate_context_terms(self, topic: str, contexts: List[str]) -> List[str]:
        """Generate context-specific terms"""
        terms = []
        
        for context in contexts:
            if context in self.context_patterns:
                for pattern in self.context_patterns[context]:
                    terms.append(f"{topic} {pattern}")
        
        return terms
    
    def _generate_temporal_terms(self, topic: str) -> List[str]:
        """Generate temporal terms for different time periods"""
        current_year = datetime.now().year
        terms = []
        
        # Recent terms
        terms.extend([
            f"{topic} recent", f"{topic} latest", f"{topic} current",
            f"{topic} today", f"{topic} now", f"{topic} this year"
        ])
        
        # Historical terms
        terms.extend([
            f"{topic} history", f"{topic} historical", f"{topic} legacy",
            f"{topic} past", f"{topic} tradition"
        ])
        
        # Year-specific terms (last 5 years)
        for year in range(current_year, current_year - 5, -1):
            terms.append(f"{topic} {year}")
        
        return terms
    
    def _generate_source_terms(self, topic: str, bias: float) -> List[str]:
        """Generate source-specific terms based on bias preference"""
        terms = []
        
        # Academic/research sources
        terms.extend([
            f"{topic} research", f"{topic} study", f"{topic} academic",
            f"{topic} university", f"{topic} professor", f"{topic} expert"
        ])
        
        # NGO/human rights sources (for critical views)
        if bias > 0.7:
            terms.extend([
                f"{topic} NGO", f"{topic} human rights", f"{topic} report",
                f"{topic} investigation", f"{topic} watchdog"
            ])
        
        # Government/official sources
        terms.extend([
            f"{topic} government", f"{topic} official", f"{topic} policy",
            f"{topic} regulation", f"{topic} law"
        ])
        
        # News and media sources
        terms.extend([
            f"{topic} news", f"{topic} media", f"{topic} coverage",
            f"{topic} analysis", f"{topic} opinion", f"{topic} editorial"
        ])
        
        return terms 