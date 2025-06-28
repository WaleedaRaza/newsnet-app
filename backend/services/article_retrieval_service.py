import asyncio
from typing import List, Dict, Optional
import httpx
from newsapi import NewsApiClient
from config import settings
import re
from collections import Counter
from services.advanced_stance_detector import advanced_stance_detector
from datetime import datetime, timedelta
from services.universal_search_generator import UniversalSearchGenerator
from services.universal_relevance_scorer import UniversalRelevanceScorer
import json
import os
import time
from functools import lru_cache

# Import the new free news sources
try:
    from pygooglenews import GoogleNews
except ImportError:
    print("⚠️ pygooglenews not installed, skipping Google News")
    GoogleNews = None

class ArticleRetrievalService:
    def __init__(self):
        # Primary NewsAPI
        self.news_api = NewsApiClient(api_key=settings.news_api_key)
        self.search_generator = UniversalSearchGenerator()
        self.relevance_scorer = UniversalRelevanceScorer()
        self._load_category_mappings()
        self._load_sentiment_words()
        
        # Smart caching system
        self.cache_file = "article_cache.json"
        self.cache_duration_hours = 24
        self.request_count = 0
        self.last_request_time = 0
        
        # HTTP client for alternative APIs
        self.http_client = httpx.AsyncClient(timeout=30.0)
        
        # Initialize Google News
        self.google_news = GoogleNews() if GoogleNews else None
        
        # Load cache
        self._load_cache()
        
        print(f"🔑 Using NewsAPI + Google News + GDELT + RSS (all free!)")
    
    def _load_cache(self):
        """Load cached articles from file"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    self.cache = json.load(f)
                print(f"📦 Loaded {len(self.cache)} cached queries")
            else:
                self.cache = {}
        except Exception as e:
            print(f"⚠️ Error loading cache: {e}")
            self.cache = {}
    
    def _save_cache(self):
        """Save articles to cache file"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            print(f"⚠️ Error saving cache: {e}")
    
    def _get_cache_key(self, query: str, bias: float) -> str:
        """Generate cache key for query and bias"""
        return f"{query.lower().strip()}_{bias:.2f}"
    
    def _is_cache_valid(self, cache_entry: Dict) -> bool:
        """Check if cache entry is still valid"""
        cache_time = datetime.fromisoformat(cache_entry['timestamp'])
        return datetime.now() - cache_time < timedelta(hours=self.cache_duration_hours)
    
    def _should_use_fallback(self) -> bool:
        """Check if we should use fallback APIs due to rate limiting"""
        return self.request_count > 80
    
    async def _search_newsapi(self, search_term: str, **kwargs) -> Optional[Dict]:
        """Search using NewsAPI with rate limit checking"""
        try:
            if self._should_use_fallback():
                print(f"⚠️ Approaching rate limit ({self.request_count}/100), using free sources")
                return None
            
            # Add delay between requests
            current_time = time.time()
            if current_time - self.last_request_time < 1:
                time.sleep(1)
            
            print(f"🔍 Making NewsAPI request for: '{search_term}' (request #{self.request_count + 1})")
            response = self.news_api.get_everything(q=search_term, **kwargs)
            
            self.request_count += 1
            self.last_request_time = current_time
            
            return response
                
        except Exception as e:
            error_msg = str(e).lower()
            if 'rate' in error_msg or 'limit' in error_msg:
                print(f"⚠️ NewsAPI rate limit hit: {e}")
                return None
            else:
                print(f"❌ NewsAPI error: {e}")
                return None
    
    async def _search_google_news(self, search_term: str, **kwargs) -> List[Dict]:
        """Search using Google News (unlimited, no API key needed!)"""
        if not self.google_news:
            return []
        
        try:
            print(f"🔍 Searching Google News for: '{search_term}'")
            
            # Use Google News search with recent results (fix the API call)
            result = self.google_news.search(search_term, when='7d')
            
            articles = []
            for entry in result['entries']:
                # Clean the title and description
                title = entry.get('title', '').strip()
                description = entry.get('summary', '').strip()
                
                # Skip articles that are clearly irrelevant
                if not title or len(title) < 10:
                    continue
                
                # Basic relevance check - must contain key terms
                search_lower = search_term.lower()
                title_lower = title.lower()
                desc_lower = description.lower()
                
                # Check if article contains search terms
                if not (any(word in title_lower for word in search_lower.split() if len(word) > 3) or 
                       any(word in desc_lower for word in search_lower.split() if len(word) > 3)):
                    continue
                
                articles.append({
                    'title': title,
                    'description': description,
                    'url': entry.get('link', ''),
                    'urlToImage': '',  # Google News doesn't provide images
                    'publishedAt': entry.get('published', datetime.now().isoformat()),
                    'source': {'name': entry.get('source', {}).get('title', 'Google News')},
                    'content': f"{title}. {description}"
                })
                
                # Limit to 5 articles per search to avoid overwhelming
                if len(articles) >= 5:
                    break
            
            print(f"🔍 Google News found {len(articles)} relevant articles")
            return articles
            
        except Exception as e:
            print(f"❌ Google News error: {e}")
            return []
    
    async def _search_gdelt(self, search_term: str, **kwargs) -> List[Dict]:
        """Search using GDELT Doc API (global news database)"""
        try:
            print(f"🔍 Searching GDELT for: '{search_term}'")
            
            # GDELT Doc API endpoint
            url = "https://api.gdeltproject.org/api/v2/doc/doc"
            
            params = {
                'query': search_term,
                'mode': 'artlist',
                'maxrecords': kwargs.get('page_size', 10),
                'format': 'json',
                'sort': 'hybridrel'
            }
            
            response = await self.http_client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            articles = []
            if 'articles' in data:
                for article in data['articles']:
                    articles.append({
                        'title': article.get('title', ''),
                        'description': article.get('seendate', ''),
                        'url': article.get('url', ''),
                        'urlToImage': '',
                        'publishedAt': article.get('seendate', datetime.now().isoformat()),
                        'source': {'name': article.get('domain', 'GDELT')},
                        'content': article.get('title', '')
                    })
            
            print(f"🔍 GDELT found {len(articles)} articles")
            return articles
            
        except Exception as e:
            print(f"❌ GDELT error: {e}")
            return []
    
    async def _search_enhanced_rss(self, search_term: str, **kwargs) -> List[Dict]:
        """Search using enhanced RSS feeds with better parsing"""
        try:
            print(f"🔍 Searching enhanced RSS feeds for: '{search_term}'")
            
            # Enhanced RSS feeds with better coverage
            rss_feeds = [
                'https://feeds.bbci.co.uk/news/rss.xml',
                'https://rss.cnn.com/rss/edition.rss',
                'https://feeds.reuters.com/Reuters/worldNews',
                'https://feeds.npr.org/1001/rss.xml',
                'https://feeds.feedburner.com/techcrunch',
                'https://feeds.arstechnica.com/arstechnica/index',
                'https://feeds.foxnews.com/foxnews/latest',
                'https://rss.nytimes.com/services/xml/rss/nyt/World.xml',
                'https://feeds.washingtonpost.com/rss/world',
                'https://feeds.theguardian.com/theguardian/world/rss'
            ]
            
            all_articles = []
            
            for feed_url in rss_feeds:
                try:
                    response = await self.http_client.get(feed_url)
                    response.raise_for_status()
                    
                    # Parse RSS content with better matching
                    articles = self._parse_enhanced_rss_content(response.text, search_term, feed_url)
                    all_articles.extend(articles)
                        
                except Exception as e:
                    print(f"❌ RSS feed error for {feed_url}: {e}")
                    continue
            
            print(f"🔍 Enhanced RSS feeds found {len(all_articles)} relevant articles")
            return all_articles
            
        except Exception as e:
            print(f"❌ Enhanced RSS search error: {e}")
            return []
    
    def _parse_enhanced_rss_content(self, content: str, search_term: str, feed_url: str) -> List[Dict]:
        """Enhanced RSS content parsing with STRICT relevance filtering"""
        articles = []
        
        try:
            import re
            
            # Extract items from RSS
            item_pattern = r'<item>(.*?)</item>'
            items = re.findall(item_pattern, content, re.DOTALL)
            
            # Clean and normalize search terms
            search_words = [word.lower().strip() for word in search_term.lower().split() if len(word) > 2]
            search_phrase = search_term.lower().strip()
            
            print(f"🔍 RSS PARSING: Looking for words: {search_words}")
            print(f"🔍 RSS PARSING: Looking for phrase: '{search_phrase}'")
            
            for item in items:
                # Extract title
                title_match = re.search(r'<title>(.*?)</title>', item, re.DOTALL)
                title = title_match.group(1).strip() if title_match else ''
                
                # Extract description
                desc_match = re.search(r'<description>(.*?)</description>', item, re.DOTALL)
                description = desc_match.group(1).strip() if desc_match else ''
                
                # Extract link
                link_match = re.search(r'<link>(.*?)</link>', item, re.DOTALL)
                link = link_match.group(1).strip() if link_match else ''
                
                # Extract pubDate
                date_match = re.search(r'<pubDate>(.*?)</pubDate>', item, re.DOTALL)
                pub_date = date_match.group(1).strip() if date_match else datetime.now().isoformat()
                
                # Clean HTML tags from title and description
                title_clean = re.sub(r'<[^>]+>', '', title)
                desc_clean = re.sub(r'<[^>]+>', '', description)
                
                # Combine for analysis
                full_text = f"{title_clean} {desc_clean}".lower()
                
                # STRICT relevance checking - article MUST contain search terms
                word_matches = sum(1 for word in search_words if word in full_text)
                phrase_match = search_phrase in full_text
                
                # Article must have at least 2 word matches OR the full phrase
                is_relevant = word_matches >= 2 or phrase_match
                
                print(f"🔍 RSS PARSING: '{title_clean[:50]}...' - Words: {word_matches}, Phrase: {phrase_match}, Relevant: {is_relevant}")
                
                if is_relevant:
                    # Determine source name from feed URL
                    source_name = self._get_enhanced_source_name(feed_url)
                    
                    articles.append({
                        'title': title_clean,
                        'description': desc_clean,
                        'url': link,
                        'urlToImage': '',
                        'publishedAt': pub_date,
                        'source': {'name': source_name},
                        'content': f"{title_clean}. {desc_clean}"
                    })
                    
                    # Limit to 2 articles per feed to avoid overwhelming
                    if len(articles) >= 2:
                        break
            
        except Exception as e:
            print(f"❌ Enhanced RSS parsing error: {e}")
        
        return articles
    
    def _get_enhanced_source_name(self, feed_url: str) -> str:
        """Enhanced source name extraction"""
        if 'bbci.co.uk' in feed_url:
            return 'BBC News'
        elif 'cnn.com' in feed_url:
            return 'CNN'
        elif 'reuters.com' in feed_url:
            return 'Reuters'
        elif 'npr.org' in feed_url:
            return 'NPR'
        elif 'techcrunch' in feed_url:
            return 'TechCrunch'
        elif 'arstechnica' in feed_url:
            return 'Ars Technica'
        elif 'foxnews.com' in feed_url:
            return 'Fox News'
        elif 'nytimes.com' in feed_url:
            return 'New York Times'
        elif 'washingtonpost.com' in feed_url:
            return 'Washington Post'
        elif 'theguardian.com' in feed_url:
            return 'The Guardian'
        else:
            return 'RSS Feed'
    
    def _load_category_mappings(self) -> Dict[str, Dict]:
        """Load category mappings for article categorization"""
        self.category_mappings = {
            "politics": {
                "keywords": ["politics", "government", "election", "president", "congress", "senate", "policy", "legislation"],
                "sources": ["CNN", "Fox News", "MSNBC", "BBC", "Reuters", "Associated Press"]
            },
            "technology": {
                "keywords": ["technology", "tech", "AI", "artificial intelligence", "software", "hardware", "digital", "innovation"],
                "sources": ["TechCrunch", "Wired", "The Verge", "Ars Technica", "MIT Technology Review"]
            },
            "science": {
                "keywords": ["science", "research", "study", "scientific", "discovery", "experiment", "laboratory"],
                "sources": ["Nature", "Science", "Scientific American", "New Scientist", "Science Daily"]
            },
            "business": {
                "keywords": ["business", "economy", "finance", "market", "stock", "investment", "company", "corporate"],
                "sources": ["Wall Street Journal", "Financial Times", "Bloomberg", "CNBC", "Forbes"]
            },
            "health": {
                "keywords": ["health", "medical", "medicine", "healthcare", "disease", "treatment", "hospital", "doctor"],
                "sources": ["Medical News Today", "Healthline", "WebMD", "Mayo Clinic", "NIH"]
            }
        }
    
    def _load_sentiment_words(self) -> Dict[str, List[str]]:
        """Load sentiment word lists for analysis"""
        self.sentiment_words = {
            "positive": [
                "good", "great", "excellent", "amazing", "wonderful", "fantastic", "outstanding",
                "brilliant", "genius", "revolutionary", "groundbreaking", "pioneering", "cutting-edge",
                "state-of-the-art", "world-class", "premier", "premium", "elite", "superior",
                "beneficial", "helpful", "useful", "valuable", "important", "essential", "necessary",
                "vital", "crucial", "critical", "indispensable", "irreplaceable", "unique"
            ],
            "negative": [
                "bad", "terrible", "awful", "horrible", "disgusting", "shameful", "unacceptable",
                "unjust", "unfair", "biased", "prejudiced", "racist", "sexist", "homophobic",
                "transphobic", "xenophobic", "fascist", "authoritarian", "dictatorial", "tyrannical",
                "oppressive", "repressive", "suppressive", "censorship", "propaganda", "lies",
                "deception", "manipulation", "brainwashing", "indoctrination", "radicalization"
            ]
        }
    
    async def search_articles(self, query: str, bias: float = 0.5, limit: int = 20) -> List[Dict]:
        """Universal search that works for ANY topic"""
        try:
            print(f"🔍 UNIVERSAL SEARCH: Starting search for query: '{query}' with bias: {bias}")
            
            # Check cache first
            cache_key = self._get_cache_key(query, bias)
            if cache_key in self.cache and self._is_cache_valid(self.cache[cache_key]):
                print(f"📦 Using cached results for: '{query}'")
                cached_articles = self.cache[cache_key]['articles']
                return cached_articles[:limit]
            
            # Extract topic and user view from query
            topic, user_view = self._extract_topic_and_view(query)
            print(f"🔍 UNIVERSAL SEARCH: Extracted topic: '{topic}', user_view: '{user_view}'")
            
            # Generate universal search terms
            search_terms = self.search_generator.generate_search_terms(query, user_view, bias)
            print(f"🔍 UNIVERSAL SEARCH: Generated {len(search_terms)} universal search terms")
            
            # Search using multiple strategies (recent + historical)
            all_articles = await self._search_multiple_strategies(search_terms, limit)
            print(f"🔍 UNIVERSAL SEARCH: Retrieved {len(all_articles)} articles")
            
            # If no articles found, try fallback search
            if not all_articles:
                print("⚠️ No articles found, trying fallback search...")
                all_articles = await self._fallback_search(topic, limit)
            
            # Analyze and score articles
            analyzed_articles = await self._analyze_articles(all_articles, topic, user_view, bias)
            print(f"🔍 UNIVERSAL SEARCH: Analyzed {len(analyzed_articles)} articles")
            
            # Sort by final score and return
            analyzed_articles.sort(key=lambda x: x['bias_analysis']['final_score'], reverse=True)
            result = analyzed_articles[:limit]
            
            # Cache the results
            self.cache[cache_key] = {
                'articles': result,
                'timestamp': datetime.now().isoformat()
            }
            self._save_cache()
            
            print(f"🔍 UNIVERSAL SEARCH: Returning {len(result)} articles")
            return result
            
        except Exception as e:
            print(f"🔍 UNIVERSAL SEARCH: Error: {e}")
            return []
    
    async def _search_multiple_strategies(self, search_terms: List[str], limit: int) -> List[Dict]:
        """Search using multiple strategies for better coverage"""
        all_articles = []
        
        # Strategy 1: Google News FIRST (most reliable, no rate limits)
        if self.google_news:
            print(f"🔍 UNIVERSAL SEARCH: Starting with Google News (most reliable)")
            for search_term in search_terms[:3]:  # Use top 3 search terms
                try:
                    print(f"🔍 UNIVERSAL SEARCH: Searching Google News for: '{search_term}'")
                    articles = await self._search_google_news(
                        search_term=search_term,
                        page_size=min(limit - len(all_articles), 10)
                    )
                    if articles:
                        print(f"🔍 UNIVERSAL SEARCH: Google News got {len(articles)} articles for '{search_term}'")
                        all_articles.extend(articles)
                        if len(all_articles) >= limit:
                            break  # Stop if we have enough articles
                except Exception as e:
                    print(f"🔍 UNIVERSAL SEARCH: Error searching Google News for '{search_term}': {e}")
                    continue
        
        # Strategy 2: NewsAPI (if not rate limited)
        if len(all_articles) < limit and not self._should_use_fallback():
            print(f"🔍 UNIVERSAL SEARCH: Trying NewsAPI, current articles: {len(all_articles)}")
            for search_term in search_terms[:2]:  # Use top 2 search terms
                try:
                    print(f"🔍 UNIVERSAL SEARCH: Searching NewsAPI for: '{search_term}'")
                    response = await self._search_newsapi(
                        search_term=search_term,
                        language='en',
                        sort_by='relevancy',
                        page_size=min(limit - len(all_articles), 10),
                        from_param=(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
                    )
                    
                    if response:
                        articles = response.get('articles', [])
                        print(f"🔍 UNIVERSAL SEARCH: NewsAPI got {len(articles)} articles for '{search_term}'")
                        all_articles.extend(articles)
                        if len(all_articles) >= limit:
                            break
                    else:
                        print(f"⚠️ NewsAPI no response for: '{search_term}'")
                        
                except Exception as e:
                    print(f"🔍 UNIVERSAL SEARCH: Error searching NewsAPI for '{search_term}': {e}")
                    continue
        else:
            print("⚠️ NewsAPI rate limited or enough articles found, skipping")
        
        # Strategy 3: Enhanced RSS feeds (only if we need more articles)
        if len(all_articles) < limit:
            print(f"🔍 UNIVERSAL SEARCH: Enhanced RSS feeds needed, current articles: {len(all_articles)}")
            for search_term in search_terms[:2]:  # Use top 2 search terms
                try:
                    print(f"🔍 UNIVERSAL SEARCH: Trying Enhanced RSS feeds for: '{search_term}'")
                    articles = await self._search_enhanced_rss(search_term=search_term)
                    if articles:
                        print(f"🔍 UNIVERSAL SEARCH: Enhanced RSS feeds got {len(articles)} articles for '{search_term}'")
                        all_articles.extend(articles)
                        if len(all_articles) >= limit:
                            break
                except Exception as e:
                    print(f"🔍 UNIVERSAL SEARCH: Error searching Enhanced RSS feeds for '{search_term}': {e}")
                    continue
        
        # Strategy 4: GDELT (fallback)
        if len(all_articles) < limit and settings.gdelt_api_key:
            for search_term in search_terms[:1]:  # Use only top search term
                try:
                    print(f"🔍 UNIVERSAL SEARCH: Trying GDELT for: '{search_term}'")
                    articles = await self._search_gdelt(
                        search_term=search_term,
                        page_size=min(limit - len(all_articles), 5)
                    )
                    if articles:
                        print(f"🔍 UNIVERSAL SEARCH: GDELT got {len(articles)} articles for '{search_term}'")
                        all_articles.extend(articles)
                        if len(all_articles) >= limit:
                            break
                except Exception as e:
                    print(f"🔍 UNIVERSAL SEARCH: Error searching GDELT for '{search_term}': {e}")
                    continue
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            if article.get('url') not in seen_urls:
                seen_urls.add(article.get('url'))
                unique_articles.append(article)
        
        print(f"🔍 UNIVERSAL SEARCH: Total unique articles after deduplication: {len(unique_articles)}")
        return unique_articles[:limit]  # Ensure we don't exceed limit
    
    async def _analyze_articles(self, articles: List[Dict], topic: str, user_view: str, bias: float) -> List[Dict]:
        """Analyze articles for stance, relevance, and bias match"""
        analyzed_articles = []
        
        for article in articles:
            try:
                # Combine title, description, and content for analysis
                content_text = f"{article.get('title', '')} {article.get('description', '')} {article.get('content', '')}"
                
                # Create user belief for stance detection
                user_belief = f"{topic} {user_view}".strip()
                
                print(f"🔍 UNIVERSAL SEARCH: Analyzing article: {article.get('title', '')[:50]}...")
                
                # Get stance analysis using advanced stance detector
                stance_result = await advanced_stance_detector.detect_stance(user_belief, content_text)
                
                # Convert StanceResult to dict format for compatibility
                stance_analysis = {
                    "stance": stance_result.stance,
                    "confidence": stance_result.confidence,
                    "method": stance_result.method,
                    "evidence": stance_result.evidence
                }
                
                # Calculate bias match using existing logic
                bias_match = self._calculate_bias_match(stance_analysis, bias, user_view)
                
                # Calculate relevance score using universal scorer
                relevance_score = self.relevance_scorer.calculate_relevance_score(content_text, topic, user_view)
                
                # Calculate final score (bias match + relevance)
                final_score = (bias_match * 0.7) + (relevance_score * 0.3)
                
                # Add analysis to article
                article['bias_analysis'] = {
                    'stance': stance_analysis["stance"],
                    'stance_confidence': stance_analysis["confidence"],
                    'stance_method': stance_analysis["method"],
                    'stance_evidence': stance_analysis.get("evidence", []),
                    'bias_match': bias_match,
                    'relevance_score': relevance_score,
                    'final_score': final_score,
                    'user_bias_preference': bias,
                    'user_belief': user_belief,
                    'analysis_method': 'universal_stance_detection'
                }
                
                analyzed_articles.append(article)
                
            except Exception as e:
                print(f"🔍 UNIVERSAL SEARCH: Error analyzing article: {e}")
                continue
        
        return analyzed_articles
    
    def _extract_topic_and_view(self, query: str) -> tuple[str, str]:
        """Extract topic and user view from query"""
        # Simple extraction - first word is topic, rest is view
        words = query.split()
        if len(words) < 2:
            return words[0] if words else "news", ""
        
        topic = words[0]
        user_view = " ".join(words[1:])
        
        return topic, user_view
    
    def _calculate_bias_match(self, stance_analysis: Dict, bias: float, user_view: str = "") -> float:
        """
        Calculate bias match using clean scoring matrix
        
        bias: 0.0 = challenging views, 1.0 = supporting views
        stance: "support", "oppose", "neutral"
        user_view: The user's view about the topic
        """
        stance = stance_analysis["stance"]
        confidence = stance_analysis["confidence"]
        
        # Determine if user has a negative or positive view
        user_has_negative_view = any(word in user_view.lower() for word in ['hate', 'terrible', 'awful', 'bad', 'wrong', 'dislike'])
        user_has_positive_view = any(word in user_view.lower() for word in ['love', 'great', 'amazing', 'good', 'right', 'like'])
        
        # Clean scoring matrix with user view consideration
        if bias == 0.0:  # User wants challenging views
            if user_has_negative_view:
                # User hates the topic, so challenging views = articles that support the topic
                if stance == "support":
                    return 1.0 * confidence  # Perfect match - supports what user hates
                elif stance == "oppose":
                    return 0.0  # Wrong direction - opposes what user hates
                else:  # neutral
                    return 0.5 * confidence
            elif user_has_positive_view:
                # User loves the topic, so challenging views = articles that oppose the topic
                if stance == "oppose":
                    return 1.0 * confidence  # Perfect match - opposes what user loves
                elif stance == "support":
                    return 0.0  # Wrong direction - supports what user loves
                else:  # neutral
                    return 0.5 * confidence
            else:
                # No clear user view, use original logic
                if stance == "oppose":
                    return 1.0 * confidence
                elif stance == "support":
                    return 0.0
                else:  # neutral
                    return 0.5 * confidence
                
        elif bias == 1.0:  # User wants supporting views
            if user_has_negative_view:
                # User hates the topic, so supporting views = articles that oppose the topic
                if stance == "oppose":
                    return 1.0 * confidence  # Perfect match - opposes what user hates
                elif stance == "support":
                    return 0.0  # Wrong direction - supports what user hates
                else:  # neutral
                    return 0.5 * confidence
            elif user_has_positive_view:
                # User loves the topic, so supporting views = articles that support the topic
                if stance == "support":
                    return 1.0 * confidence  # Perfect match - supports what user loves
                elif stance == "oppose":
                    return 0.0  # Wrong direction - opposes what user loves
                else:  # neutral
                    return 0.5 * confidence
            else:
                # No clear user view, use original logic
                if stance == "support":
                    return 1.0 * confidence
                elif stance == "oppose":
                    return 0.0
                else:  # neutral
                    return 0.5 * confidence
                
        else:  # Intermediate bias values
            if user_has_negative_view:
                # User hates the topic
                if stance == "oppose":
                    # More bias = more oppose (supporting user's negative view)
                    return bias * confidence
                elif stance == "support":
                    # More bias = less support (challenging user's negative view)
                    return (1.0 - bias) * confidence
                else:  # neutral
                    return 0.5 * confidence
            elif user_has_positive_view:
                # User loves the topic
                if stance == "support":
                    # More bias = more support (supporting user's positive view)
                    return bias * confidence
                elif stance == "oppose":
                    # More bias = less oppose (challenging user's positive view)
                    return (1.0 - bias) * confidence
                else:  # neutral
                    return 0.5 * confidence
            else:
                # No clear user view, use linear interpolation
                if stance == "support":
                    return bias * confidence
                elif stance == "oppose":
                    return (1.0 - bias) * confidence
                else:  # neutral
                    return 0.5 * confidence
    
    def extract_domain_from_url(self, url: str) -> str:
        """Extract domain from URL"""
        if not url:
            return "unknown"
        
        # Remove protocol
        if url.startswith(('http://', 'https://')):
            url = url.split('://', 1)[1]
        
        # Remove path and get domain
        domain = url.split('/')[0]
        
        # Remove www. prefix
        if domain.startswith('www.'):
            domain = domain[4:]
        
        return domain
    
    def clean_article_content(self, content: str) -> str:
        """Clean article content for analysis"""
        if not content:
            return ""
        
        # Remove extra whitespace
        content = ' '.join(content.split())
        
        # Remove common HTML artifacts
        content = content.replace('&nbsp;', ' ')
        content = content.replace('&amp;', '&')
        content = content.replace('&lt;', '<')
        content = content.replace('&gt;', '>')
        
        return content
    
    async def _fallback_search(self, topic: str, limit: int) -> List[Dict]:
        """Fallback search using real APIs when main search fails"""
        try:
            print(f"🔄 FALLBACK SEARCH: Trying real APIs for '{topic}'")
            
            # Try GDELT first
            if settings.gdelt_api_key:
                articles = await self._search_gdelt(
                    search_term=topic,
                    page_size=limit
                )
                if articles:
                    print(f"🔄 FALLBACK SEARCH: GDELT found {len(articles)} articles")
                    return articles
            
            # Try Google News
            if self.google_news:
                articles = await self._search_google_news(
                    search_term=topic,
                    page_size=limit
                )
                if articles:
                    print(f"🔄 FALLBACK SEARCH: Google News found {len(articles)} articles")
                    return articles
            
            # Try Enhanced RSS feeds
            articles = await self._search_enhanced_rss(search_term=topic)
            if articles:
                print(f"🔄 FALLBACK SEARCH: Enhanced RSS feeds found {len(articles)} articles")
                return articles
            
            print("❌ FALLBACK SEARCH: No real articles found from any source")
            return []
            
        except Exception as e:
            print(f"🔄 FALLBACK SEARCH: Error: {e}")
            return [] 