#!/usr/bin/env python3
import requests
import json

def test_universal_search():
    """Test the universal search system with different topics"""
    
    test_cases = [
        {
            "query": "Climate change I believe it's a serious threat",
            "bias": 1.0,  # "Prove me right" - want supporting views
            "description": "Climate change - supporting views"
        },
        {
            "query": "Vaccines I think they're dangerous",
            "bias": 0.0,  # "Prove me wrong" - want challenging views
            "description": "Vaccines - challenging views"
        },
        {
            "query": "AI I love artificial intelligence",
            "bias": 0.8,  # "Prove me right" - want supporting views
            "description": "AI - supporting views"
        },
        {
            "query": "Capitalism I oppose the system",
            "bias": 0.2,  # "Prove me wrong" - want challenging views
            "description": "Capitalism - challenging views"
        }
    ]
    
    print("🔍 TESTING UNIVERSAL SEARCH SYSTEM")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 TEST {i}: {test_case['description']}")
        print("-" * 40)
        print(f"Query: {test_case['query']}")
        print(f"Bias: {test_case['bias']}")
        
        url = "http://localhost:8000/v1/articles/search"
        params = {
            "q": test_case['query'],
            "bias": test_case['bias'],
            "limit": 5
        }
        
        try:
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                print(f"✅ Found {len(articles)} articles")
                
                # Show top 3 articles with their scores
                for j, article in enumerate(articles[:3], 1):
                    bias_analysis = article.get('bias_analysis', {})
                    print(f"\n  {j}. {article.get('title', 'No title')[:60]}...")
                    print(f"     Source: {article.get('source', {}).get('name', 'Unknown')}")
                    print(f"     Stance: {bias_analysis.get('stance', 'Unknown')} (confidence: {bias_analysis.get('stance_confidence', 0):.2f})")
                    print(f"     Bias Match: {bias_analysis.get('bias_match', 0):.3f}")
                    print(f"     Relevance: {bias_analysis.get('relevance_score', 0):.3f}")
                    print(f"     Final Score: {bias_analysis.get('final_score', 0):.3f}")
                
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
        
        print("\n" + "=" * 60)

if __name__ == "__main__":
    test_universal_search() 