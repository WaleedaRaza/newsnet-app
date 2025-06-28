"""
Multi-API News Service

Orchestrates multiple news APIs to provide comprehensive coverage:
- NewsAPI.org (current)
- GNews API
- Mediastack API  
- Webz.io API
- Newscatcher API
- World News API
- The Guardian API
- NYT API
- Aylien News API
- Contify API
"""

import asyncio
import httpx
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class NewsAPIClient(ABC):
    """Abstract base class for news API clients"""
    
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    @abstractmethod
    async def search_articles(self, query: str, limit: int = 20) -> List[Dict]:
        """Search for articles using the API"""
        pass
    
    @abstractmethod
    async def get_top_headlines(self, category: str = None, limit: int = 20) -> List[Dict]:
        """Get top headlines from the API"""
        pass
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

class NewsAPIClientImpl(NewsAPIClient):
    """NewsAPI.org implementation"""
    
    async def search_articles(self, query: str, limit: int = 20) -> List[Dict]:
        """Search articles using NewsAPI.org"""
        try:
            params = {
                'q': query,
                'apiKey': self.api_key,
                'language': 'en',
                'sortBy': 'relevancy',
                'pageSize': min(limit, 100)
            }
            
            response = await self.client.get(f"{self.base_url}/everything", params=params)
            response.raise_for_status()
            
            data = response.json()
            return data.get('articles', [])
            
        except Exception as e:
            logger.error(f"NewsAPI search error: {e}")
            return []
    
    async def get_top_headlines(self, category: str = None, limit: int = 20) -> List[Dict]:
        """Get top headlines using NewsAPI.org"""
        try:
            params = {
                'apiKey': self.api_key,
                'country': 'us',
                'pageSize': min(limit, 100)
            }
            
            if category:
                params['category'] = category
            
            response = await self.client.get(f"{self.base_url}/top-headlines", params=params)
            response.raise_for_status()
            
            data = response.json()
            return data.get('articles', [])
            
        except Exception as e:
            logger.error(f"NewsAPI headlines error: {e}")
            return []

class GNewsAPIClient(NewsAPIClient):
    """GNews API implementation"""
    
    async def search_articles(self, query: str, limit: int = 20) -> List[Dict]:
        """Search articles using GNews API"""
        try:
            params = {
                'q': query,
                'token': self.api_key,
                'lang': 'en',
                'max': min(limit, 100)
            }
            
            response = await self.client.get(f"{self.base_url}/search", params=params)
            response.raise_for_status()
            
            data = response.json()
            return data.get('articles', [])
            
        except Exception as e:
            logger.error(f"GNews search error: {e}")
            return []
    
    async def get_top_headlines(self, category: str = None, limit: int = 20) -> List[Dict]:
        """Get top headlines using GNews API"""
        try:
            params = {
                'token': self.api_key,
                'lang': 'en',
                'max': min(limit, 100)
            }
            
            if category:
                params['topic'] = category
            
            response = await self.client.get(f"{self.base_url}/top-headlines", params=params)
            response.raise_for_status()
            
            data = response.json()
            return data.get('articles', [])
            
        except Exception as e:
            logger.error(f"GNews headlines error: {e}")
            return []

class MultiAPIService:
    """Orchestrates multiple news APIs for comprehensive coverage"""
    
    def __init__(self, config: Dict[str, str]):
        self.clients = {}
        self.setup_clients(config)
    
    def setup_clients(self, config: Dict[str, str]):
        """Setup API clients based on configuration"""
        # NewsAPI.org
        if 'newsapi_key' in config:
            self.clients['newsapi'] = NewsAPIClientImpl(
                config['newsapi_key'],
                'https://newsapi.org/v2'
            )
        
        # GNews API
        if 'gnews_key' in config:
            self.clients['gnews'] = GNewsAPIClient(
                config['gnews_key'],
                'https://gnews.io/api/v4'
            )
        
        # Add more API clients here as we implement them
        logger.info(f"Initialized {len(self.clients)} API clients")
    
    async def search_articles_multi(self, query: str, limit: int = 20) -> List[Dict]:
        """Search articles across all available APIs"""
        all_articles = []
        
        # Search all APIs concurrently
        tasks = []
        for client_name, client in self.clients.items():
            task = self._search_with_fallback(client, query, limit // len(self.clients))
            tasks.append(task)
        
        # Wait for all searches to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect results
        for result in results:
            if isinstance(result, list):
                all_articles.extend(result)
            else:
                logger.error(f"API search failed: {result}")
        
        # Remove duplicates and return
        unique_articles = self._deduplicate_articles(all_articles)
        return unique_articles[:limit]
    
    async def get_headlines_multi(self, category: str = None, limit: int = 20) -> List[Dict]:
        """Get headlines across all available APIs"""
        all_headlines = []
        
        # Get headlines from all APIs concurrently
        tasks = []
        for client_name, client in self.clients.items():
            task = self._get_headlines_with_fallback(client, category, limit // len(self.clients))
            tasks.append(task)
        
        # Wait for all requests to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect results
        for result in results:
            if isinstance(result, list):
                all_headlines.extend(result)
            else:
                logger.error(f"API headlines failed: {result}")
        
        # Remove duplicates and return
        unique_headlines = self._deduplicate_articles(all_headlines)
        return unique_headlines[:limit]
    
    async def _search_with_fallback(self, client: NewsAPIClient, query: str, limit: int) -> List[Dict]:
        """Search with fallback handling"""
        try:
            return await client.search_articles(query, limit)
        except Exception as e:
            logger.error(f"Search failed for {client.__class__.__name__}: {e}")
            return []
    
    async def _get_headlines_with_fallback(self, client: NewsAPIClient, category: str, limit: int) -> List[Dict]:
        """Get headlines with fallback handling"""
        try:
            return await client.get_top_headlines(category, limit)
        except Exception as e:
            logger.error(f"Headlines failed for {client.__class__.__name__}: {e}")
            return []
    
    def _deduplicate_articles(self, articles: List[Dict]) -> List[Dict]:
        """Remove duplicate articles based on URL"""
        seen_urls = set()
        unique_articles = []
        
        for article in articles:
            url = article.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_articles.append(article)
        
        return unique_articles
    
    async def close(self):
        """Close all API clients"""
        for client in self.clients.values():
            await client.close()

# Global instance
multi_api_service = None

def initialize_multi_api_service(config: Dict[str, str]):
    """Initialize the global multi-API service"""
    global multi_api_service
    multi_api_service = MultiAPIService(config)
    return multi_api_service

def get_multi_api_service() -> MultiAPIService:
    """Get the global multi-API service instance"""
    return multi_api_service 