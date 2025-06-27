#!/usr/bin/env python3
"""
Test script for Intelligence API Endpoints

Tests all intelligence API endpoints using requests to verify
they work correctly with the FastAPI server.
"""

import requests
import json
import time
from typing import Dict, Any

# API base URL
BASE_URL = "http://localhost:8000"
INTELLIGENCE_BASE = f"{BASE_URL}/v1/intelligence"

def test_health_check():
    """Test the health check endpoint"""
    print("\n🧪 Testing Health Check")
    print("=" * 60)
    
    try:
        response = requests.get(f"{INTELLIGENCE_BASE}/health")
        if response.status_code == 200:
            health_data = response.json()
            print("  ✅ Health check successful")
            for service in health_data:
                print(f"    {service['service']}: {service['status']}")
        else:
            print(f"  ❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Health check error: {e}")

def test_stance_detection():
    """Test stance detection endpoints"""
    print("\n🧪 Testing Stance Detection")
    print("=" * 60)
    
    # Test single stance detection
    stance_request = {
        "belief": "Universal healthcare would improve health outcomes",
        "article_text": "A new study shows that countries with universal healthcare systems have better health outcomes and lower costs compared to the US system.",
        "method_preference": "auto"
    }
    
    try:
        response = requests.post(f"{INTELLIGENCE_BASE}/stance/detect", json=stance_request)
        if response.status_code == 200:
            result = response.json()
            print("  ✅ Single stance detection successful")
            print(f"    Stance: {result['stance']}")
            print(f"    Confidence: {result['confidence']:.3f}")
            print(f"    Method: {result['method']}")
        else:
            print(f"  ❌ Single stance detection failed: {response.status_code}")
            print(f"    Error: {response.text}")
    except Exception as e:
        print(f"  ❌ Single stance detection error: {e}")
    
    # Test batch stance detection
    batch_request = [
        {
            "belief": "Climate change is primarily caused by human activities",
            "article_text": "The IPCC has stated with high confidence that human activities are the primary driver of climate change."
        },
        {
            "belief": "Free markets are better for economic growth",
            "article_text": "Recent analysis shows that free market policies have led to increased economic growth and job creation."
        }
    ]
    
    try:
        response = requests.post(f"{INTELLIGENCE_BASE}/stance/batch", json=batch_request)
        if response.status_code == 200:
            results = response.json()
            print("  ✅ Batch stance detection successful")
            for i, result in enumerate(results):
                print(f"    {i+1}. {result['stance']} (confidence: {result['confidence']:.3f})")
        else:
            print(f"  ❌ Batch stance detection failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Batch stance detection error: {e}")
    
    # Test metrics
    try:
        response = requests.get(f"{INTELLIGENCE_BASE}/stance/metrics")
        if response.status_code == 200:
            metrics = response.json()
            print("  ✅ Stance metrics retrieved")
            print(f"    Total analyses: {metrics.get('total_analyses', 0)}")
        else:
            print(f"  ❌ Stance metrics failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Stance metrics error: {e}")

def test_belief_fingerprinting():
    """Test belief fingerprinting endpoints"""
    print("\n🧪 Testing Belief Fingerprinting")
    print("=" * 60)
    
    user_id = "test_user_123"
    
    # Test creating user fingerprint
    create_request = {
        "user_id": user_id,
        "beliefs": [
            {
                "text": "Universal healthcare would improve health outcomes",
                "category": "healthcare",
                "strength": 0.8,
                "source": "user_input"
            },
            {
                "text": "Climate change is primarily caused by human activities",
                "category": "climate",
                "strength": 0.7,
                "source": "user_input"
            }
        ]
    }
    
    try:
        response = requests.post(f"{INTELLIGENCE_BASE}/beliefs/create", json=create_request)
        if response.status_code == 200:
            result = response.json()
            print("  ✅ User fingerprint created")
            print(f"    Beliefs: {result['beliefs_count']}")
            print(f"    Categories: {result['categories']}")
        else:
            print(f"  ❌ Create fingerprint failed: {response.status_code}")
            print(f"    Error: {response.text}")
    except Exception as e:
        print(f"  ❌ Create fingerprint error: {e}")
    
    # Test content scoring
    scoring_request = {
        "user_id": user_id,
        "content_text": "A new study shows that countries with universal healthcare systems have better health outcomes and lower costs compared to the US system.",
        "content_metadata": {
            "id": "test_article_1",
            "type": "article",
            "title": "Study: Universal Healthcare Improves Outcomes"
        }
    }
    
    try:
        response = requests.post(f"{INTELLIGENCE_BASE}/beliefs/score", json=scoring_request)
        if response.status_code == 200:
            result = response.json()
            print("  ✅ Content scoring successful")
            print(f"    Overall score: {result['overall_score']:.3f}")
            print(f"    Proximity: {result['proximity_score']:.3f}")
            print(f"    Stance alignment: {result['stance_alignment']:.3f}")
        else:
            print(f"  ❌ Content scoring failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Content scoring error: {e}")
    
    # Test belief analysis
    try:
        response = requests.get(f"{INTELLIGENCE_BASE}/beliefs/analyze/{user_id}")
        if response.status_code == 200:
            result = response.json()
            print("  ✅ Belief analysis successful")
            print(f"    Total beliefs: {result['total_beliefs']}")
            print(f"    Belief diversity: {result['belief_diversity']:.3f}")
            print(f"    Strongest category: {result['recommendations']['strongest_category']}")
        else:
            print(f"  ❌ Belief analysis failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Belief analysis error: {e}")
    
    # Test belief templates
    try:
        response = requests.get(f"{INTELLIGENCE_BASE}/beliefs/templates?categories=politics,climate")
        if response.status_code == 200:
            templates = response.json()
            print("  ✅ Belief templates retrieved")
            for category, template_list in templates.items():
                print(f"    {category}: {len(template_list)} templates")
        else:
            print(f"  ❌ Belief templates failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Belief templates error: {e}")

def test_semantic_search_qa():
    """Test semantic search and Q&A endpoints"""
    print("\n🧪 Testing Semantic Search & Q&A")
    print("=" * 60)
    
    # First, index some test articles
    test_articles = [
        {
            "id": "test_article_1",
            "title": "Study: Universal Healthcare Improves Outcomes",
            "content": "A new study shows that countries with universal healthcare systems have better health outcomes and lower costs compared to the US system. The research analyzed data from 32 countries over 15 years.",
            "source": "Health News Daily",
            "category": "healthcare"
        },
        {
            "id": "test_article_2",
            "title": "IPCC: Human Activities Primary Cause of Climate Change",
            "content": "The Intergovernmental Panel on Climate Change has released its latest report, stating with high confidence that human activities are the primary driver of climate change.",
            "source": "Science Today",
            "category": "climate"
        }
    ]
    
    try:
        response = requests.post(f"{INTELLIGENCE_BASE}/search/index", json=test_articles)
        if response.status_code == 200:
            result = response.json()
            print("  ✅ Articles indexed successfully")
            print(f"    Articles added: {result['articles_added']}")
        else:
            print(f"  ❌ Article indexing failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Article indexing error: {e}")
    
    # Test semantic search
    search_request = {
        "query": "healthcare systems",
        "max_results": 3,
        "similarity_threshold": 0.3
    }
    
    try:
        response = requests.post(f"{INTELLIGENCE_BASE}/search/semantic", json=search_request)
        if response.status_code == 200:
            result = response.json()
            print("  ✅ Semantic search successful")
            print(f"    Results found: {result['total_results']}")
            for i, search_result in enumerate(result['results'][:2]):
                print(f"    {i+1}. {search_result['title']} (similarity: {search_result['similarity_score']:.3f})")
        else:
            print(f"  ❌ Semantic search failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Semantic search error: {e}")
    
    # Test question answering
    qa_request = {
        "question": "What are the benefits of universal healthcare?",
        "max_sources": 3,
        "min_confidence": 0.3
    }
    
    try:
        response = requests.post(f"{INTELLIGENCE_BASE}/qa/answer", json=qa_request)
        if response.status_code == 200:
            result = response.json()
            print("  ✅ Question answering successful")
            print(f"    Answer: {result['answer'][:100]}...")
            print(f"    Confidence: {result['confidence']:.3f}")
            print(f"    Sources used: {result['metadata']['sources_used']}")
        else:
            print(f"  ❌ Question answering failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Question answering error: {e}")
    
    # Test search statistics
    try:
        response = requests.get(f"{INTELLIGENCE_BASE}/search/statistics")
        if response.status_code == 200:
            stats = response.json()
            print("  ✅ Search statistics retrieved")
            print(f"    Total articles: {stats['total_articles']}")
            print(f"    Sources: {len(stats['sources'])}")
        else:
            print(f"  ❌ Search statistics failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Search statistics error: {e}")

def test_api_documentation():
    """Test that API documentation is accessible"""
    print("\n🧪 Testing API Documentation")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("  ✅ API documentation accessible")
        else:
            print(f"  ❌ API documentation failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ API documentation error: {e}")

def run_all_tests():
    """Run all API tests"""
    print("\n🧪 Intelligence API Test Suite")
    print("=" * 80)
    print(f"Testing API at: {BASE_URL}")
    print(f"Intelligence endpoints: {INTELLIGENCE_BASE}")
    
    # Wait a moment for server to be ready
    print("\n⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    # Run all tests
    test_health_check()
    test_stance_detection()
    test_belief_fingerprinting()
    test_semantic_search_qa()
    test_api_documentation()
    
    print(f"\n✅ All API tests completed!")
    print("=" * 80)
    print(f"📖 View API documentation at: {BASE_URL}/docs")
    print(f"🔍 Test intelligence endpoints at: {INTELLIGENCE_BASE}")

if __name__ == "__main__":
    run_all_tests() 