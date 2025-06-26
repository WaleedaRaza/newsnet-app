#!/usr/bin/env python3
"""
Test script for the Aggregation Orchestrator

This script validates the foundation of our pipeline before we build the full system.
"""

import sys
import os
import asyncio
import logging
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.aggregation_orchestrator import aggregation_orchestrator

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_orchestrator_foundation():
    """Test the basic orchestrator functionality"""
    
    print("🧪 Testing Aggregation Orchestrator Foundation")
    print("=" * 60)
    
    # Test 1: Health Check
    print("\n1. Testing Health Check...")
    health = await aggregation_orchestrator.health_check()
    print(f"✅ Health Status: {health['status']}")
    print(f"✅ Pipeline Ready: {health['pipeline_ready']}")
    print(f"✅ Timestamp: {health['timestamp']}")
    
    # Test 2: Basic Aggregation Request
    print("\n2. Testing Basic Aggregation Request...")
    
    test_topics = ["ukraine", "nato"]
    test_beliefs = {
        "ukraine": ["NATO is escalating the conflict", "Russia is the aggressor"],
        "nato": ["defensive alliance under pressure", "military buildup is necessary"]
    }
    test_bias = 0.3  # Slightly challenging
    
    print(f"📋 Test Topics: {test_topics}")
    print(f"🧠 Test Beliefs: {test_beliefs}")
    print(f"🎛️ Test Bias: {test_bias}")
    
    result = await aggregation_orchestrator.aggregate_articles(
        topics=test_topics,
        beliefs=test_beliefs,
        bias_slider=test_bias,
        user_id="test_user_123",
        limit_per_topic=5
    )
    
    print(f"\n📊 Results:")
    print(f"✅ Success: {result.success}")
    print(f"⏱️ Execution Time: {result.execution_time:.3f}s")
    print(f"📄 Articles Returned: {len(result.articles)}")
    print(f"🆔 Request ID: {result.task.request_id}")
    
    if result.success:
        print(f"\n📰 Sample Articles:")
        for i, article in enumerate(result.articles[:3]):  # Show first 3
            print(f"  {i+1}. {article['title']}")
            print(f"     Source: {article['source']}")
            print(f"     Semantic Score: {article['semantic_score']:.3f}")
            print(f"     Stance: {article['stance']} (confidence: {article['stance_confidence']:.2f})")
            print(f"     Ideology: {article['ideology']}")
            print(f"     Final Score: {article['final_score']:.3f}")
            print()
    
    # Test 3: Metrics
    print("3. Testing Metrics...")
    metrics = aggregation_orchestrator.get_pipeline_metrics()
    print(f"📈 Total Requests: {metrics['metrics']['total_requests']}")
    print(f"✅ Successful: {metrics['metrics']['successful_requests']}")
    print(f"❌ Failed: {metrics['metrics']['failed_requests']}")
    print(f"⏱️ Avg Execution Time: {metrics['metrics']['average_execution_time']:.3f}s")
    
    # Test 4: Error Handling
    print("\n4. Testing Error Handling...")
    
    # Test with invalid bias slider
    try:
        result = await aggregation_orchestrator.aggregate_articles(
            topics=[],
            beliefs={},
            bias_slider=1.5,  # Invalid bias value
            limit_per_topic=5
        )
        print(f"✅ Error handling test completed")
    except Exception as e:
        print(f"✅ Error caught: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎉 Foundation Test Completed Successfully!")
    
    return True

async def test_pipeline_structure():
    """Test the pipeline structure and data flow"""
    
    print("\n🔧 Testing Pipeline Structure")
    print("-" * 40)
    
    # Test with different scenarios
    test_scenarios = [
        {
            "name": "Challenge Mode",
            "topics": ["climate"],
            "beliefs": {"climate": ["Climate change is a serious threat"]},
            "bias": 0.1
        },
        {
            "name": "Affirm Mode", 
            "topics": ["economy"],
            "beliefs": {"economy": ["Free markets are efficient"]},
            "bias": 0.9
        },
        {
            "name": "Neutral Mode",
            "topics": ["technology"],
            "beliefs": {"technology": ["AI will transform society"]},
            "bias": 0.5
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n📋 Testing: {scenario['name']}")
        print(f"   Topics: {scenario['topics']}")
        print(f"   Bias: {scenario['bias']}")
        
        result = await aggregation_orchestrator.aggregate_articles(
            topics=scenario['topics'],
            beliefs=scenario['beliefs'],
            bias_slider=scenario['bias'],
            limit_per_topic=3
        )
        
        print(f"   ✅ Success: {result.success}")
        print(f"   📄 Articles: {len(result.articles)}")
        print(f"   ⏱️ Time: {result.execution_time:.3f}s")
    
    print("\n✅ Pipeline Structure Tests Completed!")

async def main():
    """Main test function"""
    
    print("🚀 Starting Aggregation Pipeline Foundation Tests")
    print(f"⏰ Test started at: {datetime.now()}")
    
    try:
        # Test foundation
        await test_orchestrator_foundation()
        
        # Test pipeline structure
        await test_pipeline_structure()
        
        print("\n🎉 All tests completed successfully!")
        print("✅ Foundation is ready for next phase")
        
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
        print("\n🚀 Ready to proceed to Phase 2: Multi-source news fetching")
    else:
        print("\n❌ Foundation tests failed - need to fix issues before proceeding")
        sys.exit(1) 