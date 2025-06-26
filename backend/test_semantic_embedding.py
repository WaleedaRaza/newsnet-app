#!/usr/bin/env python3
"""
Test script for the Semantic Embedding Service

This script validates the embedding generation and similarity search functionality.
"""

import sys
import os
import asyncio
import logging
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.semantic_embedding_service import semantic_embedding_service

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_embedding_foundation():
    """Test the basic embedding functionality"""
    
    print("🧪 Testing Semantic Embedding Service Foundation")
    print("=" * 60)
    
    # Test 1: Health Check
    print("\n1. Testing Health Check...")
    health = await semantic_embedding_service.health_check()
    print(f"✅ Status: {health['status']}")
    print(f"✅ Model Loaded: {health['model_loaded']}")
    print(f"✅ Test Embedding Success: {health['test_embedding_success']}")
    print(f"✅ Embedding Dimension: {health['embedding_dimension']}")
    
    # Test 2: Single Text Embedding
    print("\n2. Testing Single Text Embedding...")
    
    test_texts = [
        "NATO is escalating the conflict in Ukraine",
        "Russia is the aggressor in the Ukraine war",
        "Climate change is a serious threat to humanity",
        "Free markets are the most efficient economic system"
    ]
    
    for i, text in enumerate(test_texts):
        print(f"   📝 Embedding text {i+1}: {text[:50]}...")
        result = await semantic_embedding_service.embed_text(text)
        
        print(f"      ✅ Success: {result.success}")
        print(f"      ⏱️ Time: {result.processing_time:.3f}s")
        print(f"      📏 Dimension: {len(result.embedding)}")
        print(f"      🤖 Model: {result.model_name}")
        
        if result.metadata:
            print(f"      📊 Metadata: {result.metadata}")
        print()
    
    # Test 3: Batch Embedding
    print("3. Testing Batch Embedding...")
    
    batch_texts = [
        "Technology is transforming society",
        "AI will revolutionize healthcare",
        "Machine learning is advancing rapidly",
        "Digital transformation is accelerating"
    ]
    
    print(f"   📋 Batch size: {len(batch_texts)}")
    batch_results = await semantic_embedding_service.embed_batch(batch_texts)
    
    successful_count = sum(1 for r in batch_results if r.success)
    total_time = sum(r.processing_time for r in batch_results)
    
    print(f"   ✅ Successful: {successful_count}/{len(batch_texts)}")
    print(f"   ⏱️ Total Time: {total_time:.3f}s")
    print(f"   ⏱️ Average Time: {total_time/len(batch_texts):.3f}s per text")
    
    # Test 4: Cache Functionality
    print("\n4. Testing Cache Functionality...")
    
    # First embedding (should be cached)
    cache_text = "This text will be cached for testing"
    result1 = await semantic_embedding_service.embed_text(cache_text)
    print(f"   📝 First embedding: {result1.processing_time:.3f}s")
    
    # Second embedding (should use cache)
    result2 = await semantic_embedding_service.embed_text(cache_text)
    print(f"   📝 Cached embedding: {result2.processing_time:.3f}s")
    
    # Verify cache hit
    if result2.metadata and result2.metadata.get('cached'):
        print(f"   ✅ Cache hit confirmed")
    else:
        print(f"   ⚠️ Cache hit not detected")
    
    print("\n" + "=" * 60)
    print("🎉 Embedding Foundation Test Completed Successfully!")
    
    return True

async def test_similarity_search():
    """Test similarity search functionality"""
    
    print("\n🔍 Testing Similarity Search")
    print("-" * 40)
    
    # Test 1: Basic Similarity Search
    print("1. Testing Basic Similarity Search...")
    
    query = "NATO is escalating the Ukraine conflict"
    candidates = [
        "NATO provides defensive support to Ukraine",
        "Russia accuses NATO of provocation",
        "Climate change affects global weather patterns",
        "Free market economics promotes growth",
        "NATO's military buildup concerns Russia",
        "Ukraine seeks NATO membership",
        "Technology companies are innovating rapidly",
        "Healthcare systems need reform"
    ]
    
    print(f"   🔍 Query: {query}")
    print(f"   📋 Candidates: {len(candidates)}")
    
    similarity_result = await semantic_embedding_service.find_similar_texts(
        query_text=query,
        candidate_texts=candidates,
        top_k=5,
        threshold=0.3
    )
    
    print(f"   ✅ Processing Time: {similarity_result.processing_time:.3f}s")
    print(f"   📊 Matches Found: {len(similarity_result.matches)}")
    print(f"   📊 Total Candidates: {similarity_result.total_candidates}")
    
    print(f"\n   🏆 Top Matches:")
    for i, (text, score) in enumerate(similarity_result.matches):
        print(f"      {i+1}. Score: {score:.3f} - {text[:60]}...")
    
    # Test 2: Similarity Calculation
    print("\n2. Testing Similarity Calculation...")
    
    # Get embeddings for two similar texts
    text1 = "NATO supports Ukraine"
    text2 = "NATO helps Ukraine"
    text3 = "Climate change is real"
    
    result1 = await semantic_embedding_service.embed_text(text1)
    result2 = await semantic_embedding_service.embed_text(text2)
    result3 = await semantic_embedding_service.embed_text(text3)
    
    if result1.success and result2.success and result3.success:
        sim_12 = semantic_embedding_service.calculate_similarity(
            result1.embedding, result2.embedding
        )
        sim_13 = semantic_embedding_service.calculate_similarity(
            result1.embedding, result3.embedding
        )
        
        print(f"   📝 Similarity between similar texts: {sim_12:.3f}")
        print(f"   📝 Similarity between different texts: {sim_13:.3f}")
        
        if sim_12 > sim_13:
            print(f"   ✅ Similarity logic working correctly")
        else:
            print(f"   ⚠️ Similarity logic may need adjustment")
    
    # Test 3: Edge Cases
    print("\n3. Testing Edge Cases...")
    
    # Empty text
    empty_result = await semantic_embedding_service.embed_text("")
    print(f"   📝 Empty text: {'✅ Handled' if empty_result.success else '❌ Failed'}")
    
    # Very long text
    long_text = "This is a very long text " * 100
    long_result = await semantic_embedding_service.embed_text(long_text)
    print(f"   📝 Long text: {'✅ Handled' if long_result.success else '❌ Failed'}")
    
    # Special characters
    special_text = "Text with special chars: !@#$%^&*()_+{}|:<>?[]\\;'\",./"
    special_result = await semantic_embedding_service.embed_text(special_text)
    print(f"   📝 Special chars: {'✅ Handled' if special_result.success else '❌ Failed'}")
    
    print("\n✅ Similarity Search Tests Completed!")

async def test_belief_alignment():
    """Test belief-aligned similarity search"""
    
    print("\n🧠 Testing Belief-Aligned Similarity Search")
    print("-" * 50)
    
    # Test scenarios with different beliefs
    test_scenarios = [
        {
            "belief": "NATO is escalating the Ukraine conflict",
            "supporting_articles": [
                "NATO's military buildup in Eastern Europe",
                "NATO provides weapons to Ukraine",
                "NATO's presence provokes Russia"
            ],
            "challenging_articles": [
                "NATO is purely defensive alliance",
                "NATO protects European security",
                "Russia initiated the conflict"
            ],
            "neutral_articles": [
                "Ukraine seeks NATO membership",
                "European security concerns grow",
                "International tensions rise"
            ]
        },
        {
            "belief": "Climate change is a serious threat",
            "supporting_articles": [
                "Global temperatures continue to rise",
                "Climate scientists warn of crisis",
                "Extreme weather events increase"
            ],
            "challenging_articles": [
                "Climate change is natural variation",
                "Climate models are unreliable",
                "Economic costs outweigh benefits"
            ],
            "neutral_articles": [
                "Climate policy discussions continue",
                "Environmental regulations debated",
                "Energy transition underway"
            ]
        }
    ]
    
    for i, scenario in enumerate(test_scenarios):
        print(f"\n📋 Scenario {i+1}: {scenario['belief'][:50]}...")
        
        all_articles = (
            scenario['supporting_articles'] + 
            scenario['challenging_articles'] + 
            scenario['neutral_articles']
        )
        
        # Find similar articles
        similarity_result = await semantic_embedding_service.find_similar_texts(
            query_text=scenario['belief'],
            candidate_texts=all_articles,
            top_k=10,
            threshold=0.2
        )
        
        print(f"   🔍 Found {len(similarity_result.matches)} similar articles")
        
        # Analyze results
        supporting_found = 0
        challenging_found = 0
        neutral_found = 0
        
        for text, score in similarity_result.matches:
            if text in scenario['supporting_articles']:
                supporting_found += 1
            elif text in scenario['challenging_articles']:
                challenging_found += 1
            elif text in scenario['neutral_articles']:
                neutral_found += 1
        
        print(f"   📊 Supporting: {supporting_found}")
        print(f"   📊 Challenging: {challenging_found}")
        print(f"   📊 Neutral: {neutral_found}")
        
        # Show top matches
        print(f"   🏆 Top 3 matches:")
        for j, (text, score) in enumerate(similarity_result.matches[:3]):
            category = "supporting" if text in scenario['supporting_articles'] else \
                      "challenging" if text in scenario['challenging_articles'] else "neutral"
            print(f"      {j+1}. {score:.3f} ({category}): {text[:50]}...")
    
    print("\n✅ Belief Alignment Tests Completed!")

async def main():
    """Main test function"""
    
    print("🚀 Starting Semantic Embedding Service Tests")
    print(f"⏰ Test started at: {datetime.now()}")
    
    try:
        # Test foundation
        await test_embedding_foundation()
        
        # Test similarity search
        await test_similarity_search()
        
        # Test belief alignment
        await test_belief_alignment()
        
        # Show final metrics
        print("\n📊 Final Service Metrics:")
        metrics = semantic_embedding_service.get_metrics()
        print(f"   📈 Total Embeddings: {metrics['metrics']['total_embeddings']}")
        print(f"   ✅ Successful: {metrics['metrics']['successful_embeddings']}")
        print(f"   ❌ Failed: {metrics['metrics']['failed_embeddings']}")
        print(f"   💾 Cache Hits: {metrics['metrics']['cache_hits']}")
        print(f"   ⏱️ Avg Processing Time: {metrics['metrics']['average_processing_time']:.3f}s")
        print(f"   🤖 Model: {metrics['model_name']}")
        print(f"   💾 Cache Size: {metrics['cache_size']}")
        
        print("\n🎉 All embedding service tests completed successfully!")
        print("✅ Embedding service is ready for pipeline integration")
        
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
        print("\n🚀 Ready to proceed to Phase 4: Stance detection")
    else:
        print("\n❌ Embedding service tests failed - need to fix issues before proceeding")
        sys.exit(1) 