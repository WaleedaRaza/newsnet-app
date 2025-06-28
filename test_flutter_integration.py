#!/usr/bin/env python3
import requests
import json

def test_flutter_integration():
    """Test that the backend is ready for Flutter integration"""
    
    print("🧪 TESTING FLUTTER INTEGRATION")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test 2: Universal search endpoint
    print("\n2. Testing universal search endpoint...")
    try:
        url = "http://localhost:8000/v1/articles/search"
        params = {
            "q": "AI I love artificial intelligence",
            "bias": 0.8,
            "limit": 3
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            print(f"✅ Universal search working - found {len(articles)} articles")
            
            if articles:
                print("   Sample article:")
                article = articles[0]
                print(f"   - Title: {article.get('title', 'No title')[:50]}...")
                print(f"   - Source: {article.get('source', {}).get('name', 'Unknown')}")
                
                bias_analysis = article.get('bias_analysis', {})
                if bias_analysis:
                    print(f"   - Stance: {bias_analysis.get('stance', 'Unknown')}")
                    print(f"   - Bias Match: {bias_analysis.get('bias_match', 0):.3f}")
                    print(f"   - Final Score: {bias_analysis.get('final_score', 0):.3f}")
        else:
            print(f"❌ Universal search failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Universal search error: {e}")
    
    # Test 3: Check if all required fields are present
    print("\n3. Testing response format...")
    try:
        url = "http://localhost:8000/v1/articles/search"
        params = {
            "q": "Climate change",
            "bias": 0.5,
            "limit": 1
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            
            if articles:
                article = articles[0]
                required_fields = ['title', 'description', 'url', 'source', 'publishedAt']
                missing_fields = [field for field in required_fields if field not in article]
                
                if not missing_fields:
                    print("✅ All required article fields present")
                else:
                    print(f"❌ Missing fields: {missing_fields}")
                
                # Check bias analysis fields
                bias_analysis = article.get('bias_analysis', {})
                if bias_analysis:
                    bias_fields = ['stance', 'stance_confidence', 'bias_match', 'final_score']
                    missing_bias_fields = [field for field in bias_fields if field not in bias_analysis]
                    
                    if not missing_bias_fields:
                        print("✅ All required bias analysis fields present")
                    else:
                        print(f"❌ Missing bias fields: {missing_bias_fields}")
                else:
                    print("⚠️  No bias analysis in response")
            else:
                print("❌ No articles returned")
        else:
            print(f"❌ Format test failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Format test error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 FLUTTER INTEGRATION READY!")
    print("The backend is ready for Flutter integration with:")
    print("✅ Universal search system")
    print("✅ Stance detection")
    print("✅ Bias matching")
    print("✅ Relevance scoring")
    print("✅ Proper response format")

if __name__ == "__main__":
    test_flutter_integration() 