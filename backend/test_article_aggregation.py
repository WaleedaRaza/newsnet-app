#!/usr/bin/env python3
"""
Test script for article aggregation functionality
"""
import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.article_retrieval_service import ArticleRetrievalService
from services.bias_scoring_service import BiasScoringService
from services.article_aggregator import ArticleAggregator

async def test_article_retrieval():
    """Test article retrieval service"""
    print("🧪 Testing Article Retrieval Service...")
    
    retrieval_service = ArticleRetrievalService()
    
    # Test fetching articles for a topic
    articles = await retrieval_service.fetch_articles_for_topic("ai", limit=5)
    
    print(f"✅ Retrieved {len(articles)} articles for 'ai' topic")
    
    if articles:
        print(f"📰 Sample article: {articles[0].get('title', 'No title')}")
        print(f"🔗 Source: {articles[0].get('source', {}).get('name', 'Unknown')}")
    
    return articles

async def test_bias_scoring():
    """Test bias scoring service"""
    print("\n🧪 Testing Bias Scoring Service...")
    
    scoring_service = BiasScoringService()
    
    # Test ideological scoring
    test_domains = ["reuters.com", "cnn.com", "foxnews.com"]
    bias_slider = 0.5
    
    for domain in test_domains:
        score = scoring_service.calculate_ideological_score(domain, bias_slider)
        bias_info = scoring_service.get_source_bias_info(domain)
        print(f"📊 {domain}: Bias={bias_info['bias']}, Score={score:.2f}")
    
    return True

async def test_article_aggregation():
    """Test full article aggregation pipeline"""
    print("\n🧪 Testing Article Aggregation Pipeline...")
    
    aggregator = ArticleAggregator()
    
    # Test parameters
    topics = ["ai"]
    beliefs = {
        "ai": ["I support AI development", "AI will improve society"]
    }
    bias_slider = 0.5
    
    try:
        articles = await aggregator.aggregate_articles(
            topics=topics,
            beliefs=beliefs,
            bias_slider=bias_slider,
            limit_per_topic=3
        )
        
        print(f"✅ Aggregated {len(articles)} articles")
        
        if articles:
            print("\n📋 Sample Results:")
            for i, article in enumerate(articles[:3]):
                print(f"{i+1}. {article.title}")
                print(f"   Source: {article.source_name} ({article.source_bias})")
                print(f"   Scores: Topical={article.topical_score:.2f}, Belief={article.belief_alignment_score:.2f}, Ideological={article.ideological_score:.2f}")
                print(f"   Final Score: {article.final_score:.2f}")
                print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error in aggregation: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting Article Aggregation Tests...\n")
    
    # Test 1: Article Retrieval
    try:
        await test_article_retrieval()
    except Exception as e:
        print(f"❌ Article retrieval test failed: {e}")
    
    # Test 2: Bias Scoring
    try:
        await test_bias_scoring()
    except Exception as e:
        print(f"❌ Bias scoring test failed: {e}")
    
    # Test 3: Full Aggregation
    try:
        success = await test_article_aggregation()
        if success:
            print("🎉 All tests completed successfully!")
        else:
            print("❌ Some tests failed")
    except Exception as e:
        print(f"❌ Article aggregation test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 