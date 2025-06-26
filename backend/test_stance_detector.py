#!/usr/bin/env python3
"""
Test script for stance detection proof of concept
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.stance_detector import stance_detector

def test_stance_detection():
    """Test stance detection with sample articles and beliefs"""
    
    # Sample test cases
    test_cases = [
        {
            "belief": "NATO is escalating the Ukraine war",
            "articles": [
                {
                    "title": "NATO increases military support to Ukraine",
                    "description": "The alliance has approved additional weapons and training for Ukrainian forces, marking a significant escalation in Western involvement."
                },
                {
                    "title": "NATO denies escalation claims",
                    "description": "Alliance officials reject accusations that increased support constitutes escalation, calling it defensive assistance."
                },
                {
                    "title": "Ukraine reports successful counteroffensive",
                    "description": "Ukrainian forces have made significant gains against Russian positions, with NATO support playing a key role."
                }
            ]
        },
        {
            "belief": "Trump is a threat to democracy",
            "articles": [
                {
                    "title": "Trump's authoritarian rhetoric alarms experts",
                    "description": "Political scientists warn that Trump's recent statements about election integrity pose a serious threat to democratic institutions."
                },
                {
                    "title": "Trump defends election integrity efforts",
                    "description": "Former president argues that his actions were necessary to protect democracy and ensure fair elections."
                },
                {
                    "title": "Biden administration addresses democratic concerns",
                    "description": "White House officials outline new measures to strengthen democratic institutions and counter authoritarian threats."
                }
            ]
        }
    ]
    
    print("🧪 Testing Stance Detection Proof of Concept")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        belief = test_case["belief"]
        articles = test_case["articles"]
        
        print(f"\n📋 Test Case {i}: Belief = '{belief}'")
        print("-" * 40)
        
        # Test each article
        for j, article in enumerate(articles, 1):
            content = f"{article['title']} {article['description']}"
            
            print(f"\nArticle {j}: {article['title']}")
            
            # Classify stance
            stance_result = stance_detector.classify_stance(content, belief)
            
            # Display results
            stance_emoji = {
                "support": "✅",
                "oppose": "❌", 
                "neutral": "➖"
            }.get(stance_result["stance"], "❓")
            
            print(f"  {stance_emoji} Stance: {stance_result['stance'].upper()}")
            print(f"  📊 Confidence: {stance_result['confidence']:.2f}")
            print(f"  🔧 Method: {stance_result['method']}")
            
            if stance_result.get('evidence'):
                print(f"  🎯 Evidence: {', '.join(stance_result['evidence'][:3])}")
        
        print("\n" + "=" * 60)

def test_batch_classification():
    """Test batch classification functionality"""
    
    print("\n🔄 Testing Batch Classification")
    print("-" * 40)
    
    belief = "Climate change is a serious threat"
    articles = [
        {
            "title": "New study confirms climate change impacts",
            "description": "Research shows unprecedented warming trends and their effects on global ecosystems."
        },
        {
            "title": "Climate skeptics challenge mainstream science",
            "description": "Some researchers question the severity of climate change predictions."
        },
        {
            "title": "Weather patterns show normal variation",
            "description": "Meteorologists report that current weather patterns fall within historical ranges."
        }
    ]
    
    # Batch classify
    results = stance_detector.batch_classify_stances(articles, belief)
    
    for i, article in enumerate(results, 1):
        stance_analysis = article['stance_analysis']
        stance_emoji = {
            "support": "✅",
            "oppose": "❌",
            "neutral": "➖"
        }.get(stance_analysis["stance"], "❓")
        
        print(f"Article {i}: {stance_emoji} {stance_analysis['stance'].upper()} "
              f"(confidence: {stance_analysis['confidence']:.2f})")

if __name__ == "__main__":
    try:
        test_stance_detection()
        test_batch_classification()
        print("\n🎉 Stance detection proof of concept completed successfully!")
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc() 