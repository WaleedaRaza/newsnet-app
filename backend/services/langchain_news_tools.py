"""
Enhanced LangChain Tools for News Retrieval
Provides intelligent tools for searching multiple news sources
"""

import asyncio
import json
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import aiohttp
import feedparser
from pygooglenews import GoogleNews
import requests
import re

from langchain.tools import BaseTool
from langchain.schema import Tool

logger = logging.getLogger(__name__)

class NewsAPITool(BaseTool):
    """Enhanced NewsAPI search tool with intelligent query processing"""
    
    name = "news_api_search"
    description = "Search for recent news articles using NewsAPI with intelligent query processing"
    
    def __init__(self, api_key: str):
        super().__init__()
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2"
        self.session = aiohttp.ClientSession()
    
    def _run(self, query: str, bias_preference: float = 0.5, limit: int = 10) -> List[Dict]:
        """Search NewsAPI with bias-aware query processing"""
        try:
            # Enhance query based on bias preference
            enhanced_query = self._enhance_query_for_bias(query, bias_preference)
            
            # Make API request
            url = f"{self.base_url}/everything"
            params = {
                'q': enhanced_query,
                'apiKey': self.api_key,
                'pageSize': limit,
                'sortBy': 'relevancy',
                'language': 'en',
                'from': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            articles = data.get('articles', [])
            
            # Process and enhance articles
            enhanced_articles = []
            for article in articles:
                enhanced_article = {
                    'title': article.get('title', ''),
                    'content': article.get('content', ''),
                    'url': article.get('url', ''),
                    'source': article.get('source', {}).get('name', 'Unknown'),
                    'published_at': article.get('publishedAt', ''),
                    'description': article.get('description', ''),
                    'urlToImage': article.get('urlToImage', ''),
                    'api_source': 'NewsAPI'
                }
                enhanced_articles.append(enhanced_article)
            
            logger.info(f"NewsAPI found {len(enhanced_articles)} articles for query: {enhanced_query}")
            return enhanced_articles
            
        except Exception as e:
            logger.error(f"NewsAPI search error: {e}")
            return []
    
    def _enhance_query_for_bias(self, query: str, bias_preference: float) -> str:
        """Enhance query based on bias preference"""
        if bias_preference < 0.3:  # Challenging views
            # Add terms that might find opposing viewpoints
            bias_terms = ['criticism', 'opposition', 'controversy', 'debate', 'challenge']
        elif bias_preference > 0.7:  # Supporting views
            # Add terms that might find supportive viewpoints
            bias_terms = ['support', 'success', 'achievement', 'positive', 'benefit']
        else:  # Balanced
            bias_terms = []
        
        if bias_terms:
            enhanced_query = f'"{query}" AND ({(" OR ".join(bias_terms))})'
        else:
            enhanced_query = f'"{query}"'
        
        return enhanced_query

class GoogleNewsTool(BaseTool):
    """Enhanced Google News search tool with multiple strategies"""
    
    name = "google_news_search"
    description = "Search for news articles using Google News with multiple search strategies"
    
    def __init__(self):
        super().__init__()
        self.google_news = GoogleNews()
    
    def _run(self, query: str, bias_preference: float = 0.5, limit: int = 10) -> List[Dict]:
        """Search Google News with multiple strategies"""
        try:
            all_articles = []
            
            # Strategy 1: Exact phrase search
            try:
                result = self.google_news.search(f'"{query}"', when='7d')
                if result and result.get('entries'):
                    articles = self._process_google_news_results(result['entries'])
                    all_articles.extend(articles)
                    logger.info(f"Google News Strategy 1 found {len(articles)} articles")
            except Exception as e:
                logger.error(f"Google News Strategy 1 failed: {e}")
            
            # Strategy 2: Title-only search for high relevance
            try:
                result = self.google_news.search(f'intitle:{query}', when='7d')
                if result and result.get('entries'):
                    articles = self._process_google_news_results(result['entries'])
                    all_articles.extend(articles)
                    logger.info(f"Google News Strategy 2 found {len(articles)} articles")
            except Exception as e:
                logger.error(f"Google News Strategy 2 failed: {e}")
            
            # Strategy 3: Bias-aware search
            try:
                bias_query = self._create_bias_aware_query(query, bias_preference)
                result = self.google_news.search(bias_query, when='7d')
                if result and result.get('entries'):
                    articles = self._process_google_news_results(result['entries'])
                    all_articles.extend(articles)
                    logger.info(f"Google News Strategy 3 found {len(articles)} articles")
            except Exception as e:
                logger.error(f"Google News Strategy 3 failed: {e}")
            
            # Remove duplicates and limit
            unique_articles = self._deduplicate_articles(all_articles)
            return unique_articles[:limit]
            
        except Exception as e:
            logger.error(f"Google News search error: {e}")
            return []
    
    def _process_google_news_results(self, entries: List[Dict]) -> List[Dict]:
        """Process Google News results into standardized format"""
        articles = []
        for entry in entries:
            article = {
                'title': entry.get('title', ''),
                'content': entry.get('summary', ''),
                'url': entry.get('link', ''),
                'source': entry.get('source', {}).get('title', 'Google News'),
                'published_at': entry.get('published', datetime.now().isoformat()),
                'description': entry.get('summary', ''),
                'urlToImage': '',
                'api_source': 'Google News'
            }
            articles.append(article)
        return articles
    
    def _create_bias_aware_query(self, query: str, bias_preference: float) -> str:
        """Create bias-aware query for Google News"""
        if bias_preference < 0.3:
            # Add challenging terms
            bias_terms = ['criticism', 'opposition', 'controversy']
        elif bias_preference > 0.7:
            # Add supportive terms
            bias_terms = ['support', 'success', 'positive']
        else:
            bias_terms = []
        
        if bias_terms:
            return f'{query} {" ".join(bias_terms)}'
        else:
            return query
    
    def _deduplicate_articles(self, articles: List[Dict]) -> List[Dict]:
        """Remove duplicate articles based on URL"""
        seen_urls = set()
        unique_articles = []
        
        for article in articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)
        
        return unique_articles

class RSSTool(BaseTool):
    """Enhanced RSS feed search tool with intelligent filtering"""
    
    name = "rss_feed_search"
    description = "Search RSS feeds for news articles with intelligent relevance filtering"
    
    def __init__(self):
        super().__init__()
        self.rss_feeds = [
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
        self.session = aiohttp.ClientSession()
    
    def _run(self, query: str, bias_preference: float = 0.5, limit: int = 10) -> List[Dict]:
        """Search RSS feeds with intelligent filtering"""
        try:
            all_articles = []
            
            # Search each RSS feed
            for feed_url in self.rss_feeds:
                try:
                    articles = self._search_rss_feed(feed_url, query, bias_preference)
                    all_articles.extend(articles)
                    
                    if len(all_articles) >= limit * 2:  # Get extra for filtering
                        break
                        
                except Exception as e:
                    logger.error(f"RSS feed error for {feed_url}: {e}")
                    continue
            
            # Filter for relevance and remove duplicates
            relevant_articles = self._filter_for_relevance(all_articles, query)
            unique_articles = self._deduplicate_articles(relevant_articles)
            
            logger.info(f"RSS feeds found {len(unique_articles)} relevant articles")
            return unique_articles[:limit]
            
        except Exception as e:
            logger.error(f"RSS search error: {e}")
            return []
    
    async def _search_rss_feed(self, feed_url: str, query: str, bias_preference: float) -> List[Dict]:
        """Search a single RSS feed"""
        try:
            async with self.session.get(feed_url) as response:
                response.raise_for_status()
                content = await response.text()
                
                # Parse RSS content
                feed = feedparser.parse(content)
                articles = []
                
                # Clean and normalize search terms
                search_words = [word.lower().strip() for word in query.lower().split() if len(word) > 2]
                search_phrase = query.lower().strip()
                
                for entry in feed.entries:
                    # Extract article data
                    title = entry.get('title', '')
                    description = entry.get('summary', '')
                    link = entry.get('link', '')
                    published = entry.get('published', datetime.now().isoformat())
                    
                    # Clean HTML tags
                    title_clean = re.sub(r'<[^>]+>', '', title)
                    desc_clean = re.sub(r'<[^>]+>', '', description)
                    
                    # Combine for analysis
                    full_text = f"{title_clean} {desc_clean}".lower()
                    
                    # Check relevance
                    word_matches = sum(1 for word in search_words if word in full_text)
                    phrase_match = search_phrase in full_text
                    
                    # Article must have at least 2 word matches OR the full phrase
                    is_relevant = word_matches >= 2 or phrase_match
                    
                    if is_relevant:
                        # Determine source name
                        source_name = self._get_source_name(feed_url)
                        
                        article = {
                            'title': title_clean,
                            'content': f"{title_clean}. {desc_clean}",
                            'url': link,
                            'source': source_name,
                            'published_at': published,
                            'description': desc_clean,
                            'urlToImage': '',
                            'api_source': 'RSS Feed'
                        }
                        articles.append(article)
                        
                        # Limit to 2 articles per feed to avoid overwhelming
                        if len(articles) >= 2:
                            break
                
                return articles
                
        except Exception as e:
            logger.error(f"Error searching RSS feed {feed_url}: {e}")
            return []
    
    def _get_source_name(self, feed_url: str) -> str:
        """Extract source name from feed URL"""
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
    
    def _filter_for_relevance(self, articles: List[Dict], query: str) -> List[Dict]:
        """Filter articles for relevance to query"""
        relevant_articles = []
        query_lower = query.lower()
        
        for article in articles:
            title_lower = article['title'].lower()
            content_lower = article['content'].lower()
            
            # Check if query terms appear in title or content
            query_words = query_lower.split()
            matches = sum(1 for word in query_words if word in title_lower or word in content_lower)
            
            # Article is relevant if it has at least 2 query word matches
            if matches >= 2:
                relevant_articles.append(article)
        
        return relevant_articles
    
    def _deduplicate_articles(self, articles: List[Dict]) -> List[Dict]:
        """Remove duplicate articles based on URL"""
        seen_urls = set()
        unique_articles = []
        
        for article in articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)
        
        return unique_articles

class GDELTTool(BaseTool):
    """Enhanced GDELT search tool for global news events"""
    
    name = "gdelt_search"
    description = "Search GDELT for global news events and articles"
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://api.gdeltproject.org/api/v2/doc/doc"
        self.session = aiohttp.ClientSession()
    
    def _run(self, query: str, bias_preference: float = 0.5, limit: int = 10) -> List[Dict]:
        """Search GDELT with bias-aware processing"""
        try:
            all_articles = []
            
            # Strategy 1: Basic search
            try:
                params = {
                    'query': query,
                    'mode': 'artlist',
                    'maxrecords': limit,
                    'format': 'json',
                    'sort': 'hybridrel',
                    'startdatetime': '20250101000000',
                    'enddatetime': '20251231235959'
                }
                
                response = requests.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if 'articles' in data:
                    articles = self._process_gdelt_results(data['articles'])
                    all_articles.extend(articles)
                    logger.info(f"GDELT Strategy 1 found {len(articles)} articles")
            except Exception as e:
                logger.error(f"GDELT Strategy 1 failed: {e}")
            
            # Strategy 2: Domain-filtered search for major news sources
            try:
                major_domains = "domain:nytimes.com OR domain:reuters.com OR domain:bbc.com OR domain:cnn.com OR domain:foxnews.com"
                params = {
                    'query': f'({query}) AND ({major_domains})',
                    'mode': 'artlist',
                    'maxrecords': limit // 2,
                    'format': 'json',
                    'sort': 'hybridrel',
                    'startdatetime': '20250101000000',
                    'enddatetime': '20251231235959'
                }
                
                response = requests.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if 'articles' in data:
                    articles = self._process_gdelt_results(data['articles'])
                    all_articles.extend(articles)
                    logger.info(f"GDELT Strategy 2 found {len(articles)} articles")
            except Exception as e:
                logger.error(f"GDELT Strategy 2 failed: {e}")
            
            # Remove duplicates and limit
            unique_articles = self._deduplicate_articles(all_articles)
            return unique_articles[:limit]
            
        except Exception as e:
            logger.error(f"GDELT search error: {e}")
            return []
    
    def _process_gdelt_results(self, gdelt_articles: List[Dict]) -> List[Dict]:
        """Process GDELT results into standardized format"""
        articles = []
        for gdelt_article in gdelt_articles:
            article = {
                'title': gdelt_article.get('title', ''),
                'content': gdelt_article.get('title', ''),  # GDELT often only has title
                'url': gdelt_article.get('url', ''),
                'source': gdelt_article.get('domain', 'GDELT'),
                'published_at': gdelt_article.get('seendate', datetime.now().isoformat()),
                'description': gdelt_article.get('seendate', ''),
                'urlToImage': '',
                'api_source': 'GDELT'
            }
            articles.append(article)
        return articles
    
    def _deduplicate_articles(self, articles: List[Dict]) -> List[Dict]:
        """Remove duplicate articles based on URL"""
        seen_urls = set()
        unique_articles = []
        
        for article in articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)
        
        return unique_articles

def create_news_tools(api_keys: Dict[str, str]) -> List[Tool]:
    """Create all news tools with proper configuration"""
    tools = []
    
    # NewsAPI tool
    if api_keys.get('news_api_key'):
        news_api_tool = NewsAPITool(api_keys['news_api_key'])
        tools.append(Tool(
            name=news_api_tool.name,
            description=news_api_tool.description,
            func=news_api_tool._run
        ))
    
    # Google News tool
    google_news_tool = GoogleNewsTool()
    tools.append(Tool(
        name=google_news_tool.name,
        description=google_news_tool.description,
        func=google_news_tool._run
    ))
    
    # RSS tool
    rss_tool = RSSTool()
    tools.append(Tool(
        name=rss_tool.name,
        description=rss_tool.description,
        func=rss_tool._run
    ))
    
    # GDELT tool
    gdelt_tool = GDELTTool()
    tools.append(Tool(
        name=gdelt_tool.name,
        description=gdelt_tool.description,
        func=gdelt_tool._run
    ))
    
    return tools
