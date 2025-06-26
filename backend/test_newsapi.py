#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from newsapi import NewsApiClient

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv('144a4a90f1c04f5dbfcd3bbc7b8d2434')
print(f"API Key: {api_key}")

if api_key:
    try:
        # Test NewsAPI connection
        client = NewsApiClient(api_key=api_key)
        print("Testing NewsAPI connection...")
        
        # Try to get top headlines
        response = client.get_top_headlines(country='us', page_size=5)
        print(f"Success! Found {len(response['articles'])} articles")
        
        # Try to search for articles
        search_response = client.get_everything(
            q='US Politics',
            language='en',
            sort_by='publishedAt',
            page_size=5
        )
        print(f"Search success! Found {len(search_response['articles'])} articles")
        
    except Exception as e:
        print(f"Error: {e}")
else:
    print("No API key found in environment variables") 