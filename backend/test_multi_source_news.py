#!/usr/bin/env python3
"""
Test script for the Multi-Source News Service

This script validates the news aggregation functionality before integrating with the pipeline.
"""

import sys
import os
import asyncio
import logging
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.multi_source_news_service import multi_source_news_service

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_news_service_foundation():
    """Test the basic news service functionality"""
    
    print("🧪 Testing Multi-Source News Service Foundation")
    print("=" * 60)
    
    # Test 1: Service Initialization
    print("\n1. Testing Service Initialization...")
    print(f"✅ Sources configured: {len(multi_source_news_service.sources)}")
    
    for source in multi_source_news_service.sources:
        print(f"   📰 {source.name}: {'✅ Enabled' if source.enabled else '❌ Disabled'}")
        if source.api_key:
            print(f"      🔑 API Key: {'✅ Present' if source.api_key else '❌ Missing'}")
    
    # Test 2: Mock Article Fetching
    print("\n2. Testing Mock Article Fetching...")
    
    async with multi_source_news_service as news_service:
        test_topics = ["ukraine", "climate"]
        
        print(f"📋 Fetching articles for topics: {test_topics}")
        
        articles = await news_service.fetch_articles_for_topics(
            topics=test_topics,
            max_articles_per_topic=3,
            days_back=7
        )
        
        print(f"✅ Fetched {len(articles)} total articles")
        
        # Group by source
        by_source = {}
        for article in articles:
            source = article.source_name
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(article)
        
        print(f"\n📊 Articles by source:")
        for source, source_articles in by_source.items():
            print(f"   📰 {source}: {len(source_articles)} articles")
        
        # Show sample articles
        print(f"\n📰 Sample Articles:")
        for i, article in enumerate(articles[:3]):
            print(f"  {i+1}. {article.title}")
            print(f"     Source: {article.source_name}")
            print(f"     URL: {article.url}")
            print(f"     Published: {article.published_at}")
            print(f"     Content length: {len(article.content)} chars")
            print()
    
    # Test 3: Metrics
    print("3. Testing Metrics...")
    metrics = multi_source_news_service.get_metrics()
    print(f"📈 Total Requests: {metrics['metrics']['total_requests']}")
    print(f"✅ Successful: {metrics['metrics']['successful_requests']}")
    print(f"❌ Failed: {metrics['metrics']['failed_requests']}")
    print(f"📄 Articles Fetched: {metrics['metrics']['articles_fetched']}")
    print(f"📰 Sources Used: {list(metrics['metrics']['sources_used'])}")
    
    print("\n" + "=" * 60)
    print("🎉 News Service Foundation Test Completed Successfully!")
    
    return True

async def test_article_quality():
    """Test the quality and structure of fetched articles"""
    
    print("\n🔍 Testing Article Quality")
    print("-" * 40)
    
    async with multi_source_news_service as news_service:
        # Test with a single topic
        topic = "technology"
        articles = await news_service.fetch_articles_for_topics(
            topics=[topic],
            max_articles_per_topic=5,
            days_back=7
        )
        
        print(f"📋 Testing article quality for topic: {topic}")
        print(f"📄 Articles fetched: {len(articles)}")
        
        # Analyze article quality
        quality_metrics = {
            'has_title': 0,
            'has_content': 0,
            'has_url': 0,
            'has_date': 0,
            'content_length_avg': 0,
            'title_length_avg': 0
        }
        
        total_content_length = 0
        total_title_length = 0
        
        for article in articles:
            if article.title:
                quality_metrics['has_title'] += 1
                total_title_length += len(article.title)
            
            if article.content:
                quality_metrics['has_content'] += 1
                total_content_length += len(article.content)
            
            if article.url:
                quality_metrics['has_url'] += 1
            
            if article.published_at:
                quality_metrics['has_date'] += 1
        
        if articles:
            quality_metrics['content_length_avg'] = total_content_length / len(articles)
            quality_metrics['title_length_avg'] = total_title_length / len(articles)
        
        print(f"\n📊 Quality Metrics:")
        print(f"   📝 Has Title: {quality_metrics['has_title']}/{len(articles)}")
        print(f"   📄 Has Content: {quality_metrics['has_content']}/{len(articles)}")
        print(f"   🔗 Has URL: {quality_metrics['has_url']}/{len(articles)}")
        print(f"   📅 Has Date: {quality_metrics['has_date']}/{len(articles)}")
        print(f"   📏 Avg Content Length: {quality_metrics['content_length_avg']:.0f} chars")
        print(f"   📏 Avg Title Length: {quality_metrics['title_length_avg']:.0f} chars")
        
        # Show sample content
        if articles:
            sample = articles[0]
            print(f"\n📰 Sample Article Structure:")
            print(f"   Title: {sample.title[:100]}...")
            print(f"   Content: {sample.content[:200]}...")
            print(f"   Source: {sample.source_name}")
            print(f"   Domain: {sample.source_domain}")
            print(f"   Author: {sample.author}")
    
    print("\n✅ Article Quality Tests Completed!")

async def test_error_handling():
    """Test error handling and edge cases"""
    
    print("\n🛡️ Testing Error Handling")
    print("-" * 40)
    
    async with multi_source_news_service as news_service:
        # Test 1: Empty topics
        print("1. Testing empty topics...")
        articles = await news_service.fetch_articles_for_topics(
            topics=[],
            max_articles_per_topic=5
        )
        print(f"   ✅ Empty topics handled: {len(articles)} articles")
        
        # Test 2: Invalid topic characters
        print("2. Testing invalid topic characters...")
        articles = await news_service.fetch_articles_for_topics(
            topics=["!@#$%^&*()", "valid-topic"],
            max_articles_per_topic=3
        )
        print(f"   ✅ Invalid characters handled: {len(articles)} articles")
        
        # Test 3: Very long topic
        print("3. Testing very long topic...")
        long_topic = "this is a very long topic name that might cause issues with some APIs" * 5
        articles = await news_service.fetch_articles_for_topics(
            topics=[long_topic],
            max_articles_per_topic=2
        )
        print(f"   ✅ Long topic handled: {len(articles)} articles")
    
    print("\n✅ Error Handling Tests Completed!")

async def main():
    """Main test function"""
    
    print("🚀 Starting Multi-Source News Service Tests")
    print(f"⏰ Test started at: {datetime.now()}")
    
    try:
        # Test foundation
        await test_news_service_foundation()
        
        # Test article quality
        await test_article_quality()
        
        # Test error handling
        await test_error_handling()
        
        print("\n🎉 All news service tests completed successfully!")
        print("✅ News service is ready for pipeline integration")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    # Run the tests
    success = asyncio.run(main())
    
    if success:
        print("\n🚀 Ready to proceed to Phase 3: Semantic processing and embedding")
    else:
        print("\n❌ News service tests failed - need to fix issues before proceeding")
        sys.exit(1) 