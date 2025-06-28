# Free News API Keys Guide

To avoid rate limiting and ensure your app always has real news data, get these free API keys:

## 1. GNews API (100 requests/day free)
- Visit: https://gnews.io/
- Click "Get API Key"
- Sign up with email
- Copy your API key
- Add to `config.py`: `gnews_api_key = "your_key_here"`

## 2. Mediastack API (500 requests/month free)
- Visit: https://mediastack.com/
- Click "Get Free API Key"
- Sign up with email
- Copy your API key
- Add to `config.py`: `mediastack_api_key = "your_key_here"`

## 3. RSS Feeds (Unlimited, no key needed)
- Already implemented
- Uses BBC, CNN, Reuters, NPR feeds
- Works as final fallback

## How It Works:
1. **Primary**: NewsAPI (your existing key)
2. **Fallback 1**: GNews API (100/day free)
3. **Fallback 2**: Mediastack API (500/month free)
4. **Fallback 3**: RSS Feeds (unlimited)

## Total Free Requests:
- NewsAPI: 100/day
- GNews: 100/day
- Mediastack: 500/month
- RSS: Unlimited
- **Total**: 300+ requests/day for free!

## Benefits:
✅ **Always real news** - No mock data ever  
✅ **Multiple sources** - Diverse perspectives  
✅ **Rate limit protection** - Automatic fallback  
✅ **Credible results** - Real articles only  
✅ **Free tier friendly** - No paid plans needed  

Just add the API keys to your config and you're set! 🚀 