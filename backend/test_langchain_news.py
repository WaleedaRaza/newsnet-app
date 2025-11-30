#!/usr/bin/env python3
"""
Test script for LangChain-powered news engine
"""

import asyncio
import json
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import LangChain components
try:
    from services.langchain_news_engine import LangChainNewsEngine
    from config import get_api_keys
    print("✅ Successfully imported LangChain components")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure all dependencies are installed:")
    print("pip install -r requirements_langchain.txt")
    exit(1)

async def test_langchain_news_engine():
    """Test the LangChain news engine with various queries"""
    
    print("\n🧠 Testing LangChain News Engine")
    print("=" * 50)
    
    try:
        # Get API keys
        api_keys = get_api_keys()
        print(f"📋 API Keys available: {list(api_keys.keys())}")
        
        # Initialize LangChain news engine
        news_engine = LangChainNewsEngine(api_keys)
        print("✅ LangChain news engine initialized")
        
        # Test health check
        print("\n🏥 Testing health check...")
        health_status = await news_engine.health_check()
        print(f"Health status: {health_status}")
        
        # Test queries
        test_queries = [
            {
                "query": "climate change",
                "bias_preference": 0.8,
                "description": "Pro-climate action bias"
            },
            {
                "query": "artificial intelligence regulation",
                "bias_preference": 0.3,
                "description": "Skeptical of AI regulation"
            },
            {
                "query": "economic policy",
                "bias_preference": 0.5,
                "description": "Balanced view"
            }
        ]
        
        for i, test_case in enumerate(test_queries, 1):
            print(f"\n🔍 Test {i}: {test_case['description']}")
            print(f"Query: '{test_case['query']}' with bias {test_case['bias_preference']}")
            print("-" * 40)
            
            try:
                # Perform intelligent search
                result = await news_engine.intelligent_search(
                    query=test_case['query'],
                    bias_preference=test_case['bias_preference'],
                    limit=5,
                    include_analysis=True
                )
                
                # Display results
                articles = result.get('articles', [])
                print(f"📰 Found {len(articles)} articles")
                
                for j, article in enumerate(articles, 1):
                    print(f"\n  Article {j}:")
                    print(f"    Title: {article.get('title', 'N/A')[:60]}...")
                    print(f"    Source: {article.get('source', 'N/A')}")
                    print(f"    Stance: {article.get('stance', 'N/A')}")
                    print(f"    Confidence: {article.get('confidence', 0):.2f}")
                    print(f"    Bias Match: {article.get('bias_match', 0):.2f}")
                    print(f"    Relevance: {article.get('relevance_score', 0):.2f}")
                    print(f"    Final Score: {article.get('final_score', 0):.2f}")
                
                # Display analysis if available
                if result.get('analysis'):
                    analysis = result['analysis']
                    print(f"\n  📊 Analysis:")
                    if analysis.get('narrative_synthesis'):
                        print(f"    Narrative: {analysis['narrative_synthesis'][:100]}...")
                    if analysis.get('stance_distribution'):
                        print(f"    Stance Distribution: {analysis['stance_distribution']}")
                    if analysis.get('bias_analysis'):
                        print(f"    Bias Analysis: {analysis['bias_analysis'][:100]}...")
                
                # Display search metadata
                if result.get('search_metadata'):
                    metadata = result['search_metadata']
                    print(f"\n  🔍 Search Metadata:")
                    print(f"    Sources Used: {metadata.get('sources_used', [])}")
                    print(f"    Search Time: {metadata.get('search_time', 0):.2f}s")
                
            except Exception as e:
                print(f"❌ Test {i} failed: {e}")
                continue
        
        print("\n✅ LangChain news engine test completed!")
        
    except Exception as e:
        print(f"❌ LangChain test failed: {e}")
        import traceback
        traceback.print_exc()

async def test_langchain_tools():
    """Test individual LangChain tools"""
    
    print("\n🔧 Testing LangChain Tools")
    print("=" * 50)
    
    try:
        from services.langchain_news_tools import create_news_tools
        from config import get_api_keys
        
        api_keys = get_api_keys()
        tools = create_news_tools(api_keys)
        
        print(f"📋 Created {len(tools)} tools:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")
        
        # Test Google News tool
        google_news_tool = next((t for t in tools if 'google_news' in t.name), None)
        if google_news_tool:
            print(f"\n🔍 Testing {google_news_tool.name}...")
            try:
                result = google_news_tool.func("climate change", 0.5, 3)
                print(f"✅ {google_news_tool.name} returned {len(result)} articles")
                for i, article in enumerate(result[:2], 1):
                    print(f"  Article {i}: {article.get('title', 'N/A')[:50]}...")
            except Exception as e:
                print(f"❌ {google_news_tool.name} failed: {e}")
        
        print("\n✅ LangChain tools test completed!")
        
    except Exception as e:
        print(f"❌ LangChain tools test failed: {e}")

async def main():
    """Main test function"""
    print("🚀 Starting LangChain News Engine Tests")
    print("=" * 60)
    
    # Test tools first
    await test_langchain_tools()
    
    # Test full engine
    await test_langchain_news_engine()
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    asyncio.run(main()) 