import asyncio
from typing import List, Dict
import httpx
from newsapi import NewsApiClient
from config import settings

class ArticleRetrievalService:
    def __init__(self):
        self.news_api = NewsApiClient(api_key=settings.news_api_key)
        self.topic_expansions = self._load_topic_expansions()
    
    def _load_topic_expansions(self) -> Dict[str, List[str]]:
        """Load keyword expansions for topics"""
        return {
            "ukraine": ["ukraine", "russia", "nato", "zelensky", "putin", "donbas"],
            "ai": ["artificial intelligence", "machine learning", "chatgpt", "openai"],
            "climate": ["climate change", "global warming", "environment", "carbon"],
            "covid": ["covid", "coronavirus", "pandemic", "vaccine"],
            "economy": ["economy", "economic", "market", "trade", "business"],
            "politics": ["politics", "election", "government", "congress", "senate"],
            "technology": ["technology", "tech", "software", "digital", "innovation"],
            "health": ["health", "medical", "healthcare", "medicine", "hospital"],
            "sports": ["sports", "football", "basketball", "baseball", "soccer"],
            "entertainment": ["entertainment", "movie", "film", "celebrity", "hollywood"],
        }
    
    async def fetch_articles_for_topic(self, topic: str, limit: int = 30) -> List[Dict]:
        """Fetch articles from News API for a given topic"""
        try:
            # Get expanded keywords
            keywords = self.topic_expansions.get(topic.lower(), [topic])
            
            # Search for articles
            response = self.news_api.get_everything(
                q=' OR '.join(keywords),
                language='en',
                sort_by='publishedAt',
                page_size=limit
            )
            
            return response['articles']
        except Exception as e:
            print(f"Error fetching articles for topic {topic}: {e}")
            return []
    
    async def fetch_articles_for_multiple_topics(self, topics: List[str], limit_per_topic: int = 30) -> Dict[str, List[Dict]]:
        """Fetch articles for multiple topics"""
        results = {}
        
        for topic in topics:
            articles = await self.fetch_articles_for_topic(topic, limit_per_topic)
            results[topic] = articles
        
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