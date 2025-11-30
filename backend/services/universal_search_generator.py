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

class UniversalSearchTermGenerator:
    """Generate intelligent, stance-aware search terms for any topic"""
    
    def __init__(self):
        self.negative_keywords = {
            'hate', 'terrible', 'awful', 'bad', 'wrong', 'dislike', 'evil', 'horrible',
            'worst', 'disgusting', 'terrible', 'awful', 'dreadful', 'atrocious',
            'ruining', 'destroying', 'damaging', 'harming', 'hurting', 'problematic',
            'controversial', 'scandal', 'corruption', 'failure', 'disaster', 'crisis'
        }
        
        self.positive_keywords = {
            'love', 'great', 'amazing', 'good', 'right', 'like', 'excellent', 'wonderful',
            'fantastic', 'brilliant', 'outstanding', 'perfect', 'best', 'superior',
            'helping', 'improving', 'beneficial', 'positive', 'success', 'achievement',
            'victory', 'triumph', 'breakthrough', 'innovation', 'progress'
        }
        
        self.critical_terms = {
            'criticism', 'criticize', 'critic', 'opposition', 'oppose', 'against',
            'protest', 'protesters', 'demonstration', 'backlash', 'outrage',
            'controversy', 'scandal', 'investigation', 'allegations', 'charges',
            'lawsuit', 'legal', 'court', 'judge', 'prosecution', 'conviction',
            'failure', 'collapse', 'bankruptcy', 'crisis', 'emergency', 'disaster',
            'resignation', 'fired', 'terminated', 'suspended', 'banned', 'prohibited'
        }
        
        self.supportive_terms = {
            'support', 'supporter', 'endorse', 'endorsement', 'approval', 'approve',
            'success', 'achievement', 'victory', 'win', 'triumph', 'breakthrough',
            'innovation', 'progress', 'improvement', 'growth', 'expansion',
            'election', 'reelection', 'campaign', 'rally', 'speech', 'announcement',
            'launch', 'release', 'introduction', 'new', 'latest', 'updated'
        }
        
        self.news_sources = {
            'liberal': ['msnbc.com', 'cnn.com', 'nytimes.com', 'washingtonpost.com', 'huffpost.com', 'vox.com', 'theguardian.com'],
            'conservative': ['foxnews.com', 'breitbart.com', 'nypost.com', 'washingtontimes.com', 'dailywire.com', 'newsmax.com'],
            'neutral': ['reuters.com', 'ap.org', 'bbc.com', 'npr.org', 'pbs.org', 'abcnews.go.com', 'cbsnews.com', 'nbcnews.com']
        }
    
    def generate_search_terms(self, query: str, bias: float) -> List[str]:
        """
        Generate intelligent, stance-aware search terms
        
        Args:
            query: User query like "maga I hate maga"
            bias: 0.0 = challenging views, 1.0 = supporting views
        
        Returns:
            List of intelligent search terms
        """
        print(f"🔍 INTELLIGENT SEARCH: Generating stance-aware terms for '{query}' with bias {bias}")
        
        # Extract topic and user view
        topic, user_view = self._extract_topic_and_view(query)
        print(f"🔍 INTELLIGENT SEARCH: Topic: '{topic}', User view: '{user_view}'")
        
        # Determine user sentiment
        user_sentiment = self._analyze_user_sentiment(user_view)
        print(f"🔍 INTELLIGENT SEARCH: User sentiment: {user_sentiment}")
        
        # Generate stance-aware terms
        if bias == 0.0:  # User wants challenging views
            terms = self._generate_challenging_terms(topic, user_sentiment)
        elif bias == 1.0:  # User wants supporting views
            terms = self._generate_supporting_terms(topic, user_sentiment)
        else:  # Mixed bias
            terms = self._generate_mixed_terms(topic, user_sentiment, bias)
        
        print(f"🔍 INTELLIGENT SEARCH: Generated {len(terms)} stance-aware terms")
        print(f"🔍 INTELLIGENT SEARCH: Sample terms: {terms[:5]}")
        
        return terms
    
    def _extract_topic_and_view(self, query: str) -> tuple[str, str]:
        """Extract topic and user view from query"""
        words = query.split()
        if len(words) < 2:
            return words[0] if words else "news", ""
        
        # Find the main topic (usually first significant word)
        topic = words[0].lower()
        user_view = " ".join(words[1:])
        
        return topic, user_view
    
    def _analyze_user_sentiment(self, user_view: str) -> str:
        """Analyze user sentiment from their view"""
        user_view_lower = user_view.lower()
        
        negative_count = sum(1 for word in self.negative_keywords if word in user_view_lower)
        positive_count = sum(1 for word in self.positive_keywords if word in user_view_lower)
        
        if negative_count > positive_count:
            return "negative"
        elif positive_count > negative_count:
            return "positive"
        else:
            return "neutral"
    
    def _generate_challenging_terms(self, topic: str, user_sentiment: str) -> List[str]:
        """Generate terms that challenge the user's view"""
        terms = []
        
        if user_sentiment == "negative":
            # User hates the topic, so challenging views = articles that support the topic
            terms.extend([
                f'"{topic}"',
                f'intitle:{topic}',
                f'{topic} support',
                f'{topic} supporters',
                f'{topic} endorsement',
                f'{topic} success',
                f'{topic} achievement',
                f'{topic} victory',
                f'{topic} positive',
                f'{topic} beneficial',
                f'{topic} improvement',
                f'{topic} growth',
                f'{topic} progress',
                f'{topic} breakthrough',
                f'{topic} innovation'
            ])
        elif user_sentiment == "positive":
            # User loves the topic, so challenging views = articles that oppose the topic
            terms.extend([
                f'"{topic}"',
                f'intitle:{topic}',
                f'{topic} criticism',
                f'{topic} critics',
                f'{topic} opposition',
                f'{topic} protest',
                f'{topic} controversy',
                f'{topic} scandal',
                f'{topic} failure',
                f'{topic} crisis',
                f'{topic} problems',
                f'{topic} issues',
                f'{topic} negative',
                f'{topic} harmful',
                f'{topic} dangerous'
            ])
        else:
            # Neutral user, provide balanced challenging views
            terms.extend([
                f'"{topic}"',
                f'intitle:{topic}',
                f'{topic} debate',
                f'{topic} discussion',
                f'{topic} analysis',
                f'{topic} review',
                f'{topic} opinion',
                f'{topic} perspective',
                f'{topic} viewpoint',
                f'{topic} argument',
                f'{topic} controversy',
                f'{topic} criticism',
                f'{topic} support',
                f'{topic} opposition'
            ])
        
        return terms
    
    def _generate_supporting_terms(self, topic: str, user_sentiment: str) -> List[str]:
        """Generate terms that support the user's view"""
        terms = []
        
        if user_sentiment == "negative":
            # User hates the topic, so supporting views = articles that also oppose the topic
            terms.extend([
                f'"{topic}"',
                f'intitle:{topic}',
                f'{topic} criticism',
                f'{topic} critics',
                f'{topic} opposition',
                f'{topic} protest',
                f'{topic} controversy',
                f'{topic} scandal',
                f'{topic} failure',
                f'{topic} crisis',
                f'{topic} problems',
                f'{topic} issues',
                f'{topic} negative',
                f'{topic} harmful',
                f'{topic} dangerous',
                f'{topic} investigation',
                f'{topic} allegations',
                f'{topic} charges',
                f'{topic} lawsuit',
                f'{topic} legal'
            ])
        elif user_sentiment == "positive":
            # User loves the topic, so supporting views = articles that also support the topic
            terms.extend([
                f'"{topic}"',
                f'intitle:{topic}',
                f'{topic} support',
                f'{topic} supporters',
                f'{topic} endorsement',
                f'{topic} success',
                f'{topic} achievement',
                f'{topic} victory',
                f'{topic} positive',
                f'{topic} beneficial',
                f'{topic} improvement',
                f'{topic} growth',
                f'{topic} progress',
                f'{topic} breakthrough',
                f'{topic} innovation',
                f'{topic} launch',
                f'{topic} announcement',
                f'{topic} new',
                f'{topic} latest',
                f'{topic} updated'
            ])
        else:
            # Neutral user, provide balanced supporting views
            terms.extend([
                f'"{topic}"',
                f'intitle:{topic}',
                f'{topic} news',
                f'{topic} latest',
                f'{topic} update',
                f'{topic} recent',
                f'{topic} today',
                f'{topic} current',
                f'{topic} development',
                f'{topic} story',
                f'{topic} report',
                f'{topic} coverage',
                f'{topic} analysis',
                f'{topic} review'
            ])
        
        return terms
    
    def _generate_mixed_terms(self, topic: str, user_sentiment: str, bias: float) -> List[str]:
        """Generate mixed terms based on bias level"""
        challenging_terms = self._generate_challenging_terms(topic, user_sentiment)
        supporting_terms = self._generate_supporting_terms(topic, user_sentiment)
        
        # Mix based on bias level
        num_challenging = int(len(challenging_terms) * (1 - bias))
        num_supporting = int(len(supporting_terms) * bias)
        
        terms = challenging_terms[:num_challenging] + supporting_terms[:num_supporting]
        
        # Add some neutral terms
        neutral_terms = [
            f'"{topic}"',
            f'intitle:{topic}',
            f'{topic} news',
            f'{topic} latest',
            f'{topic} update'
        ]
        
        return terms + neutral_terms
    
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
        
        for context_name, context_words in UNIVERSAL_CONTEXT_PATTERNS.items():
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
        for pattern in UNIVERSAL_STANCE_PATTERNS[stance_category]:
            terms.append(f"{topic} {pattern}")
            terms.append(f'"{topic}" "{pattern}"')
        
        # Also add evidence terms for any stance
        for pattern in UNIVERSAL_STANCE_PATTERNS["evidence"]:
            terms.append(f"{topic} {pattern}")
        
        return terms
    
    def _generate_context_terms(self, topic: str, contexts: List[str]) -> List[str]:
        """Generate context-specific terms"""
        terms = []
        
        for context in contexts:
            if context in UNIVERSAL_CONTEXT_PATTERNS:
                for pattern in UNIVERSAL_CONTEXT_PATTERNS[context]:
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