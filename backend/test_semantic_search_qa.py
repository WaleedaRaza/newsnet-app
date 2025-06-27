#!/usr/bin/env python3
"""
Test script for Semantic Search & Q&A Service

Tests article indexing, semantic search, question answering,
and various query types with realistic news content.
"""

import sys
import os
import asyncio
import logging
from datetime import datetime

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.semantic_search_qa import semantic_search_qa_service

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Sample articles for testing
SAMPLE_ARTICLES = [
    {
        "id": "article_1",
        "title": "Study: Universal Healthcare Improves Outcomes",
        "content": "A new study shows that countries with universal healthcare systems have better health outcomes and lower costs compared to the US system. The research, published in the Journal of Health Economics, analyzed data from 32 countries over 15 years. Countries with universal healthcare showed 20% lower mortality rates and 30% lower healthcare costs per capita.",
        "source": "Health News Daily",
        "category": "healthcare",
        "url": "https://example.com/article1",
        "published_at": "2024-01-15"
    },
    {
        "id": "article_2",
        "title": "Report: Private Healthcare More Efficient",
        "content": "Conservative think tank releases report arguing that private healthcare systems are more efficient and provide better quality care than government-run alternatives. The study cites examples from several European countries where privatization led to reduced wait times and improved patient satisfaction. Critics argue the study is biased and ignores accessibility issues.",
        "source": "Economic Review",
        "category": "healthcare",
        "url": "https://example.com/article2",
        "published_at": "2024-01-16"
    },
    {
        "id": "article_3",
        "title": "IPCC: Human Activities Primary Cause of Climate Change",
        "content": "The Intergovernmental Panel on Climate Change has released its latest report, stating with high confidence that human activities are the primary driver of climate change. The report calls for immediate action to reduce greenhouse gas emissions. Scientists warn that without significant changes, global temperatures could rise by 2-3 degrees Celsius by 2050.",
        "source": "Science Today",
        "category": "climate",
        "url": "https://example.com/article3",
        "published_at": "2024-01-17"
    },
    {
        "id": "article_4",
        "title": "Scientists Debate Natural vs Human Climate Factors",
        "content": "Some researchers argue that natural climate cycles play a larger role than human activities in current warming trends. The debate continues among climate scientists about the relative contributions of natural and anthropogenic factors. However, the majority of climate scientists maintain that human activities are the dominant factor in recent warming.",
        "source": "Climate Research Journal",
        "category": "climate",
        "url": "https://example.com/article4",
        "published_at": "2024-01-18"
    },
    {
        "id": "article_5",
        "title": "Analysis: Free Markets Drive Economic Growth",
        "content": "Recent economic analysis shows that free market policies have led to increased economic growth and job creation. The study examines data from countries that have implemented market-oriented reforms. Results indicate that deregulation and privatization correlate with higher GDP growth rates and lower unemployment.",
        "source": "Economic Policy Institute",
        "category": "economy",
        "url": "https://example.com/article5",
        "published_at": "2024-01-19"
    },
    {
        "id": "article_6",
        "title": "Research: Government Intervention Can Reduce Inequality",
        "content": "New research suggests that government intervention in markets can help address inequality and provide essential services. The study looks at successful examples of government programs in various countries. Findings show that targeted government spending on education and healthcare can significantly reduce income inequality.",
        "source": "Social Policy Review",
        "category": "economy",
        "url": "https://example.com/article6",
        "published_at": "2024-01-20"
    },
    {
        "id": "article_7",
        "title": "Tech Companies Invest in Renewable Energy",
        "content": "Major technology companies are investing billions in renewable energy projects. Google, Apple, and Microsoft have all announced plans to become carbon neutral by 2030. These investments are driving down the cost of renewable energy and creating new jobs in the clean energy sector.",
        "source": "Tech News",
        "category": "technology",
        "url": "https://example.com/article7",
        "published_at": "2024-01-21"
    },
    {
        "id": "article_8",
        "title": "AI Breakthrough in Medical Diagnosis",
        "content": "Artificial intelligence has achieved a breakthrough in medical diagnosis, with new algorithms showing 95% accuracy in detecting early-stage cancer. The technology analyzes medical images and patient data to identify patterns that human doctors might miss. This could revolutionize healthcare by enabling earlier treatment and better outcomes.",
        "source": "Medical Technology Weekly",
        "category": "technology",
        "url": "https://example.com/article8",
        "published_at": "2024-01-22"
    }
]

# Sample questions for testing
SAMPLE_QUESTIONS = [
    "What are the benefits of universal healthcare?",
    "How do private and public healthcare systems compare?",
    "What is causing climate change?",
    "Are free markets better for economic growth?",
    "How can we reduce income inequality?",
    "What are tech companies doing about climate change?",
    "How is AI being used in healthcare?",
    "What are the latest developments in renewable energy?"
]

async def test_article_indexing():
    """Test adding articles to the search index"""
    print("\n🧪 Testing Article Indexing")
    print("=" * 60)
    
    try:
        await semantic_search_qa_service.add_articles(SAMPLE_ARTICLES)
        print(f"  ✅ Successfully indexed {len(SAMPLE_ARTICLES)} articles")
        
        # Get statistics
        stats = await semantic_search_qa_service.get_search_statistics()
        print(f"  📊 Total articles: {stats['total_articles']}")
        print(f"  🤖 Embeddings available: {stats['embeddings_available']}")
        print(f"  📐 Embedding dimensions: {stats['embedding_dimensions']}")
        print(f"  📰 Sources: {stats['sources']}")
        print(f"  🏷️  Categories: {stats['categories']}")
        
    except Exception as e:
        print(f"  ❌ Failed to index articles: {e}")

async def test_semantic_search():
    """Test semantic search functionality"""
    print("\n🧪 Testing Semantic Search")
    print("=" * 60)
    
    test_queries = [
        "healthcare systems",
        "climate change causes",
        "economic growth",
        "technology innovation",
        "government policies"
    ]
    
    for query in test_queries:
        print(f"\nSearching for: '{query}'")
        
        try:
            results = await semantic_search_qa_service.semantic_search(query, max_results=3)
            
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result.title}")
                print(f"     Source: {result.source}")
                print(f"     Similarity: {result.similarity_score:.3f}")
                print(f"     Content: {result.content[:100]}...")
                
        except Exception as e:
            print(f"  ❌ Search failed: {e}")

async def test_question_answering():
    """Test question answering functionality"""
    print("\n🧪 Testing Question Answering")
    print("=" * 60)
    
    for question in SAMPLE_QUESTIONS[:4]:  # Test first 4 questions
        print(f"\nQ: {question}")
        
        try:
            answer_result = await semantic_search_qa_service.answer_question(question)
            
            print(f"  A: {answer_result.answer}")
            print(f"  Confidence: {answer_result.confidence:.3f}")
            print(f"  Sources used: {answer_result.metadata['sources_used']}")
            
            if answer_result.evidence:
                print(f"  Evidence:")
                for evidence in answer_result.evidence[:2]:  # Show first 2 pieces
                    print(f"    - {evidence[:80]}...")
                    
        except Exception as e:
            print(f"  ❌ Failed to answer question: {e}")

async def test_search_variations():
    """Test search with different parameters"""
    print("\n🧪 Testing Search Variations")
    print("=" * 60)
    
    query = "healthcare"
    
    # Test different max_results
    for max_results in [2, 5, 10]:
        print(f"\nSearching for '{query}' with max_results={max_results}")
        
        try:
            results = await semantic_search_qa_service.semantic_search(
                query, 
                max_results=max_results
            )
            print(f"  Found {len(results)} results")
            
        except Exception as e:
            print(f"  ❌ Search failed: {e}")
    
    # Test different similarity thresholds
    for threshold in [0.2, 0.5, 0.8]:
        print(f"\nSearching for '{query}' with threshold={threshold}")
        
        try:
            results = await semantic_search_qa_service.semantic_search(
                query, 
                similarity_threshold=threshold
            )
            print(f"  Found {len(results)} results")
            
        except Exception as e:
            print(f"  ❌ Search failed: {e}")

async def test_edge_cases():
    """Test edge cases and error handling"""
    print("\n🧪 Testing Edge Cases")
    print("=" * 60)
    
    # Test empty query
    print("\nTesting empty query:")
    try:
        results = await semantic_search_qa_service.semantic_search("")
        print(f"  Empty query returned {len(results)} results")
    except Exception as e:
        print(f"  ❌ Empty query failed: {e}")
    
    # Test very specific query
    print("\nTesting very specific query:")
    try:
        results = await semantic_search_qa_service.semantic_search(
            "What is the exact chemical composition of the atmosphere on Mars?"
        )
        print(f"  Specific query returned {len(results)} results")
    except Exception as e:
        print(f"  ❌ Specific query failed: {e}")
    
    # Test question with no relevant content
    print("\nTesting question with no relevant content:")
    try:
        answer = await semantic_search_qa_service.answer_question(
            "What is the population of Mars?"
        )
        print(f"  Answer: {answer.answer}")
        print(f"  Confidence: {answer.confidence}")
    except Exception as e:
        print(f"  ❌ No relevant content test failed: {e}")

async def test_health_check():
    """Test service health check"""
    print("\n🧪 Testing Health Check")
    print("=" * 60)
    
    try:
        health = await semantic_search_qa_service.health_check()
        
        print(f"  🔧 Service: {health['service']}")
        print(f"  ✅ Status: {health['status']}")
        print(f"  🤖 Sentence Transformer: {health['sentence_transformer_available']}")
        print(f"  📰 Articles Indexed: {health['articles_indexed']}")
        print(f"  🔢 Embeddings Generated: {health['embeddings_generated']}")
        
    except Exception as e:
        print(f"  ❌ Health check failed: {e}")

async def run_all_tests():
    """Run all semantic search and Q&A tests"""
    print("\n🧪 Semantic Search & Q&A Test Suite")
    print("=" * 80)
    print(f"Test started at: {datetime.now()}")
    
    # Run all tests
    await test_article_indexing()
    await test_semantic_search()
    await test_question_answering()
    await test_search_variations()
    await test_edge_cases()
    await test_health_check()
    
    print(f"\n✅ All tests completed at: {datetime.now()}")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(run_all_tests()) 