#!/usr/bin/env python3
"""
Test script for User Belief Fingerprinting Service

Tests belief fingerprint creation, content scoring, personalized recommendations,
and belief analysis with realistic user scenarios.
"""

import sys
import os
import asyncio
import logging
from datetime import datetime

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.user_belief_fingerprint import user_belief_fingerprint_service

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Sample user beliefs for testing
SAMPLE_USERS = {
    "progressive_user": [
        {
            "text": "Universal healthcare would improve health outcomes",
            "category": "healthcare",
            "strength": 0.9,
            "source": "user_input"
        },
        {
            "text": "Climate change is primarily caused by human activities",
            "category": "climate",
            "strength": 0.8,
            "source": "user_input"
        },
        {
            "text": "Government should play a larger role in the economy",
            "category": "politics",
            "strength": 0.7,
            "source": "user_input"
        },
        {
            "text": "Social programs are necessary for a just society",
            "category": "social_issues",
            "strength": 0.8,
            "source": "user_input"
        }
    ],
    
    "conservative_user": [
        {
            "text": "Free markets are the best way to organize society",
            "category": "politics",
            "strength": 0.9,
            "source": "user_input"
        },
        {
            "text": "Individual rights are more important than collective welfare",
            "category": "social_issues",
            "strength": 0.8,
            "source": "user_input"
        },
        {
            "text": "Private healthcare is more efficient than government-run systems",
            "category": "healthcare",
            "strength": 0.7,
            "source": "user_input"
        },
        {
            "text": "Economic growth is more important than environmental protection",
            "category": "climate",
            "strength": 0.6,
            "source": "user_input"
        }
    ],
    
    "moderate_user": [
        {
            "text": "Democracy is the best form of government",
            "category": "politics",
            "strength": 0.6,
            "source": "user_input"
        },
        {
            "text": "Healthcare should be a right, not a privilege",
            "category": "healthcare",
            "strength": 0.5,
            "source": "user_input"
        },
        {
            "text": "Renewable energy should replace fossil fuels",
            "category": "climate",
            "strength": 0.7,
            "source": "user_input"
        }
    ]
}

# Sample content for testing
SAMPLE_CONTENT = [
    {
        "id": "article_1",
        "type": "article",
        "text": "A new study shows that countries with universal healthcare systems have better health outcomes and lower costs compared to the US system. The research, published in the Journal of Health Economics, analyzed data from 32 countries over 15 years.",
        "title": "Study: Universal Healthcare Improves Outcomes"
    },
    {
        "id": "article_2",
        "type": "article",
        "text": "Conservative think tank releases report arguing that private healthcare systems are more efficient and provide better quality care than government-run alternatives. The study cites examples from several European countries.",
        "title": "Report: Private Healthcare More Efficient"
    },
    {
        "id": "article_3",
        "type": "article",
        "text": "The Intergovernmental Panel on Climate Change has released its latest report, stating with high confidence that human activities are the primary driver of climate change. The report calls for immediate action to reduce greenhouse gas emissions.",
        "title": "IPCC: Human Activities Primary Cause of Climate Change"
    },
    {
        "id": "article_4",
        "type": "article",
        "text": "Some researchers argue that natural climate cycles play a larger role than human activities in current warming trends. The debate continues among climate scientists about the relative contributions of natural and anthropogenic factors.",
        "title": "Scientists Debate Natural vs Human Climate Factors"
    },
    {
        "id": "article_5",
        "type": "article",
        "text": "Recent economic analysis shows that free market policies have led to increased economic growth and job creation. The study examines data from countries that have implemented market-oriented reforms.",
        "title": "Analysis: Free Markets Drive Economic Growth"
    },
    {
        "id": "article_6",
        "type": "article",
        "text": "New research suggests that government intervention in markets can help address inequality and provide essential services. The study looks at successful examples of government programs in various countries.",
        "title": "Research: Government Intervention Can Reduce Inequality"
    }
]

async def test_belief_fingerprint_creation():
    """Test creating belief fingerprints for different user types"""
    print("\n🧪 Testing Belief Fingerprint Creation")
    print("=" * 60)
    
    for user_id, beliefs in SAMPLE_USERS.items():
        print(f"\nCreating fingerprint for {user_id}...")
        
        try:
            fingerprint = await user_belief_fingerprint_service.create_user_fingerprint(user_id, beliefs)
            
            print(f"  ✅ Successfully created fingerprint")
            print(f"  📊 Beliefs: {len(fingerprint.beliefs)}")
            print(f"  🏷️  Categories: {fingerprint.categories}")
            print(f"  📅 Last updated: {fingerprint.last_updated}")
            
        except Exception as e:
            print(f"  ❌ Failed to create fingerprint: {e}")

async def test_content_scoring():
    """Test scoring content for different users"""
    print("\n🧪 Testing Content Scoring")
    print("=" * 60)
    
    for user_id in SAMPLE_USERS.keys():
        print(f"\nScoring content for {user_id}:")
        
        for content in SAMPLE_CONTENT[:3]:  # Test first 3 articles
            try:
                score = await user_belief_fingerprint_service.score_content_for_user(
                    user_id, 
                    content['text'],
                    content
                )
                
                print(f"  📰 {content['title']}")
                print(f"    Proximity: {score.proximity_score:.3f}")
                print(f"    Stance Alignment: {score.stance_alignment:.3f}")
                print(f"    Overall Score: {score.overall_score:.3f}")
                print(f"    Evidence: {score.evidence[0] if score.evidence else 'None'}")
                
            except Exception as e:
                print(f"  ❌ Failed to score content: {e}")

async def test_personalized_recommendations():
    """Test personalized content recommendations"""
    print("\n🧪 Testing Personalized Recommendations")
    print("=" * 60)
    
    for user_id in SAMPLE_USERS.keys():
        print(f"\nRecommendations for {user_id}:")
        
        try:
            recommendations = await user_belief_fingerprint_service.get_personalized_recommendations(
                user_id, 
                SAMPLE_CONTENT,
                limit=3
            )
            
            for i, (content, score) in enumerate(recommendations, 1):
                print(f"  {i}. {content['title']}")
                print(f"     Score: {score.overall_score:.3f}")
                print(f"     Categories: {score.metadata.get('categories_covered', [])}")
                
        except Exception as e:
            print(f"  ❌ Failed to get recommendations: {e}")

async def test_belief_analysis():
    """Test belief analysis and insights"""
    print("\n🧪 Testing Belief Analysis")
    print("=" * 60)
    
    for user_id in SAMPLE_USERS.keys():
        print(f"\nAnalysis for {user_id}:")
        
        try:
            analysis = await user_belief_fingerprint_service.analyze_user_beliefs(user_id)
            
            print(f"  📊 Total beliefs: {analysis['total_beliefs']}")
            print(f"  🏷️  Categories: {analysis['categories']}")
            print(f"  📈 Belief diversity: {analysis['belief_diversity']:.3f}")
            print(f"  💪 Strongest category: {analysis['recommendations']['strongest_category']}")
            print(f"  🔍 Most diverse category: {analysis['recommendations']['most_diverse_category']}")
            print(f"  💡 Suggested categories: {analysis['recommendations']['suggested_categories']}")
            
        except Exception as e:
            print(f"  ❌ Failed to analyze beliefs: {e}")

async def test_belief_templates():
    """Test belief template functionality"""
    print("\n🧪 Testing Belief Templates")
    print("=" * 60)
    
    try:
        # Get all templates
        all_templates = await user_belief_fingerprint_service.get_belief_templates()
        print(f"Available categories: {list(all_templates.keys())}")
        
        # Get specific category templates
        politics_templates = await user_belief_fingerprint_service.get_belief_templates(['politics'])
        print(f"\nPolitics templates ({len(politics_templates['politics'])}):")
        for template in politics_templates['politics'][:2]:  # Show first 2
            print(f"  - {template}")
            
    except Exception as e:
        print(f"  ❌ Failed to get templates: {e}")

async def test_health_check():
    """Test service health check"""
    print("\n🧪 Testing Health Check")
    print("=" * 60)
    
    try:
        health = await user_belief_fingerprint_service.health_check()
        
        print(f"  🔧 Service: {health['service']}")
        print(f"  ✅ Status: {health['status']}")
        print(f"  🤖 Sentence Transformer: {health['sentence_transformer_available']}")
        print(f"  👥 Users Registered: {health['users_registered']}")
        print(f"  🏷️  Categories Supported: {len(health['categories_supported'])}")
        
    except Exception as e:
        print(f"  ❌ Health check failed: {e}")

async def run_all_tests():
    """Run all belief fingerprinting tests"""
    print("\n🧪 User Belief Fingerprinting Test Suite")
    print("=" * 80)
    print(f"Test started at: {datetime.now()}")
    
    # Run all tests
    await test_belief_fingerprint_creation()
    await test_content_scoring()
    await test_personalized_recommendations()
    await test_belief_analysis()
    await test_belief_templates()
    await test_health_check()
    
    print(f"\n✅ All tests completed at: {datetime.now()}")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(run_all_tests()) 