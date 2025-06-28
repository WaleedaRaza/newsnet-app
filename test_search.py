#!/usr/bin/env python3
import requests
import json

def test_search():
    url = "http://localhost:8000/v1/articles/search"
    
    # Test the same query that was problematic before
    params = {
        "q": "Palestine I oppose the occupation of Israel",
        "bias": 1.0,  # "Prove me right" - want supporting views
        "limit": 10
    }
    
    print("🔍 TESTING IMPROVED SEARCH STRATEGY")
    print("=" * 50)
    print(f"Query: {params['q']}")
    print(f"Bias: {params['bias']} (Prove me right)")
    print(f"Limit: {params['limit']}")
    print()
    
    try:
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            
            print(f"✅ Found {len(articles)} articles")
            print()
            
            # Analyze results
            total_bias_match = 0
            total_relevance = 0
            total_final_score = 0
            stance_counts = {}
            
            for i, article in enumerate(articles, 1):
                bias_analysis = article.get('bias_analysis', {})
                
                print(f"{i}. {article.get('title', 'No title')[:80]}...")
                print(f"   Source: {article.get('source', {}).get('name', 'Unknown')}")
                print(f"   Stance: {bias_analysis.get('stance', 'unknown')} (conf: {bias_analysis.get('stance_confidence', 0):.2f})")
                print(f"   Bias Match: {bias_analysis.get('bias_match', 0):.3f}")
                print(f"   Relevance: {bias_analysis.get('relevance_score', 0):.3f}")
                print(f"   Final Score: {bias_analysis.get('final_score', 0):.3f}")
                
                # Check relevance
                content = f"{article.get('title', '')} {article.get('description', '')}".lower()
                has_palestine = 'palestine' in content
                has_israel = 'israel' in content
                has_occupation = 'occupation' in content
                print(f"   Contains Palestine: {has_palestine}, Israel: {has_israel}, Occupation: {has_occupation}")
                print()
                
                # Accumulate stats
                total_bias_match += bias_analysis.get('bias_match', 0)
                total_relevance += bias_analysis.get('relevance_score', 0)
                total_final_score += bias_analysis.get('final_score', 0)
                
                stance = bias_analysis.get('stance', 'unknown')
                stance_counts[stance] = stance_counts.get(stance, 0) + 1
            
            # Print summary
            if articles:
                print("📊 SUMMARY:")
                print(f"   Average Bias Match: {total_bias_match/len(articles):.3f}")
                print(f"   Average Relevance: {total_relevance/len(articles):.3f}")
                print(f"   Average Final Score: {total_final_score/len(articles):.3f}")
                print(f"   Stance Distribution: {stance_counts}")
                
                # Count relevant articles
                relevant_count = sum(1 for a in articles 
                                   if 'palestine' in f"{a.get('title', '')} {a.get('description', '')}".lower())
                print(f"   Articles mentioning Palestine: {relevant_count}/{len(articles)}")
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_search() 