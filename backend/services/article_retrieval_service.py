import asyncio
from typing import List, Dict
import httpx
from newsapi import NewsApiClient
from config import settings
import re
from collections import Counter
from services.stance_detector import stance_detector

class ArticleRetrievalService:
    def __init__(self):
        self.news_api = NewsApiClient(api_key=settings.news_api_key)
        self.category_mappings = self._load_category_mappings()
        self.sentiment_words = self._load_sentiment_words()
    
    def _load_category_mappings(self) -> Dict[str, Dict]:
        """Load comprehensive category mappings for NewsNet categories"""
        return {
            "geopolitics": {
                "search_terms": [
                    "politics", "government", "election", "diplomacy", "foreign policy", 
                    "international relations", "conflict", "war", "peace", "treaty",
                    "israel", "palestine", "ukraine", "russia", "china", "taiwan",
                    "iran", "north korea", "nato", "united nations", "sanctions"
                ],
                "keywords": [
                    "geopolitics", "international", "diplomatic", "conflict", "war",
                    "peace", "treaty", "alliance", "sanctions", "embargo"
                ]
            },
            "economics": {
                "search_terms": [
                    "economy", "economic", "market", "trade", "business", "finance",
                    "federal reserve", "interest rates", "inflation", "gdp", "unemployment",
                    "stock", "stocks", "stock market", "wall street", "bitcoin", "cryptocurrency", "nasdaq", "dow jones", "s&p 500", "investing", "investment", "oil prices",
                    "gold prices", "housing market", "consumer spending", "economic growth"
                ],
                "keywords": [
                    "economic", "financial", "market", "trade", "business", "finance",
                    "monetary", "fiscal", "inflation", "recession", "growth", "stock", "investment"
                ]
            },
            "social_issues": {
                "search_terms": [
                    "social issues", "civil rights", "racial justice", "lgbtq rights",
                    "women rights", "immigration", "refugees", "police reform",
                    "criminal justice", "gun control", "abortion", "voting rights",
                    "education", "healthcare", "minimum wage", "income inequality",
                    "climate change", "environment", "renewable energy", "protest", "protests", "demonstration", "march", "activism"
                ],
                "keywords": [
                    "social", "rights", "justice", "equality", "reform", "policy",
                    "education", "healthcare", "environment", "climate", "protest", "activism"
                ]
            },
            "tech_science": {
                "search_terms": [
                    "technology", "science", "artificial intelligence", "ai", "machine learning",
                    "chatgpt", "openai", "spacex", "nasa", "quantum computing",
                    "robotics", "automation", "social media", "tiktok", "twitter",
                    "youtube", "facebook", "meta", "apple", "google", "microsoft",
                    "tesla", "electric vehicles", "self driving cars"
                ],
                "keywords": [
                    "technology", "science", "innovation", "digital", "automation",
                    "artificial intelligence", "machine learning", "robotics"
                ]
            },
            "health": {
                "search_terms": [
                    "health", "medical", "healthcare", "medicine", "hospital", "doctor",
                    "vaccination", "vaccine", "covid", "coronavirus", "pandemic",
                    "mental health", "obesity", "nutrition", "fitness", "exercise",
                    "pharmaceutical", "drug", "treatment", "surgery"
                ],
                "keywords": [
                    "health", "medical", "healthcare", "medicine", "treatment",
                    "vaccination", "pandemic", "disease", "wellness"
                ]
            },
            "sports": {
                "search_terms": [
                    "sports", "football", "basketball", "baseball", "soccer", "tennis",
                    "olympics", "world cup", "super bowl", "nba", "nfl", "mlb",
                    "nhl", "championship", "tournament", "athlete", "player"
                ],
                "keywords": [
                    "sports", "athletic", "competition", "tournament", "championship",
                    "olympics", "world cup", "league"
                ]
            }
        }
    
    def _load_sentiment_words(self) -> Dict[str, List[str]]:
        """Load comprehensive sentiment words for better analysis"""
        return {
            "positive": [
                # General positive
                "great", "excellent", "amazing", "wonderful", "fantastic", "brilliant", "outstanding",
                "success", "victory", "win", "achievement", "progress", "improvement", "growth",
                "strong", "powerful", "effective", "efficient", "innovative", "revolutionary",
                "hero", "leader", "genius", "visionary", "champion", "defender", "protector",
                "freedom", "liberty", "justice", "equality", "democracy", "rights", "opportunity",
                "prosperity", "wealth", "successful", "thriving", "booming", "flourishing",
                # Political positive
                "patriot", "patriotic", "american", "greatest", "best", "strongest", "united",
                "together", "hope", "change", "reform", "improve", "better", "future", "promise",
                "trust", "honest", "truthful", "transparent", "accountable", "responsible"
            ],
            "negative": [
                # General negative
                "terrible", "awful", "horrible", "disastrous", "catastrophic", "devastating",
                "failure", "defeat", "loss", "collapse", "crisis", "disaster", "scandal",
                "weak", "ineffective", "incompetent", "corrupt", "dishonest", "criminal",
                "villain", "enemy", "threat", "danger", "evil", "tyrant", "dictator",
                "oppression", "injustice", "inequality", "poverty", "suffering", "pain",
                "destruction", "chaos", "anarchy", "corruption", "greed", "selfish",
                # Political negative
                "hate", "racist", "sexist", "bigot", "fascist", "authoritarian", "tyrannical",
                "corrupt", "crooked", "liar", "cheat", "fraud", "criminal", "indictment",
                "guilty", "convicted", "impeachment", "scandal", "controversy", "outrage",
                "disaster", "failure", "incompetent", "unfit", "dangerous", "threat",
                "embarrassment", "shame", "disgrace", "humiliation", "ridiculous", "stupid"
            ],
            "intensifiers": [
                "very", "extremely", "absolutely", "completely", "totally", "utterly",
                "incredibly", "unbelievably", "massively", "hugely", "enormously",
                "especially", "particularly", "especially", "notably", "remarkably"
            ],
            "negators": [
                "not", "no", "never", "none", "neither", "nor", "without", "lacks",
                "fails", "refuses", "denies", "rejects", "opposes", "against", "anti"
            ]
        }
    
    def analyze_topic_sentiment(self, text: str, topic: str, user_view: str = "") -> Dict:
        """Analyze sentiment specifically around the topic and user's view"""
        if not text or not topic:
            return {"score": 0.5, "confidence": 0.0, "sentiment": "neutral"}
        
        text_lower = text.lower()
        topic_lower = topic.lower()
        user_view_lower = user_view.lower()
        
        # Find all mentions of the topic
        topic_mentions = self._find_topic_mentions(text_lower, topic_lower)
        if not topic_mentions:
            return {"score": 0.5, "confidence": 0.0, "sentiment": "neutral"}
        
        # Analyze sentiment around each topic mention
        topic_sentiments = []
        for mention in topic_mentions:
            sentiment = self._analyze_context_sentiment(text_lower, mention, user_view_lower)
            topic_sentiments.append(sentiment)
        
        # Calculate overall sentiment
        if not topic_sentiments:
            return {"score": 0.5, "confidence": 0.0, "sentiment": "neutral"}
        
        avg_sentiment = sum(sentiment["score"] for sentiment in topic_sentiments) / len(topic_sentiments)
        confidence = min(1.0, len(topic_sentiments) / 5.0)  # More mentions = higher confidence
        
        # Determine sentiment label
        if avg_sentiment > 0.7:
            sentiment_label = "very_positive"
        elif avg_sentiment > 0.6:
            sentiment_label = "positive"
        elif avg_sentiment > 0.4:
            sentiment_label = "neutral"
        elif avg_sentiment > 0.3:
            sentiment_label = "negative"
        else:
            sentiment_label = "very_negative"
        
        return {
            "score": avg_sentiment,
            "confidence": confidence,
            "sentiment": sentiment_label,
            "mentions": len(topic_mentions)
        }
    
    def _find_topic_mentions(self, text: str, topic: str) -> List[Dict]:
        """Find all mentions of the topic with their positions"""
        mentions = []
        words = text.split()
        
        for i, word in enumerate(words):
            # Check if word contains the topic
            if topic in word.lower():
                # Get context window around the mention
                start = max(0, i - 5)
                end = min(len(words), i + 6)
                context = words[start:end]
                
                mentions.append({
                    "position": i,
                    "word": word,
                    "context": context,
                    "context_start": start,
                    "context_end": end
                })
        
        return mentions
    
    def _analyze_context_sentiment(self, text: str, mention: Dict, user_view: str) -> Dict:
        """Analyze sentiment in the context around a topic mention"""
        context_words = mention["context"]
        context_text = " ".join(context_words).lower()
        
        # Count positive and negative words in context
        positive_count = sum(1 for word in self.sentiment_words["positive"] 
                           if word in context_text)
        negative_count = sum(1 for word in self.sentiment_words["negative"] 
                           if word in context_text)
        
        # Check for intensifiers and negators
        intensifier_count = sum(1 for word in self.sentiment_words["intensifiers"] 
                              if word in context_text)
        negator_count = sum(1 for word in self.sentiment_words["negators"] 
                          if word in context_text)
        
        # Apply intensifiers and negators
        if negator_count > 0:
            # Negators flip the sentiment
            positive_count, negative_count = negative_count, positive_count
        
        if intensifier_count > 0:
            # Intensifiers amplify the sentiment
            positive_count *= (1 + intensifier_count * 0.5)
            negative_count *= (1 + intensifier_count * 0.5)
        
        # Calculate sentiment score
        total_sentiment_words = positive_count + negative_count
        if total_sentiment_words == 0:
            return {"score": 0.5, "confidence": 0.0}
        
        sentiment_score = positive_count / total_sentiment_words
        
        # Check if user view is mentioned in context (indicates alignment)
        user_view_alignment = 0.0
        if user_view and any(word in context_text for word in user_view.split()):
            user_view_alignment = 0.2  # Slight boost for mentioning user's view
        
        # Adjust score based on user view alignment
        final_score = min(1.0, sentiment_score + user_view_alignment)
        
        return {
            "score": final_score,
            "confidence": min(1.0, total_sentiment_words / 3.0)
        }
    
    def _get_user_view_polarity(self, user_view: str) -> str:
        """Detect if the user view is positive, negative, or neutral toward the topic."""
        user_view = user_view.lower()
        negative_words = [
            'hate', 'bad', 'awful', 'terrible', 'against', 'oppose', 'dislike', 'worse', 'worst',
            'corrupt', 'evil', 'dangerous', 'problem', 'criticize', 'criticising', 'criticizing',
            'should resign', 'should be removed', 'should be jailed', 'should be arrested', 'should be banned',
            'should be impeached', 'should be fired', 'should be stopped', 'should be defeated', 'should lose',
            'should not', 'never', 'no', 'not', 'fail', 'failure', 'liar', 'fraud', 'criminal', 'indictment',
            'guilty', 'convicted', 'impeachment', 'scandal', 'controversy', 'outrage', 'unfit', 'embarrassment',
            'shame', 'disgrace', 'humiliation', 'ridiculous', 'stupid', 'incompetent', 'untrustworthy', 'dishonest'
        ]
        positive_words = [
            'love', 'good', 'great', 'amazing', 'support', 'for', 'like', 'admire', 'best', 'better', 'awesome',
            'honest', 'trust', 'trustworthy', 'leader', 'hero', 'should win', 'should succeed', 'should be president',
            'should be elected', 'should be supported', 'should be praised', 'should be promoted', 'should be protected',
            'should be celebrated', 'should be honored', 'should be respected', 'should be defended', 'should be kept',
            'should be re-elected', 'should stay', 'should continue', 'should be allowed', 'should be free', 'should be safe',
            'should be helped', 'should be saved', 'should be improved', 'should be fixed', 'should be trusted', 'should be believed'
        ]
        for word in negative_words:
            if word in user_view:
                return "negative"
        for word in positive_words:
            if word in user_view:
                return "positive"
        return "neutral"

    def calculate_bias_match(self, article_sentiment: Dict, user_bias: float, user_view: str = "") -> float:
        """Calculate how well an article matches the user's bias preference, inverting logic based on user view polarity."""
        article_score = article_sentiment["score"]
        user_view_polarity = self._get_user_view_polarity(user_view)
        # bias_slider: 0 = challenging, 1 = supporting
        if user_view_polarity == "negative":
            # Supporting: want negative articles; Challenging: want positive articles
            target_sentiment = 0.0 if user_bias > 0.5 else 1.0
        elif user_view_polarity == "positive":
            # Supporting: want positive articles; Challenging: want negative articles
            target_sentiment = 1.0 if user_bias > 0.5 else 0.0
        else:
            # Neutral: prefer neutral articles
            target_sentiment = 0.5
        return 1.0 - abs(article_score - target_sentiment)
    
    async def search_articles(self, query: str, bias: float = 0.5, limit: int = 20) -> List[Dict]:
        """Search articles with intelligent stance detection and bias analysis"""
        try:
            print(f"🔍 SEARCH: Starting search for query: '{query}' with bias: {bias}")
            
            # Extract topic and user view from query
            topic, user_view = self._extract_topic_and_view(query)
            print(f"🔍 SEARCH: Extracted topic: '{topic}', user_view: '{user_view}'")
            
            # Create user belief for stance detection
            user_belief = f"{topic} {user_view}".strip()
            print(f"🔍 SEARCH: User belief: '{user_belief}'")
            
            # Determine search strategy based on user view
            if self._is_political_view(user_view):
                # For political views, search for political content
                search_terms = [
                    f"{topic} politics",
                    f"{topic} election",
                    f"{topic} president",
                    f"{topic} government",
                    f"{topic} policy",
                    f"{topic} {user_view}"  # Include user view in search
                ]
            else:
                # For non-political views, search broadly
                search_terms = [topic, f"{topic} {user_view}"]
            
            print(f"🔍 SEARCH: Using search terms: {search_terms}")
            
            # Search for articles using multiple terms
            all_articles = []
            for search_term in search_terms[:3]:  # Use first 3 search terms
                try:
                    print(f"🔍 SEARCH: Searching News API for: '{search_term}'")
                    response = self.news_api.get_everything(
                        q=search_term,
                        language='en',
                        sort_by='relevancy',
                        page_size=min(limit * 2, 50)  # Get more articles to filter
                    )
                    articles = response.get('articles', [])
                    print(f"🔍 SEARCH: Got {len(articles)} articles for '{search_term}'")
                    all_articles.extend(articles)
                except Exception as e:
                    print(f"🔍 SEARCH: Error searching for '{search_term}': {e}")
                    continue
            
            print(f"🔍 SEARCH: Total articles before deduplication: {len(all_articles)}")
            
            # Remove duplicates based on URL
            seen_urls = set()
            unique_articles = []
            for article in all_articles:
                if article.get('url') not in seen_urls:
                    seen_urls.add(article.get('url'))
                    unique_articles.append(article)
            
            print(f"🔍 SEARCH: Unique articles after deduplication: {len(unique_articles)}")
            
            if not unique_articles:
                print("🔍 SEARCH: No articles found, returning empty list")
                return []
            
            # Analyze each article for stance and bias
            analyzed_articles = []
            for article in unique_articles:
                # Combine title, description, and content for analysis
                content_text = f"{article.get('title', '')} {article.get('description', '')} {article.get('content', '')}"
                
                # Get stance analysis using new stance detector
                stance_analysis = stance_detector.classify_stance(content_text, user_belief)
                
                # Calculate bias match using clean scoring matrix
                bias_match = self._calculate_bias_match(stance_analysis, bias)
                
                # Add analysis to article
                article['bias_analysis'] = {
                    'stance': stance_analysis["stance"],
                    'stance_confidence': stance_analysis["confidence"],
                    'stance_method': stance_analysis["method"],
                    'stance_evidence': stance_analysis.get("evidence", []),
                    'bias_match': bias_match,
                    'user_bias_preference': bias,
                    'user_belief': user_belief,
                    'analysis_method': 'stance_detection'
                }
                
                analyzed_articles.append(article)
            
            print(f"🔍 SEARCH: Analyzed {len(analyzed_articles)} articles")
            
            # Sort by bias match (how well they match user's preference)
            analyzed_articles.sort(key=lambda x: x['bias_analysis']['bias_match'], reverse=True)
            
            # Return top articles
            result = analyzed_articles[:limit]
            print(f"🔍 SEARCH: Returning {len(result)} articles")
            return result
            
        except Exception as e:
            print(f"🔍 SEARCH: Error searching articles: {e}")
            return []
    
    def _calculate_bias_match(self, stance_analysis: Dict, bias: float) -> float:
        """
        Calculate bias match using clean scoring matrix
        
        bias: 0.0 = challenging views, 1.0 = supporting views
        stance: "support", "oppose", "neutral"
        """
        stance = stance_analysis["stance"]
        confidence = stance_analysis["confidence"]
        
        # Clean scoring matrix
        if bias == 0.0:  # User wants challenging views
            if stance == "oppose":
                return 1.0 * confidence  # Perfect match
            elif stance == "support":
                return 0.0  # Wrong direction
            else:  # neutral
                return 0.5 * confidence
                
        elif bias == 1.0:  # User wants supporting views
            if stance == "support":
                return 1.0 * confidence  # Perfect match
            elif stance == "oppose":
                return 0.0  # Wrong direction
            else:  # neutral
                return 0.5 * confidence
                
        else:  # Intermediate bias values
            if stance == "support":
                # Interpolate: more bias = more support
                return bias * confidence
            elif stance == "oppose":
                # Interpolate: more bias = less oppose
                return (1.0 - bias) * confidence
            else:  # neutral
                return 0.5 * confidence
    
    def _is_political_view(self, user_view: str) -> bool:
        """Check if the user view is political in nature"""
        political_keywords = [
            'hate', 'love', 'support', 'oppose', 'against', 'for', 'believe', 'think',
            'good', 'bad', 'great', 'terrible', 'amazing', 'awful', 'leader', 'president',
            'politics', 'policy', 'government', 'election', 'vote', 'democrat', 'republican',
            'liberal', 'conservative', 'right', 'wrong', 'justice', 'freedom', 'rights'
        ]
        
        user_view_lower = user_view.lower()
        return any(keyword in user_view_lower for keyword in political_keywords)
    
    def _extract_topic_and_view(self, query: str) -> tuple[str, str]:
        """Extract the main topic and user view from the search query"""
        # Simple extraction - first word is usually the topic
        words = query.split()
        if len(words) == 0:
            return "", ""
        
        # First word is the topic
        topic = words[0]
        
        # Rest is the user view
        user_view = " ".join(words[1:]) if len(words) > 1 else ""
        
        return topic, user_view
    
    async def fetch_articles_for_category(self, category: str, limit: int = 30) -> List[Dict]:
        """Fetch articles from News API for a given category"""
        try:
            if category not in self.category_mappings:
                print(f"Unknown category: {category}")
                return []
            
            category_config = self.category_mappings[category]
            search_terms = category_config["search_terms"]
            
            # Create a comprehensive search query
            query = " OR ".join(search_terms[:10])  # Limit to first 10 terms to avoid query too long
            
            # Search for articles
            response = self.news_api.get_everything(
                q=query,
                language='en',
                sort_by='publishedAt',
                page_size=limit
            )
            
            return response['articles']
        except Exception as e:
            print(f"Error fetching articles for category {category}: {e}")
            return []
    
    async def fetch_articles_for_multiple_categories(self, categories: List[str], limit_per_category: int = 30) -> Dict[str, List[Dict]]:
        """Fetch articles for multiple categories"""
        results = {}
        
        for category in categories:
            articles = await self.fetch_articles_for_category(category, limit_per_category)
            results[category] = articles
        
        return results
    
    def extract_domain_from_url(self, url: str) -> str:
        """Extract domain from URL"""
        from urllib.parse import urlparse
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except:
            return ""
    
    def clean_article_content(self, content: str) -> str:
        """Clean and normalize article content"""
        if not content:
            return ""
        
        # Remove common unwanted patterns
        content = content.replace("[+", "").replace(" chars]", "")
        content = content.strip()
        
        return content 