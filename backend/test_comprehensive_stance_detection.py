#!/usr/bin/env python3
"""
Comprehensive Stance Detection Test Suite

Tests the advanced stance detector with:
- Real-world news examples
- Edge cases and adversarial examples
- Different belief phrasings
- Cross-topic diversity
- Confidence analysis
"""

import sys
import os
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.advanced_stance_detector import advanced_stance_detector

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Comprehensive test cases organized by category
TEST_CASES = {
    "palestine_israel": [
        {
            "belief": "Israel is committing war crimes in Gaza",
            "articles": [
                "A UN report accuses Israel of using disproportionate force in Gaza, resulting in civilian casualties. Human rights groups have called for investigations into possible war crimes.",
                "The Israeli Defense Forces state that all operations in Gaza are in accordance with international law and are aimed at neutralizing terrorist threats from Hamas.",
                "Independent observers report that both sides have committed violations, but the scale and nature of Israeli actions raise serious concerns about compliance with international law.",
                "Israel maintains that its military actions are defensive and proportional, citing the need to protect its citizens from rocket attacks and terrorist infiltration."
            ]
        },
        {
            "belief": "Palestinian resistance is justified",
            "articles": [
                "Many international observers argue that Palestinian resistance is a response to decades of occupation and blockade. However, some Western governments label these actions as terrorism.",
                "The Israeli government condemns all forms of Palestinian resistance as acts of terrorism and maintains that its security measures are necessary for the protection of its citizens.",
                "Legal experts debate whether Palestinian resistance constitutes legitimate self-defense under international law or terrorism under domestic statutes.",
                "Some analysts suggest that the term 'resistance' is used to legitimize violence that should be condemned regardless of the underlying political context."
            ]
        }
    ],
    
    "us_politics": [
        {
            "belief": "MAGA is a positive movement for America",
            "articles": [
                "Supporters of the MAGA movement believe it has revitalized American industry and restored national pride. Critics, however, argue it has deepened political divisions.",
                "Numerous studies show that the MAGA movement has led to increased polarization and a rise in hate crimes across the country.",
                "The MAGA movement has brought attention to important issues like border security and economic nationalism, though its methods remain controversial.",
                "Political analysts note that the MAGA movement has fundamentally changed the Republican Party's platform and electoral strategy."
            ]
        },
        {
            "belief": "Trump won the 2020 election",
            "articles": [
                "Multiple independent audits and court rulings have confirmed that Joe Biden won the 2020 election. Claims of widespread fraud have been debunked by both Republican and Democratic officials.",
                "Some right-wing media outlets continue to promote the narrative that Trump was the rightful winner of the 2020 election, despite a lack of credible evidence.",
                "Election security experts have repeatedly stated that the 2020 election was one of the most secure in American history, with no evidence of widespread fraud.",
                "Polls show that a significant portion of Republican voters continue to believe the election was stolen, despite overwhelming evidence to the contrary."
            ]
        }
    ],
    
    "climate_change": [
        {
            "belief": "Climate change is primarily caused by human activities",
            "articles": [
                "The overwhelming majority of climate scientists agree that human activities, particularly the burning of fossil fuels, are the primary driver of climate change.",
                "Some researchers argue that natural climate cycles play a larger role than human activities in current warming trends.",
                "The Intergovernmental Panel on Climate Change has stated with high confidence that human influence has warmed the atmosphere, ocean, and land.",
                "While natural factors do influence climate, the rapid warming observed since the industrial revolution cannot be explained without considering human greenhouse gas emissions."
            ]
        },
        {
            "belief": "Renewable energy is more expensive than fossil fuels",
            "articles": [
                "Recent studies show that renewable energy costs have fallen dramatically, making wind and solar competitive with or cheaper than fossil fuels in many markets.",
                "Critics argue that renewable energy costs don't account for the full system costs of backup power and grid infrastructure needed for intermittent sources.",
                "The International Energy Agency reports that solar and wind are now the cheapest sources of new electricity generation in most countries.",
                "Some energy analysts maintain that fossil fuels remain more cost-effective when considering reliability and energy density factors."
            ]
        }
    ],
    
    "healthcare": [
        {
            "belief": "Universal healthcare would improve health outcomes",
            "articles": [
                "Studies comparing healthcare systems show that countries with universal coverage generally have better health outcomes and lower costs than the US system.",
                "Critics argue that universal healthcare would lead to longer wait times, reduced quality of care, and higher taxes without significant health benefits.",
                "The World Health Organization ranks countries with universal healthcare systems higher in overall health system performance than those without.",
                "Some economists suggest that universal healthcare could reduce overall healthcare spending while improving access and outcomes for the population."
            ]
        }
    ],
    
    "edge_cases": [
        {
            "belief": "The sky is blue",
            "articles": [
                "Meteorologists explain that the sky appears blue due to Rayleigh scattering, where shorter wavelengths of light are scattered more than longer ones.",
                "During sunset, the sky can appear red or orange due to the angle of sunlight passing through more atmosphere.",
                "The sky is not actually blue - it's an optical illusion created by how our eyes perceive scattered light.",
                "Scientists have measured the exact wavelengths of light that make the sky appear blue to human observers."
            ]
        },
        {
            "belief": "Water is wet",
            "articles": [
                "Linguists and philosophers debate whether 'wetness' is a property of water itself or a sensation experienced when water comes into contact with other materials.",
                "From a scientific perspective, water molecules are not 'wet' - wetness is a property that emerges when water interacts with surfaces.",
                "The question of whether water is wet depends on how one defines the term 'wet' and whether it applies to the substance itself or its interactions.",
                "Children often ask whether water is wet, leading to interesting discussions about the nature of physical properties and language."
            ]
        }
    ],
    
    "adversarial": [
        {
            "belief": "Democracy is the best form of government",
            "articles": [
                "While democracy has many virtues, some political scientists argue that it's not universally the best form of government for all societies and circumstances.",
                "Historical examples show that democracies can be unstable, inefficient, and vulnerable to populism and demagoguery.",
                "The success of democracy depends on having an educated citizenry, strong institutions, and a culture that values democratic norms.",
                "Some authoritarian regimes have achieved impressive economic growth and social stability, challenging the assumption that democracy is always superior."
            ]
        },
        {
            "belief": "Science is always objective and unbiased",
            "articles": [
                "Scientists are human beings who can be influenced by their own biases, funding sources, and cultural assumptions, potentially affecting research outcomes.",
                "The scientific method is designed to minimize bias, but the history of science shows that even well-intentioned researchers can make errors.",
                "Peer review and replication help identify and correct biases in scientific research, but the process is not perfect.",
                "While science strives for objectivity, the interpretation and application of scientific findings can be influenced by political and social factors."
            ]
        }
    ]
}

async def run_comprehensive_tests():
    """Run comprehensive stance detection tests"""
    print("\n🧪 Comprehensive Stance Detection Test Suite")
    print("=" * 80)
    print(f"Test started at: {datetime.now()}")
    
    results = []
    total_cases = sum(len(category) for category in TEST_CASES.values())
    print(f"Total test categories: {len(TEST_CASES)}")
    print(f"Total belief-article combinations: {total_cases}")
    
    for category_name, category_cases in TEST_CASES.items():
        print(f"\n📂 Category: {category_name.upper()}")
        print("-" * 60)
        
        for case in category_cases:
            belief = case["belief"]
            articles = case["articles"]
            
            print(f"\nBelief: {belief}")
            
            for i, article in enumerate(articles):
                print(f"  Article {i+1}: {article[:80]}{'...' if len(article) > 80 else ''}")
                
                result = await advanced_stance_detector.detect_stance(belief, article)
                results.append({
                    'category': category_name,
                    'belief': belief,
                    'article': article,
                    'result': result
                })
                
                print(f"    → {result.stance.upper()} (confidence: {result.confidence:.2f}) - {result.method}")
    
    # Analysis
    print("\n" + "=" * 80)
    print("📊 ANALYSIS RESULTS")
    print("=" * 80)
    
    # Method distribution
    methods = {}
    stances = {}
    confidence_by_method = {}
    confidence_by_category = {}
    
    for result_data in results:
        result = result_data['result']
        category = result_data['category']
        
        # Method distribution
        method = result.method
        methods[method] = methods.get(method, 0) + 1
        
        # Stance distribution
        stance = result.stance
        stances[stance] = stances.get(stance, 0) + 1
        
        # Confidence by method
        if method not in confidence_by_method:
            confidence_by_method[method] = []
        confidence_by_method[method].append(result.confidence)
        
        # Confidence by category
        if category not in confidence_by_category:
            confidence_by_category[category] = []
        confidence_by_category[category].append(result.confidence)
    
    print("\n🔧 Method Distribution:")
    for method, count in methods.items():
        percentage = (count / len(results)) * 100
        print(f"  {method}: {count} ({percentage:.1f}%)")
    
    print("\n🎯 Stance Distribution:")
    for stance, count in stances.items():
        percentage = (count / len(results)) * 100
        print(f"  {stance}: {count} ({percentage:.1f}%)")
    
    print("\n📈 Average Confidence by Method:")
    for method, confidences in confidence_by_method.items():
        avg_confidence = sum(confidences) / len(confidences)
        print(f"  {method}: {avg_confidence:.3f}")
    
    print("\n📊 Average Confidence by Category:")
    for category, confidences in confidence_by_category.items():
        avg_confidence = sum(confidences) / len(confidences)
        print(f"  {category}: {avg_confidence:.3f}")
    
    # Potential issues
    print("\n⚠️  Potential Issues:")
    low_confidence_count = sum(1 for r in results if r['result'].confidence < 0.5)
    if low_confidence_count > 0:
        print(f"  - {low_confidence_count} cases with low confidence (< 0.5)")
    
    neutral_count = sum(1 for r in results if r['result'].stance == 'neutral')
    if neutral_count > len(results) * 0.3:  # More than 30% neutral
        print(f"  - High neutral rate: {neutral_count}/{len(results)} ({neutral_count/len(results)*100:.1f}%)")
    
    print(f"\n✅ Test completed at: {datetime.now()}")
    print("=" * 80)
    
    return results

if __name__ == "__main__":
    asyncio.run(run_comprehensive_tests()) 