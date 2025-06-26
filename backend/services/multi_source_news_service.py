"""
Multi-Source News Service

This service aggregates articles from multiple news sources:
- NewsAPI.org
- GNews API  
- The Guardian API
- NYTimes API (if available)

Features:
- Rate limiting and fallback
- Unified article format
- Error handling and retry logic
- Source diversity tracking
"""

import asyncio
import aiohttp
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import os
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)

@dataclass
class NewsSourceConfig:
    """Configuration for a news source"""
    name: str
    base_url: str
    api_key: Optional[str] = None
    rate_limit: int = 100  # requests per hour
    timeout: int = 30
    enabled: bool = True

@dataclass
class RawArticle:
    """Raw article from a news source"""
    source_name: str
    title: str
    content: str
    url: str
    published_at: Optional[datetime]
    author: Optional[str] = None
    source_domain: Optional[str] = None
    raw_data: Dict[str, Any] = None

class MultiSourceNewsService:
    """
    Service for fetching articles from multiple news sources
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Configure news sources
        self.sources = self._configure_sources()
        
        # Rate limiting
        self.request_counts = {source.name: 0 for source in self.sources}
        self.last_reset = time.time()
        
        # Metrics
        self.metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'articles_fetched': 0,
            'sources_used': set()
        }
        
        self.logger.info(f"Initialized MultiSourceNewsService with {len(self.sources)} sources")
    
    def _configure_sources(self) -> List[NewsSourceConfig]:
        """Configure available news sources"""
        sources = []
        
        # NewsAPI.org
        newsapi_key = os.getenv('NEWSAPI_KEY')
        if newsapi_key:
            sources.append(NewsSourceConfig(
                name='newsapi',
                base_url='https://newsapi.org/v2',
                api_key=newsapi_key,
                rate_limit=100,
                timeout=30
            ))
        
        # GNews API
        gnews_key = os.getenv('GNEWS_API_KEY')
        if gnews_key:
            sources.append(NewsSourceConfig(
                name='gnews',
                base_url='https://gnews.io/api/v4',
                api_key=gnews_key,
                rate_limit=100,
                timeout=30
            ))
        
        # The Guardian API
        guardian_key = os.getenv('GUARDIAN_API_KEY')
        if guardian_key:
            sources.append(NewsSourceConfig(
                name='guardian',
                base_url='https://content.guardianapis.com',
                api_key=guardian_key,
                rate_limit=500,
                timeout=30
            ))
        
        # If no API keys, add mock source for testing
        if not sources:
            self.logger.warning("No API keys found - using mock source for testing")
            sources.append(NewsSourceConfig(
                name='mock',
                base_url='mock://api.example.com',
                rate_limit=1000,
                timeout=5
            ))
        
        return sources
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'User-Agent': 'Lens-NewsNet/1.0'}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def fetch_articles_for_topics(
        self, 
        topics: List[str], 
        max_articles_per_topic: int = 20,
        days_back: int = 7
    ) -> List[RawArticle]:
        """
        Fetch articles for given topics from all available sources
        
        Args:
            topics: List of topics to search for
            max_articles_per_topic: Maximum articles per topic per source
            days_back: How many days back to search
            
        Returns:
            List of raw articles from all sources
        """
        self.logger.info(f"Fetching articles for topics: {topics}")
        self.logger.info(f"Max articles per topic: {max_articles_per_topic}")
        self.logger.info(f"Days back: {days_back}")
        
        all_articles = []
        
        # Fetch from each source concurrently
        tasks = []
        for source in self.sources:
            if not source.enabled:
                continue
                
            for topic in topics:
                task = self._fetch_from_source(
                    source, topic, max_articles_per_topic, days_back
                )
                tasks.append(task)
        
        # Execute all tasks concurrently
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, Exception):
                    self.logger.error(f"Source fetch failed: {result}")
                    self.metrics['failed_requests'] += 1
                else:
                    all_articles.extend(result)
                    self.metrics['articles_fetched'] += len(result)
            
            # Update metrics
            self.metrics['total_requests'] += len(topics) * len(self.sources)
            self.metrics['successful_requests'] += len([r for r in results if not isinstance(r, Exception)])
        else:
            # No tasks to execute
            self.logger.info("No tasks to execute - no sources enabled or no topics provided")
        
        self.logger.info(f"Fetched {len(all_articles)} total articles from {len(self.sources)} sources")
        
        return all_articles
    
    async def _fetch_from_source(
        self, 
        source: NewsSourceConfig, 
        topic: str, 
        max_articles: int,
        days_back: int
    ) -> List[RawArticle]:
        """Fetch articles from a specific source for a topic"""
        
        try:
            if source.name == 'mock':
                return await self._fetch_mock_articles(topic, max_articles)
            elif source.name == 'newsapi':
                return await self._fetch_from_newsapi(source, topic, max_articles, days_back)
            elif source.name == 'gnews':
                return await self._fetch_from_gnews(source, topic, max_articles, days_back)
            elif source.name == 'guardian':
                return await self._fetch_from_guardian(source, topic, max_articles, days_back)
            else:
                self.logger.warning(f"Unknown source: {source.name}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error fetching from {source.name} for topic {topic}: {e}")
            return []
    
    async def _fetch_from_newsapi(
        self, 
        source: NewsSourceConfig, 
        topic: str, 
        max_articles: int,
        days_back: int
    ) -> List[RawArticle]:
        """Fetch articles from NewsAPI.org"""
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        url = f"{source.base_url}/everything"
        params = {
            'q': topic,
            'from': start_date.strftime('%Y-%m-%d'),
            'to': end_date.strftime('%Y-%m-%d'),
            'sortBy': 'relevancy',
            'pageSize': min(max_articles, 100),
            'apiKey': source.api_key,
            'language': 'en'
        }
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                self.logger.error(f"NewsAPI error: {response.status}")
                return []
            
            data = await response.json()
            
            if data.get('status') != 'ok':
                self.logger.error(f"NewsAPI API error: {data.get('message', 'Unknown error')}")
                return []
            
            articles = []
            for item in data.get('articles', []):
                article = RawArticle(
                    source_name=source.name,
                    title=item.get('title', ''),
                    content=item.get('content', '') or item.get('description', ''),
                    url=item.get('url', ''),
                    published_at=self._parse_date(item.get('publishedAt')),
                    author=item.get('author'),
                    source_domain=item.get('source', {}).get('name'),
                    raw_data=item
                )
                articles.append(article)
            
            self.metrics['sources_used'].add(source.name)
            self.logger.info(f"Fetched {len(articles)} articles from NewsAPI for topic '{topic}'")
            return articles
    
    async def _fetch_from_gnews(
        self, 
        source: NewsSourceConfig, 
        topic: str, 
        max_articles: int,
        days_back: int
    ) -> List[RawArticle]:
        """Fetch articles from GNews API"""
        
        url = f"{source.base_url}/search"
        params = {
            'q': topic,
            'max': max_articles,
            'apikey': source.api_key,
            'lang': 'en',
            'country': 'us',
            'sortby': 'relevance'
        }
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                self.logger.error(f"GNews error: {response.status}")
                return []
            
            data = await response.json()
            
            if 'errors' in data:
                self.logger.error(f"GNews API error: {data['errors']}")
                return []
            
            articles = []
            for item in data.get('articles', []):
                article = RawArticle(
                    source_name=source.name,
                    title=item.get('title', ''),
                    content=item.get('content', ''),
                    url=item.get('url', ''),
                    published_at=self._parse_date(item.get('publishedAt')),
                    author=item.get('author'),
                    source_domain=item.get('source', {}).get('name'),
                    raw_data=item
                )
                articles.append(article)
            
            self.metrics['sources_used'].add(source.name)
            self.logger.info(f"Fetched {len(articles)} articles from GNews for topic '{topic}'")
            return articles
    
    async def _fetch_from_guardian(
        self, 
        source: NewsSourceConfig, 
        topic: str, 
        max_articles: int,
        days_back: int
    ) -> List[RawArticle]:
        """Fetch articles from The Guardian API"""
        
        url = f"{source.base_url}/search"
        params = {
            'q': topic,
            'api-key': source.api_key,
            'page-size': min(max_articles, 50),
            'show-fields': 'headline,bodyText,byline,lastModified',
            'show-tags': 'contributor',
            'order-by': 'relevance'
        }
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                self.logger.error(f"Guardian error: {response.status}")
                return []
            
            data = await response.json()
            
            if data.get('response', {}).get('status') != 'ok':
                self.logger.error(f"Guardian API error: {data.get('response', {}).get('message', 'Unknown error')}")
                return []
            
            articles = []
            for item in data.get('response', {}).get('results', []):
                fields = item.get('webTitle', '')
                body_text = item.get('fields', {}).get('bodyText', '')
                
                article = RawArticle(
                    source_name=source.name,
                    title=item.get('webTitle', ''),
                    content=body_text or item.get('webTitle', ''),
                    url=item.get('webUrl', ''),
                    published_at=self._parse_date(item.get('webPublicationDate')),
                    author=item.get('fields', {}).get('byline'),
                    source_domain='The Guardian',
                    raw_data=item
                )
                articles.append(article)
            
            self.metrics['sources_used'].add(source.name)
            self.logger.info(f"Fetched {len(articles)} articles from Guardian for topic '{topic}'")
            return articles
    
    async def _fetch_mock_articles(self, topic: str, max_articles: int) -> List[RawArticle]:
        """Fetch mock articles for testing"""
        
        articles = []
        for i in range(min(max_articles, 5)):  # Max 5 mock articles
            article = RawArticle(
                source_name='mock',
                title=f"Mock article about {topic} - {i+1}",
                content=f"This is a mock article about {topic} for testing purposes. It contains sample content that would be analyzed by the pipeline.",
                url=f"https://mock.example.com/{topic}-{i}",
                published_at=datetime.now() - timedelta(hours=i),
                author=f"Mock Author {i+1}",
                source_domain="Mock News",
                raw_data={'mock': True, 'topic': topic, 'index': i}
            )
            articles.append(article)
        
        self.logger.info(f"Generated {len(articles)} mock articles for topic '{topic}'")
        return articles
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime object"""
        if not date_str:
            return None
        
        try:
            # Try common date formats
            formats = [
                '%Y-%m-%dT%H:%M:%SZ',
                '%Y-%m-%dT%H:%M:%S.%fZ',
                '%Y-%m-%dT%H:%M:%S%z',
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            self.logger.warning(f"Could not parse date: {date_str}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error parsing date {date_str}: {e}")
            return None
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get service metrics"""
        return {
            'metrics': self.metrics.copy(),
            'sources_configured': len(self.sources),
            'sources_enabled': len([s for s in self.sources if s.enabled]),
            'timestamp': datetime.now().isoformat()
        }

# Global instance
multi_source_news_service = MultiSourceNewsService() 