#!/usr/bin/env python3
"""
Test stance detection search functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.stance_detector import stance_detector
from services.article_retrieval_service import ArticleRetrievalService
import asyncio

async def test_stance_search():
    """Test the stance-based search functionality"""
    
    print("🧪 Testing Stance-Based Search")
    print("=" * 50)
    
    # Initialize service
    service = ArticleRetrievalService()
    
    # Test cases
    test_queries = [
        {
            "query": "trump I hate him",
            "bias": 0.0,  # Want challenging views
            "expected": "Should find articles that oppose Trump"
        },
        {
            "query": "trump I love him", 
            "bias": 1.0,  # Want supporting views
            "expected": "Should find articles that support Trump"
        },
        {
            "query": "NATO escalation",
            "bias": 0.5,  # Neutral
            "expected": "Should find balanced mix"
        }
    ]
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n📋 Test {i}: {test_case['query']} (bias: {test_case['bias']})")
        print(f"Expected: {test_case['expected']}")
        print("-" * 40)
        
        try:
            # Test search
            articles = await service.search_articles(
                query=test_case["query"],
                bias=test_case["bias"],
                limit=3
            )
            
            print(f"Found {len(articles)} articles")
            
            for j, article in enumerate(articles, 1):
                bias_analysis = article.get('bias_analysis', {})
                stance = bias_analysis.get('stance', 'unknown')
                confidence = bias_analysis.get('stance_confidence', 0.0)
                bias_match = bias_analysis.get('bias_match', 0.0)
                user_belief = bias_analysis.get('user_belief', '')
                
                stance_emoji = {
                    "support": "✅",
                    "oppose": "❌",
                    "neutral": "➖"
                }.get(stance, "❓")
                
                print(f"  Article {j}: {stance_emoji} {stance.upper()}")
                print(f"    Title: {article.get('title', 'No title')}")
                print(f"    Stance Confidence: {confidence:.2f}")
                print(f"    Bias Match: {bias_match:.2f}")
                print(f"    User Belief: {user_belief}")
                
                if bias_analysis.get('stance_evidence'):
                    print(f"    Evidence: {', '.join(bias_analysis['stance_evidence'][:2])}")
                print()
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

def test_stance_detection_directly():
    """Test stance detection directly with sample articles"""
    
    print("\n🔍 Testing Stance Detection Directly")
    print("=" * 40)
    
    # Sample articles
    articles = [
        {
            "title": "Trump faces new legal challenges",
            "description": "Former president confronts multiple lawsuits and investigations as legal pressure mounts."
        },
        {
            "title": "Trump defends his record on economy",
            "description": "Former president highlights job creation and economic growth during his administration."
        },
        {
            "title": "Biden administration announces new policies",
            "description": "White House introduces measures to address economic concerns and support middle class."
        }
    ]
    
    user_belief = "trump I hate him"
    
    print(f"User Belief: '{user_belief}'")
    print()
    
    for i, article in enumerate(articles, 1):
        content = f"{article['title']} {article['description']}"
        
        stance_result = stance_detector.classify_stance(content, user_belief)
        
        stance_emoji = {
            "support": "✅",
            "oppose": "❌",
            "neutral": "➖"
        }.get(stance_result["stance"], "❓")
        
        print(f"Article {i}: {stance_emoji} {stance_result['stance'].upper()}")
        print(f"  Title: {article['title']}")
        print(f"  Confidence: {stance_result['confidence']:.2f}")
        print(f"  Method: {stance_result['method']}")
        if stance_result.get('evidence'):
            print(f"  Evidence: {', '.join(stance_result['evidence'][:2])}")
        print()

if __name__ == "__main__":
    try:
        # Test stance detection directly first
        test_stance_detection_directly()
        
        # Test full search (if News API is available)
        print("\n" + "="*60)
        print("Testing Full Search (requires News API)")
        print("="*60)
        
        asyncio.run(test_stance_search())
        
        print("\n🎉 Stance-based search testing completed!")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc() 