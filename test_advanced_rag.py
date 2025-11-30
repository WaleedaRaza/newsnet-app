#!/usr/bin/env python3
"""
Test script for AdvancedRAGEngine (LangChain RAG Overhaul)
Run this script to test stance detection and see results in the terminal.
"""
import os
import sys
import argparse
import asyncio
from datetime import datetime

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv(dotenv_path="backend/.env")

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.services.advanced_rag_engine import AdvancedRAGEngine

async def main():
    parser = argparse.ArgumentParser(description="Test AdvancedRAGEngine (LangChain RAG Overhaul)")
    parser.add_argument('--query', type=str, default="climate change I support renewable energy", help="User query (topic + belief)")
    parser.add_argument('--bias', type=float, default=0.5, help="Bias slider (0.0 = challenge, 1.0 = affirm)")
    parser.add_argument('--limit', type=int, default=10, help="Number of articles to retrieve/analyze")
    args = parser.parse_args()

    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return

    print(f"\n🧠 ADVANCED RAG ENGINE TEST")
    print(f"Query: {args.query}")
    print(f"Bias slider: {args.bias}")
    print(f"Limit: {args.limit}")
    print("=" * 60)

    engine = AdvancedRAGEngine(openai_api_key)
    start_time = datetime.now()
    results = await engine.search_and_analyze(args.query, bias_slider=args.bias, limit=args.limit)
    end_time = datetime.now()

    print(f"\n⏱️  Completed in: {(end_time - start_time).total_seconds():.2f} seconds")
    print(f"\nProcessed Query: {results['processed_query']}")
    print(f"Total Articles: {results['summary']['total_articles']}")
    print(f"Stance Distribution: {results['summary']['stance_distribution']}")
    print(f"Average Confidence: {results['summary']['average_confidence']:.2f}")
    print(f"Average Uncertainty: {results['summary']['average_uncertainty']:.2f}")

    print("\nTop Articles:")
    for i, article in enumerate(results['articles'][:5], 1):
        print(f"\n{i}. {article['title']} [{article['source']}]")
        print(f"   URL: {article['url']}")
        print(f"   Stance: {article['stance']} (confidence: {article['confidence']:.2f}, bias_score: {article['bias_score']:.2f}, uncertainty: {article['uncertainty']:.2f})")
        print(f"   Debate Strength: {article.get('debate_strength', 0.0):.2f}")
        print(f"   Reasoning: {article['reasoning'][:200]}{'...' if len(article['reasoning']) > 200 else ''}")
        if article['evidence']:
            print(f"   Evidence: {article['evidence'][:2]}")
        if article.get('killer_evidence'):
            print(f"   Killer Evidence: {article['killer_evidence'][:2]}")

    print("\nDone.")

if __name__ == "__main__":
    asyncio.run(main()) 