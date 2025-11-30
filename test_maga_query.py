#!/usr/bin/env python3
"""
Test script for MAGA query with improved system
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.services.article_retrieval_service import ArticleRetrievalService

async def test_maga_query():
    """Test the MAGA query with improved system"""
    
    print("🔍 TESTING MAGA QUERY WITH IMPROVED SYSTEM")
    print("=" * 60)
    
    # Initialize services
    retrieval_service = ArticleRetrievalService()
    
    # Test query
    query = "maga I hate it"
    bias = 1.0  # Supporting views
    
    print(f"Query: '{query}'")
    print(f"Bias: {bias}")
    print()
    
    try:
        # Search for articles
        articles = await retrieval_service.search_articles(
            query=query,
            bias=bias,
            limit=10
        )
        
        print(f"✅ Found {len(articles)} articles")
        print()
        
        # Display results
        for i, article in enumerate(articles[:5], 1):
            title = article.get('title', 'No title')
            source = article.get('source', {}).get('name', 'Unknown') if isinstance(article.get('source'), dict) else str(article.get('source', 'Unknown'))
            
            # Get analysis results
            bias_analysis = article.get('bias_analysis', {})
            stance = bias_analysis.get('stance', 'unknown')
            confidence = bias_analysis.get('confidence', 0)
            bias_match = bias_analysis.get('bias_match', 0)
            relevance_score = bias_analysis.get('relevance_score', 0)
            final_score = bias_analysis.get('final_score', 0)
            
            print(f"  {i}. {title}")
            print(f"     Source: {source}")
            print(f"     Stance: {stance} (confidence: {confidence:.3f})")
            print(f"     Bias Match: {bias_match:.3f}")
            print(f"     Relevance: {relevance_score:.3f}")
            print(f"     Final Score: {final_score:.3f}")
            print()
        
        # Summary statistics
        if articles:
            total_bias_match = sum(article.get('bias_analysis', {}).get('bias_match', 0) for article in articles)
            total_relevance = sum(article.get('bias_analysis', {}).get('relevance_score', 0) for article in articles)
            total_final = sum(article.get('bias_analysis', {}).get('final_score', 0) for article in articles)
            
            print("📊 SUMMARY STATISTICS:")
            print(f"   - Average Bias Match: {total_bias_match/len(articles):.3f}")
            print(f"   - Average Relevance: {total_relevance/len(articles):.3f}")
            print(f"   - Average Final Score: {total_final/len(articles):.3f}")
            
            # Source diversity
            sources = {}
            for article in articles:
                source = article.get('source', {}).get('name', 'Unknown') if isinstance(article.get('source'), dict) else str(article.get('source', 'Unknown'))
                sources[source] = sources.get(source, 0) + 1
            
            print(f"   - Sources used: {len(sources)}")
            print(f"   - Top sources: {dict(sorted(sources.items(), key=lambda x: x[1], reverse=True)[:3])}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_maga_query()) 