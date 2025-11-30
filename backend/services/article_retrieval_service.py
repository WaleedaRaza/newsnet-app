import asyncio
import json
import aiohttp
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pygooglenews import GoogleNews
import time
from functools import lru_cache
from .universal_search_generator import UniversalSearchTermGenerator
from newsapi import NewsApiClient
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings
import re
from collections import Counter
from .advanced_stance_detector import advanced_stance_detector
from .universal_relevance_scorer import UniversalRelevanceScorer

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
        self.relevance_scorer = UniversalRelevanceScorer()
        self._load_category_mappings()
        self._load_sentiment_words()
        
        # Smart caching system
        self.cache_file = "article_cache.json"
        self.cache_duration_hours = 24
        self.request_count = 0
        self.last_request_time = 0
        
        # HTTP client for alternative APIs
        self.http_client = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
        
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
            async with self.http_client.get(f"https://newsapi.org/v2/everything?q={search_term}&apiKey={settings.news_api_key}") as response:
                response.raise_for_status()
                data = await response.json()
                
                self.request_count += 1
                self.last_request_time = current_time
                
                return data
                
        except Exception as e:
            error_msg = str(e).lower()
            if 'rate' in error_msg or 'limit' in error_msg:
                print(f"⚠️ NewsAPI rate limit hit: {e}")
                return None
            else:
                print(f"❌ NewsAPI error: {e}")
                return None
    
    async def _search_google_news(self, search_term: str, **kwargs) -> List[Dict]:
        """Search using Google News with ADVANCED features from pygooglenews"""
        try:
            print(f"🔍 ADVANCED Google News search for: '{search_term}'")
            
            # Use ALL advanced features from pygooglenews
            gn = GoogleNews()
            
            # Advanced search with multiple strategies
            articles = []
            
            # Strategy 1: Exact phrase search with time filtering
            try:
                print(f"🔍 Google News Strategy 1: Exact phrase '{search_term}' (last 24h)")
                result = gn.search(f'"{search_term}"', when='24h')
                if result and result.get('entries'):
                    for entry in result['entries']:
                        articles.append({
                            'title': entry.get('title', ''),
                            'description': entry.get('summary', ''),
                            'url': entry.get('link', ''),
                            'urlToImage': '',
                            'publishedAt': entry.get('published', datetime.now().isoformat()),
                            'source': {'name': entry.get('source', {}).get('title', 'Google News')},
                            'content': entry.get('summary', '')
                        })
                    print(f"🔍 Strategy 1 found {len(result['entries'])} articles")
            except Exception as e:
                print(f"❌ Google News Strategy 1 failed: {e}")
            
            # Strategy 2: Title-only search for high relevance
            try:
                print(f"🔍 Google News Strategy 2: Title search 'intitle:{search_term}'")
                result = gn.search(f'intitle:{search_term}', when='7d')
                if result and result.get('entries'):
                    for entry in result['entries']:
                        articles.append({
                            'title': entry.get('title', ''),
                            'description': entry.get('summary', ''),
                            'url': entry.get('link', ''),
                            'urlToImage': '',
                            'publishedAt': entry.get('published', datetime.now().isoformat()),
                            'source': {'name': entry.get('source', {}).get('title', 'Google News')},
                            'content': entry.get('summary', '')
                        })
                    print(f"🔍 Strategy 2 found {len(result['entries'])} articles")
            except Exception as e:
                print(f"❌ Google News Strategy 2 failed: {e}")
            
            # Strategy 3: Boolean OR search for broader coverage
            try:
                print(f"🔍 Google News Strategy 3: Boolean search '{search_term} OR \"{search_term}\"'")
                result = gn.search(f'{search_term} OR "{search_term}"', when='7d')
                if result and result.get('entries'):
                    for entry in result['entries']:
                        articles.append({
                            'title': entry.get('title', ''),
                            'description': entry.get('summary', ''),
                            'url': entry.get('link', ''),
                            'urlToImage': '',
                            'publishedAt': entry.get('published', datetime.now().isoformat()),
                            'source': {'name': entry.get('source', {}).get('title', 'Google News')},
                            'content': entry.get('summary', '')
                        })
                    print(f"🔍 Strategy 3 found {len(result['entries'])} articles")
            except Exception as e:
                print(f"❌ Google News Strategy 3 failed: {e}")
            
            # Strategy 4: All-in-text search for comprehensive coverage
            try:
                print(f"🔍 Google News Strategy 4: All-in-text 'allintext:{search_term}'")
                result = gn.search(f'allintext:{search_term}', when='7d')
                if result and result.get('entries'):
                    for entry in result['entries']:
                        articles.append({
                            'title': entry.get('title', ''),
                            'description': entry.get('summary', ''),
                            'url': entry.get('link', ''),
                            'urlToImage': '',
                            'publishedAt': entry.get('published', datetime.now().isoformat()),
                            'source': {'name': entry.get('source', {}).get('title', 'Google News')},
                            'content': entry.get('summary', '')
                        })
                    print(f"🔍 Strategy 4 found {len(result['entries'])} articles")
            except Exception as e:
                print(f"❌ Google News Strategy 4 failed: {e}")
            
            # Remove duplicates based on URL
            seen_urls = set()
            unique_articles = []
            for article in articles:
                if article.get('url') not in seen_urls:
                    seen_urls.add(article.get('url'))
                    unique_articles.append(article)
            
            print(f"🔍 ADVANCED Google News total unique articles: {len(unique_articles)}")
            return unique_articles
            
        except Exception as e:
            print(f"❌ ADVANCED Google News error: {e}")
            return []
    
    async def _search_gdelt(self, search_term: str, **kwargs) -> List[Dict]:
        """Search using GDELT Doc API with ADVANCED features"""
        try:
            print(f"🔍 ADVANCED GDELT search for: '{search_term}'")
            
            # Use the proper GDELT Doc API
            url = "https://api.gdeltproject.org/api/v2/doc/doc"
            
            articles = []
            
            # Strategy 1: Basic search with recent articles
            try:
                print(f"🔍 GDELT Strategy 1: Basic search '{search_term}'")
                params = {
                    'query': search_term,
                    'mode': 'artlist',
                    'maxrecords': 20,
                    'format': 'json',
                    'sort': 'hybridrel',
                    'startdatetime': '20250101000000',
                    'enddatetime': '20251231235959'
                }
                
                async with self.http_client.get(url, params=params) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
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
                        print(f"🔍 GDELT Strategy 1 found {len(data['articles'])} articles")
            except Exception as e:
                print(f"❌ GDELT Strategy 1 failed: {e}")
            
            # Strategy 2: Search with domain filtering for major news sources
            try:
                print(f"🔍 GDELT Strategy 2: Domain-filtered search")
                major_domains = "domain:nytimes.com OR domain:reuters.com OR domain:bbc.com OR domain:cnn.com OR domain:foxnews.com OR domain:msnbc.com OR domain:abcnews.go.com OR domain:cbsnews.com OR domain:nbcnews.com OR domain:usatoday.com OR domain:wsj.com OR domain:latimes.com OR domain:chicagotribune.com OR domain:washingtonpost.com OR domain:politico.com OR domain:axios.com OR domain:thehill.com OR domain:rollcall.com"
                
                params = {
                    'query': f'({search_term}) AND ({major_domains})',
                    'mode': 'artlist',
                    'maxrecords': 15,
                    'format': 'json',
                    'sort': 'hybridrel',
                    'startdatetime': '20250101000000',
                    'enddatetime': '20251231235959'
                }
                
                async with self.http_client.get(url, params=params) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
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
                        print(f"🔍 GDELT Strategy 2 found {len(data['articles'])} articles")
            except Exception as e:
                print(f"❌ GDELT Strategy 2 failed: {e}")
            
            # Strategy 3: Search with sentiment filtering
            try:
                print(f"🔍 GDELT Strategy 3: Sentiment-aware search")
                params = {
                    'query': f'"{search_term}"',
                    'mode': 'artlist',
                    'maxrecords': 10,
                    'format': 'json',
                    'sort': 'hybridrel',
                    'startdatetime': '20250101000000',
                    'enddatetime': '20251231235959'
                }
                
                async with self.http_client.get(url, params=params) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
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
                        print(f"🔍 GDELT Strategy 3 found {len(data['articles'])} articles")
            except Exception as e:
                print(f"❌ GDELT Strategy 3 failed: {e}")
            
            # Remove duplicates
            seen_urls = set()
            unique_articles = []
            for article in articles:
                if article.get('url') not in seen_urls:
                    seen_urls.add(article.get('url'))
                    unique_articles.append(article)
            
            print(f"🔍 ADVANCED GDELT total unique articles: {len(unique_articles)}")
            return unique_articles
            
        except Exception as e:
            print(f"❌ ADVANCED GDELT error: {e}")
            return []
    
    async def _search_commoncrawl(self, search_term: str, **kwargs) -> List[Dict]:
        """Search using CommonCrawl with ADVANCED features"""
        try:
            print(f"🔍 ADVANCED CommonCrawl search for: '{search_term}'")
            
            # Use the CORRECT CommonCrawl index (current one)
            # Get the latest index from https://commoncrawl.org/the-data/get-started/
            url = "https://index.commoncrawl.org/CC-MAIN-2024-50-index"
            
            articles = []
            
            # Strategy 1: News domain search with content filtering
            try:
                print(f"🔍 CommonCrawl Strategy 1: News domain search")
                params = {
                    'url': '*.news.com OR *.com/news OR *.org/news OR *.co.uk/news OR *.ca/news',
                    'match': search_term,
                    'output': 'json',
                    'fl': 'url,title,timestamp,content,length'
                }
                
                async with self.http_client.get(url, params=params) as response:
                    response.raise_for_status()
                    
                    lines = (await response.text()).strip().split('\n')
                    for line in lines:
                        if line.strip():
                            try:
                                data = json.loads(line)
                                # Filter for quality content
                                if data.get('length', 0) > 1000:  # Minimum content length
                                    articles.append({
                                        'title': data.get('title', ''),
                                        'description': data.get('content', '')[:200] + '...',
                                        'url': data.get('url', ''),
                                        'urlToImage': '',
                                        'publishedAt': data.get('timestamp', datetime.now().isoformat()),
                                        'source': {'name': 'CommonCrawl'},
                                        'content': data.get('content', '')
                                    })
                                    
                                    if len(articles) >= 10:
                                        break
                            except json.JSONDecodeError:
                                continue
                
                print(f"🔍 CommonCrawl Strategy 1 found {len(articles)} articles")
            except Exception as e:
                print(f"❌ CommonCrawl Strategy 1 failed: {e}")
            
            # Strategy 2: Major news sources only
            try:
                print(f"🔍 CommonCrawl Strategy 2: Major news sources")
                major_news_domains = "nytimes.com OR reuters.com OR bbc.com OR cnn.com OR foxnews.com OR msnbc.com OR abcnews.go.com OR cbsnews.com OR nbcnews.com OR usatoday.com OR wsj.com OR latimes.com OR washingtonpost.com OR politico.com OR axios.com"
                
                params = {
                    'url': major_news_domains,
                    'match': search_term,
                    'output': 'json',
                    'fl': 'url,title,timestamp,content,length'
                }
                
                async with self.http_client.get(url, params=params) as response:
                    response.raise_for_status()
                    
                    lines = (await response.text()).strip().split('\n')
                    for line in lines:
                        if line.strip():
                            try:
                                data = json.loads(line)
                                if data.get('length', 0) > 500:  # Lower threshold for major sources
                                    articles.append({
                                        'title': data.get('title', ''),
                                        'description': data.get('content', '')[:200] + '...',
                                        'url': data.get('url', ''),
                                        'urlToImage': '',
                                        'publishedAt': data.get('timestamp', datetime.now().isoformat()),
                                        'source': {'name': 'CommonCrawl'},
                                        'content': data.get('content', '')
                                    })
                                    
                                    if len(articles) >= 15:
                                        break
                            except json.JSONDecodeError:
                                continue
                
                print(f"🔍 CommonCrawl Strategy 2 found {len(articles)} articles")
            except Exception as e:
                print(f"❌ CommonCrawl Strategy 2 failed: {e}")
            
            # Strategy 3: Recent content only (last 6 months)
            try:
                print(f"🔍 CommonCrawl Strategy 3: Recent content")
                # Use a more recent index for recent content
                recent_url = "https://index.commoncrawl.org/CC-MAIN-2024-45-index"
                
                params = {
                    'url': '*.news.com OR *.com/news',
                    'match': search_term,
                    'output': 'json',
                    'fl': 'url,title,timestamp,content,length'
                }
                
                async with self.http_client.get(recent_url, params=params) as response:
                    response.raise_for_status()
                    
                    lines = (await response.text()).strip().split('\n')
                    for line in lines:
                        if line.strip():
                            try:
                                data = json.loads(line)
                                if data.get('length', 0) > 800:
                                    articles.append({
                                        'title': data.get('title', ''),
                                        'description': data.get('content', '')[:200] + '...',
                                        'url': data.get('url', ''),
                                        'urlToImage': '',
                                        'publishedAt': data.get('timestamp', datetime.now().isoformat()),
                                        'source': {'name': 'CommonCrawl'},
                                        'content': data.get('content', '')
                                    })
                                    
                                    if len(articles) >= 20:
                                        break
                            except json.JSONDecodeError:
                                continue
                
                print(f"🔍 CommonCrawl Strategy 3 found {len(articles)} articles")
            except Exception as e:
                print(f"❌ CommonCrawl Strategy 3 failed: {e}")
            
            # Remove duplicates
            seen_urls = set()
            unique_articles = []
            for article in articles:
                if article.get('url') not in seen_urls:
                    seen_urls.add(article.get('url'))
                    unique_articles.append(article)
            
            print(f"🔍 ADVANCED CommonCrawl total unique articles: {len(unique_articles)}")
            return unique_articles
            
        except Exception as e:
            print(f"❌ ADVANCED CommonCrawl error: {e}")
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
                'https://feeds.theguardian.com/theguardian/world/rss',
                'https://feeds.nbcnews.com/nbcnews/public/world',
                'https://feeds.abcnews.com/abcnews/internationalheadlines',
                'https://feeds.cbsnews.com/CBSNewsWorld',
                'https://feeds.feedburner.com/time/world',
                'https://feeds.feedburner.com/time/politics'
            ]
            
            all_articles = []
            
            for feed_url in rss_feeds:
                try:
                    async with self.http_client.get(feed_url) as response:
                        response.raise_for_status()
                        
                        # Parse RSS content with better matching
                        articles = self._parse_enhanced_rss_content(await response.text(), search_term, feed_url)
                        all_articles.extend(articles)
                        
                        if len(all_articles) >= 20:
                            break
                            
                except Exception as e:
                    print(f"❌ RSS feed error for {feed_url}: {e}")
                    continue
            
            # Remove duplicates
            seen_urls = set()
            unique_articles = []
            for article in all_articles:
                if article.get('url') not in seen_urls:
                    seen_urls.add(article.get('url'))
                    unique_articles.append(article)
            
            print(f"🔍 Enhanced RSS found {len(unique_articles)} unique articles")
            return unique_articles
            
        except Exception as e:
            print(f"❌ Enhanced RSS error: {e}")
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
        """Search articles using UNIVERSAL search with intelligent stance detection"""
        try:
            print(f"🔍 UNIVERSAL SEARCH: Starting search for query: '{query}' with bias: {bias}")
            
            # Extract topic and user view
            topic, user_view = self._extract_topic_and_view(query)
            print(f"🔍 UNIVERSAL SEARCH: Extracted topic: '{topic}', user_view: '{user_view}'")
            
            # Generate intelligent, stance-aware search terms
            search_generator = UniversalSearchTermGenerator()
            search_terms = search_generator.generate_search_terms(query, bias)
            print(f"🔍 UNIVERSAL SEARCH: Generated {len(search_terms)} intelligent search terms")
            
            # Search using ALL APIs with intelligent strategy
            articles = await self._search_multiple_strategies_intelligent(search_terms, limit, bias, user_view)
            
            if not articles:
                print("⚠️ No articles found, trying fallback search")
                articles = await self._fallback_search(topic, limit)
            
            if not articles:
                print("❌ No articles found from any source")
                return []
            
            print(f"🔍 UNIVERSAL SEARCH: Retrieved {len(articles)} articles")
            
            # Analyze articles with CORRECT stance detection
            analyzed_articles = await self._analyze_articles_intelligent(articles, topic, user_view, bias)
            
            print(f"🔍 UNIVERSAL SEARCH: Analyzed {len(analyzed_articles)} articles")
            
            # Sort by final score and return
            analyzed_articles.sort(key=lambda x: x.get('bias_analysis', {}).get('final_score', 0), reverse=True)
            
            print(f"🔍 UNIVERSAL SEARCH: Returning {len(analyzed_articles)} articles")
            return analyzed_articles[:limit]
            
        except Exception as e:
            print(f"❌ UNIVERSAL SEARCH: Error: {e}")
            return []
    
    async def _search_multiple_strategies_intelligent(self, search_terms: List[str], limit: int, bias: float, user_view: str) -> List[Dict]:
        """
        Search using multiple strategies with intelligent bias-aware prioritization
        """
        print(f"🔍 INTELLIGENT SEARCH: Using {len(search_terms)} search strategies")
        print(f"🔍 INTELLIGENT SEARCH: Search terms: {search_terms}")
        
        all_articles = []
        seen_urls = set()
        seen_sources = {}  # Track articles per source for diversity
        
        # IMPROVED: Source diversity limits
        max_articles_per_source = max(3, limit // 5)  # Max 3 articles per source, or limit/5
        
        for i, search_term in enumerate(search_terms):
            if len(all_articles) >= limit:
                break
                
            print(f"🔍 INTELLIGENT SEARCH: Strategy {i+1}/{len(search_terms)}: '{search_term}'")
            
            try:
                # Try Google News first (most reliable for political topics)
                if self.google_news:
                    articles = await self._search_google_news(
                        search_term=search_term,
                        page_size=limit * 2  # Get more to filter for diversity
                    )
                    if articles:
                        print(f"🔍 INTELLIGENT SEARCH: Google News found {len(articles)} articles")
                        articles = self._filter_for_diversity(articles, seen_urls, seen_sources, max_articles_per_source)
                        all_articles.extend(articles)
                        print(f"🔍 INTELLIGENT SEARCH: After diversity filter: {len(articles)} articles")
                
                # Try NewsAPI if we need more articles
                if len(all_articles) < limit and not self._should_use_fallback():
                    newsapi_result = await self._search_newsapi(search_term=search_term)
                    if newsapi_result and newsapi_result.get('articles'):
                        articles = newsapi_result['articles']
                        print(f"🔍 INTELLIGENT SEARCH: NewsAPI found {len(articles)} articles")
                        articles = self._filter_for_diversity(articles, seen_urls, seen_sources, max_articles_per_source)
                        all_articles.extend(articles)
                        print(f"🔍 INTELLIGENT SEARCH: After diversity filter: {len(articles)} articles")
                
                # Try Enhanced RSS feeds
                if len(all_articles) < limit:
                    articles = await self._search_enhanced_rss(search_term=search_term)
                    if articles:
                        print(f"🔍 INTELLIGENT SEARCH: Enhanced RSS found {len(articles)} articles")
                        articles = self._filter_for_diversity(articles, seen_urls, seen_sources, max_articles_per_source)
                        all_articles.extend(articles)
                        print(f"🔍 INTELLIGENT SEARCH: After diversity filter: {len(articles)} articles")
                
                # Try GDELT as fallback
                if len(all_articles) < limit and settings.gdelt_api_key:
                    articles = await self._search_gdelt(
                        search_term=search_term,
                        page_size=limit
                    )
                    if articles:
                        print(f"🔍 INTELLIGENT SEARCH: GDELT found {len(articles)} articles")
                        articles = self._filter_for_diversity(articles, seen_urls, seen_sources, max_articles_per_source)
                        all_articles.extend(articles)
                        print(f"🔍 INTELLIGENT SEARCH: After diversity filter: {len(articles)} articles")
                
                # Try CommonCrawl as last resort
                if len(all_articles) < limit:
                    articles = await self._search_commoncrawl(
                        search_term=search_term,
                        page_size=limit
                    )
                    if articles:
                        print(f"🔍 INTELLIGENT SEARCH: CommonCrawl found {len(articles)} articles")
                        articles = self._filter_for_diversity(articles, seen_urls, seen_sources, max_articles_per_source)
                        all_articles.extend(articles)
                        print(f"🔍 INTELLIGENT SEARCH: After diversity filter: {len(articles)} articles")
                
            except Exception as e:
                print(f"🔍 INTELLIGENT SEARCH: Error in strategy {i+1}: {e}")
                continue
        
        print(f"🔍 INTELLIGENT SEARCH: Total articles found: {len(all_articles)}")
        print(f"🔍 INTELLIGENT SEARCH: Sources used: {list(seen_sources.keys())}")
        
        return all_articles[:limit]
    
    def _filter_for_diversity(self, articles: List[Dict], seen_urls: set, seen_sources: Dict, max_per_source: int) -> List[Dict]:
        """
        Filter articles for source diversity and URL deduplication
        """
        filtered_articles = []
        
        for article in articles:
            url = article.get('url', '')
            source = article.get('source', {}).get('name', '') if isinstance(article.get('source'), dict) else str(article.get('source', ''))
            
            # Skip if URL already seen
            if url in seen_urls:
                continue
            
            # Skip if too many articles from this source
            if seen_sources.get(source, 0) >= max_per_source:
                continue
            
            # Add to filtered list
            filtered_articles.append(article)
            seen_urls.add(url)
            seen_sources[source] = seen_sources.get(source, 0) + 1
        
        return filtered_articles
    
    async def _analyze_articles_intelligent(self, articles: List[Dict], topic: str, user_view: str, bias: float) -> List[Dict]:
        """Analyze articles with CORRECT stance detection logic"""
        analyzed_articles = []
        
        print(f"🔍 INTELLIGENT ANALYSIS: Analyzing {len(articles)} articles")
        print(f"🔍 INTELLIGENT ANALYSIS: Topic: '{topic}', User view: '{user_view}', Bias: {bias}")
        
        for i, article in enumerate(articles):
            try:
                print(f"🔍 INTELLIGENT ANALYSIS: Analyzing article {i+1}/{len(articles)}: {article.get('title', 'No title')[:50]}...")
                
                # Get stance analysis
                stance_analysis = await advanced_stance_detector.detect_stance(
                    belief=user_view,
                    article_text=f"{article.get('title', '')} {article.get('description', '')} {article.get('content', '')}"
                )
                
                # Calculate bias match with CORRECT logic
                bias_match = self._calculate_bias_match({
                    "stance": stance_analysis.stance,
                    "confidence": stance_analysis.confidence
                }, bias, user_view)
                
                # Calculate relevance score
                relevance_scorer = UniversalRelevanceScorer()
                article_content = f"{article.get('title', '')} {article.get('description', '')} {article.get('content', '')}"
                relevance_score = relevance_scorer.calculate_relevance_score(article_content, topic, user_view)
                
                # Calculate final score
                final_score = (bias_match * 0.7) + (relevance_score * 0.3)
                
                # Add analysis to article
                article['bias_analysis'] = {
                    'stance': stance_analysis.stance,
                    'stance_confidence': stance_analysis.confidence,
                    'stance_method': stance_analysis.method,
                    'stance_evidence': stance_analysis.evidence,
                    'bias_match': bias_match,
                    'relevance_score': relevance_score,
                    'final_score': final_score,
                    'user_bias_preference': bias,
                    'user_belief': user_view,
                    'analysis_method': 'intelligent_stance_detection'
                }
                
                analyzed_articles.append(article)
            
            except Exception as e:
                print(f"🔍 INTELLIGENT ANALYSIS: Error analyzing article: {e}")
                continue
        
        return analyzed_articles
    
    def _extract_topic_and_view(self, query: str) -> tuple[str, str]:
        """Extract topic and user view from query"""
        words = query.split()
        if len(words) < 2:
            return words[0] if words else "news", ""
        
        # Find the main topic (usually first significant word)
        topic = words[0].lower()
        user_view = " ".join(words[1:])
        
        return topic, user_view
    
    def _calculate_bias_match(self, stance_analysis: Dict, bias: float, user_view: str = "") -> float:
        """
        Calculate bias match using CORRECT logic
        
        bias: 0.0 = challenging views, 1.0 = supporting views
        stance: "support", "oppose", "neutral"
        user_view: The user's view about the topic
        
        CORRECT LOGIC:
        - "support" stance = article supports the USER'S view
        - "oppose" stance = article opposes the USER'S view
        """
        stance = stance_analysis["stance"]
        confidence = stance_analysis["confidence"]
        
        # Determine if user has a negative or positive view
        user_has_negative_view = any(word in user_view.lower() for word in ['hate', 'terrible', 'awful', 'bad', 'wrong', 'dislike', 'evil', 'horrible', 'worst', 'disgusting', 'ruining', 'destroying', 'damaging', 'harming', 'hurting', 'problematic', 'controversial', 'scandal', 'corruption', 'failure', 'disaster', 'crisis'])
        user_has_positive_view = any(word in user_view.lower() for word in ['love', 'great', 'amazing', 'good', 'right', 'like', 'excellent', 'wonderful', 'fantastic', 'brilliant', 'outstanding', 'perfect', 'best', 'superior', 'helping', 'improving', 'beneficial', 'positive', 'success', 'achievement', 'victory', 'triumph', 'breakthrough', 'innovation', 'progress'])
        
        print(f"🔍 BIAS MATCH: User view: '{user_view}'")
        print(f"🔍 BIAS MATCH: User negative: {user_has_negative_view}, positive: {user_has_positive_view}")
        print(f"🔍 BIAS MATCH: Article stance: {stance}, confidence: {confidence}")
        print(f"🔍 BIAS MATCH: User bias preference: {bias}")
        
        # CORRECT LOGIC: "support" means supports the USER'S view
        if bias == 0.0:  # User wants challenging views
            if user_has_negative_view:
                # User hates the topic, so challenging views = articles that support the topic (oppose user's view)
                if stance == "oppose":  # Article opposes user's negative view (supports topic)
                    return 1.0 * confidence  # Perfect match - challenges user's negative view
                elif stance == "support":  # Article supports user's negative view (opposes topic)
                    return 0.0  # Wrong direction - supports user's negative view
                else:  # neutral
                    return 0.5 * confidence
            elif user_has_positive_view:
                # User loves the topic, so challenging views = articles that oppose the topic (oppose user's view)
                if stance == "oppose":  # Article opposes user's positive view (opposes topic)
                    return 1.0 * confidence  # Perfect match - challenges user's positive view
                elif stance == "support":  # Article supports user's positive view (supports topic)
                    return 0.0  # Wrong direction - supports user's positive view
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
                # User hates the topic, so supporting views = articles that also oppose the topic (support user's view)
                if stance == "support":  # Article supports user's negative view (opposes topic)
                    return 1.0 * confidence  # Perfect match - supports user's negative view
                elif stance == "oppose":  # Article opposes user's negative view (supports topic)
                    return 0.0  # Wrong direction - opposes user's negative view
                else:  # neutral
                    return 0.5 * confidence
            elif user_has_positive_view:
                # User loves the topic, so supporting views = articles that also support the topic (support user's view)
                if stance == "support":  # Article supports user's positive view (supports topic)
                    return 1.0 * confidence  # Perfect match - supports user's positive view
                elif stance == "oppose":  # Article opposes user's positive view (opposes topic)
                    return 0.0  # Wrong direction - opposes user's positive view
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
                if stance == "support":
                    # More bias = more support (supporting user's negative view)
                    return bias * confidence
                elif stance == "oppose":
                    # More bias = less oppose (challenging user's negative view)
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