#!/usr/bin/env python3
"""
Test script for the Advanced Stance Detector

Focus: Palestine/Israel and MAGA topics, with real and synthetic examples.
Logs stance, confidence, method, and evidence for each belief/article pair.
"""

import sys
import os
import asyncio
import logging
from datetime import datetime

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.advanced_stance_detector import advanced_stance_detector

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Test cases: (belief, article)
test_cases = [
    # Palestine/Israel
    ("Israel is committing war crimes in Gaza", "A UN report accuses Israel of using disproportionate force in Gaza, resulting in civilian casualties. Human rights groups have called for investigations into possible war crimes."),
    ("Israel is committing war crimes in Gaza", "The Israeli Defense Forces state that all operations in Gaza are in accordance with international law and are aimed at neutralizing terrorist threats from Hamas."),
    ("Palestinian resistance is justified", "Many international observers argue that Palestinian resistance is a response to decades of occupation and blockade. However, some Western governments label these actions as terrorism."),
    ("Palestinian resistance is justified", "The Israeli government condemns all forms of Palestinian resistance as acts of terrorism and maintains that its security measures are necessary for the protection of its citizens."),
    ("Hamas is a terrorist organization", "The United States and European Union have designated Hamas as a terrorist organization. Hamas, however, claims to be a legitimate resistance movement fighting for Palestinian rights."),
    ("Hamas is a terrorist organization", "Some analysts argue that labeling Hamas as a terrorist group oversimplifies the complex political situation in Gaza and ignores its role as a governing authority."),
    # MAGA
    ("MAGA is a positive movement for America", "Supporters of the MAGA movement believe it has revitalized American industry and restored national pride. Critics, however, argue it has deepened political divisions."),
    ("MAGA is a positive movement for America", "Numerous studies show that the MAGA movement has led to increased polarization and a rise in hate crimes across the country."),
    ("Trump won the 2020 election", "Multiple independent audits and court rulings have confirmed that Joe Biden won the 2020 election. Claims of widespread fraud have been debunked by both Republican and Democratic officials."),
    ("Trump won the 2020 election", "Some right-wing media outlets continue to promote the narrative that Trump was the rightful winner of the 2020 election, despite a lack of credible evidence."),
]

async def run_stance_tests():
    print("\n🧪 Advanced Stance Detection Test Harness")
    print("=" * 80)
    print(f"Test started at: {datetime.now()}")
    print(f"Total test cases: {len(test_cases)}\n")
    
    results = []
    for i, (belief, article) in enumerate(test_cases):
        print(f"\nCase {i+1}:")
        print(f"  Belief:   {belief}")
        print(f"  Article:  {article[:120]}{'...' if len(article) > 120 else ''}")
        
        result = await advanced_stance_detector.detect_stance(belief, article)
        results.append(result)
        
        print(f"  → Stance:      {result.stance.upper()} (confidence: {result.confidence:.2f})")
        print(f"  → Method:      {result.method}")
        print(f"  → Evidence:    {result.evidence}")
        if result.metadata:
            print(f"  → Metadata:    {result.metadata}")
    
    print("\n" + "=" * 80)
    print("Summary Table:")
    print(f"{'#':<3} {'Stance':<8} {'Conf.':<6} {'Method':<8} {'Belief':<40} {'Article (truncated)':<40}")
    print("-" * 80)
    for i, result in enumerate(results):
        print(f"{i+1:<3} {result.stance:<8} {result.confidence:<6.2f} {result.method:<8} {result.belief[:38]:<40} {result.article_text[:38]:<40}")
    print("\nTest completed at:", datetime.now())
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(run_stance_tests()) 