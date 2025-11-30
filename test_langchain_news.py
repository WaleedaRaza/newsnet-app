#!/usr/bin/env python3
"""
Test script for LangChain-powered Intelligent News Engine
Demonstrates LLM-based news retrieval, stance detection, and narrative synthesis
"""

import asyncio
import os
import sys
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.services.langchain_news_engine import LangChainNewsEngine, UserQuery, NewsAnalysis

async def test_langchain_news_engine():
    """Test the LangChain news engine with a real query"""
    
    print("🧠 LANGCHAIN NEWS ENGINE TEST")
    print("=" * 60)
    
    # Get OpenAI API key
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return
    
    try:
        # Initialize the LangChain news engine
        print("🔧 Initializing LangChain News Engine...")
        news_engine = LangChainNewsEngine(openai_api_key)
        print("✅ LangChain News Engine initialized successfully")
        
        # Test query with bias preference
        test_queries = [
            UserQuery(
                topic="MAGA",
                user_belief="I hate MAGA and think it's ruining America",
                bias_slider=0.0,  # Challenge me
                limit=10
            ),
            UserQuery(
                topic="MAGA", 
                user_belief="I hate MAGA and think it's ruining America",
                bias_slider=1.0,  # Affirm me
                limit=10
            ),
            UserQuery(
                topic="climate change",
                user_belief="Climate change is a serious threat that needs immediate action",
                bias_slider=0.5,  # Balanced
                limit=10
            )
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n🔍 TEST {i}: {query.topic}")
            print(f"User Belief: '{query.user_belief}'")
            print(f"Bias Slider: {query.bias_slider} ({'Challenge' if query.bias_slider < 0.5 else 'Affirm'})")
            print("-" * 40)
            
            # Perform intelligent news search
            start_time = datetime.now()
            analysis = await news_engine.search_news_intelligent(query)
            end_time = datetime.now()
            
            # Display results
            print(f"⏱️  Search completed in: {(end_time - start_time).total_seconds():.2f} seconds")
            print(f"📰 Found {len(analysis.articles)} articles")
            
            # Display article analysis
            print("\n📋 ARTICLE ANALYSIS:")
            for j, article in enumerate(analysis.articles[:5], 1):  # Show top 5
                print(f"\n{j}. {article.title}")
                print(f"   Source: {article.source}")
                print(f"   Stance: {article.llm_stance} (confidence: {article.llm_confidence:.2f})")
                print(f"   Bias Score: {article.llm_bias_score:.2f}")
                print(f"   Framing: {article.llm_framing}")
                if article.llm_omissions:
                    print(f"   Omissions: {', '.join(article.llm_omissions[:2])}")
                print(f"   URL: {article.url}")
            
            # Display narrative synthesis
            print(f"\n🧠 NARRATIVE SYNTHESIS:")
            print(analysis.narrative_fusion[:500] + "..." if len(analysis.narrative_fusion) > 500 else analysis.narrative_fusion)
            
            # Display stance comparison
            print(f"\n📊 STANCE COMPARISON:")
            for source, articles in analysis.stance_comparison.items():
                stances = [a['stance'] for a in articles if a['stance']]
                if stances:
                    stance_counts = {}
                    for stance in stances:
                        stance_counts[stance] = stance_counts.get(stance, 0) + 1
                    print(f"   {source}: {stance_counts}")
            
            # Display bias analysis
            print(f"\n🎯 BIAS ANALYSIS:")
            bias_analysis = analysis.bias_analysis
            print(f"   User Belief: {bias_analysis.get('user_belief', 'N/A')}")
            print(f"   Bias Preference: {bias_analysis.get('bias_preference', 'N/A')}")
            print(f"   Articles Analyzed: {bias_analysis.get('articles_analyzed', 0)}")
            print(f"   Stance Distribution: {bias_analysis.get('stance_distribution', {})}")
            
            print("\n" + "=" * 60)
        
        # Test vector store query
        print("\n🔍 TESTING VECTOR STORE QUERY:")
        vector_results = await news_engine.query_vector_store("MAGA politics", k=5)
        print(f"Found {len(vector_results)} similar articles in vector store")
        
        # Display system metrics
        print("\n📈 SYSTEM METRICS:")
        metrics = news_engine.get_metrics()
        for key, value in metrics.items():
            print(f"   {key}: {value}")
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

async def test_llm_stance_detection():
    """Test LLM-based stance detection specifically"""
    
    print("\n🧠 TESTING LLM STANCE DETECTION")
    print("=" * 40)
    
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("❌ OPENAI_API_KEY not set")
        return
    
    try:
        news_engine = LangChainNewsEngine(openai_api_key)
        
        # Test articles with known stances
        test_articles = [
            {
                'title': 'MAGA Supporters Rally in Support of Trump',
                'content': 'Thousands of MAGA supporters gathered today to show their support for former President Trump and his America First agenda. The rally featured speakers who praised Trump\'s policies and criticized the current administration.',
                'expected_stance': 'support'
            },
            {
                'title': 'Critics Slam MAGA Movement as Divisive',
                'content': 'Political analysts and critics argue that the MAGA movement has been deeply divisive for American democracy. They point to increased polarization and the spread of misinformation as major concerns.',
                'expected_stance': 'oppose'
            },
            {
                'title': 'MAGA Movement: A Political Analysis',
                'content': 'The MAGA movement represents a significant shift in American politics. This article examines both the movement\'s impact on Republican politics and the broader implications for American democracy.',
                'expected_stance': 'neutral'
            }
        ]
        
        user_belief = "I hate MAGA and think it's ruining America"
        
        for i, article in enumerate(test_articles, 1):
            print(f"\n📰 Test Article {i}: {article['title']}")
            print(f"Expected stance: {article['expected_stance']}")
            
            # Test stance detection
            stance_result = await news_engine.stance_chain.arun(
                belief=user_belief,
                title=article['title'],
                content=article['content']
            )
            
            print(f"LLM stance result: {stance_result}")
            print("-" * 30)
        
        print("✅ Stance detection tests completed!")
        
    except Exception as e:
        print(f"❌ Error in stance detection test: {e}")

if __name__ == "__main__":
    print("🚀 Starting LangChain News Engine Tests")
    print("Make sure you have set your OPENAI_API_KEY environment variable")
    print()
    
    # Run tests
    asyncio.run(test_langchain_news_engine())
    asyncio.run(test_llm_stance_detection())
    
    print("\n🎉 All tests completed!") 