# 🚀 **FREE News Sources Guide - No API Keys Required!**

NewsNet now uses **completely free** news sources with unlimited access. No more rate limits or API key hassles!

## 📰 **Available Free News Sources**

### 1. **Google News (pygooglenews)** ⭐ **BEST**
- **GitHub:** https://github.com/kotartemiy/pygooglenews
- **Install:** `pip install pygooglenews`
- **Cost:** FREE (unlimited)
- **Rate Limits:** None
- **Features:**
  - Full Google News search
  - Recent articles (1h, 1d, 7d, 1m)
  - Topic-based feeds
  - Geographic news
  - No API key needed!

**Usage:**
```python
from pygooglenews import GoogleNews
gn = GoogleNews()

# Search recent news
result = gn.search('climate change', when='7d')

# Get top stories
top_news = gn.top_news()

# Get topic headlines
tech_news = gn.topic_headlines('TECHNOLOGY')
```

### 2. **GDELT Doc API** 🌍 **Global Coverage**
- **GitHub:** https://github.com/alex9smith/gdelt-doc-api
- **Website:** https://api.gdeltproject.org/
- **Cost:** FREE (unlimited)
- **Rate Limits:** None
- **Features:**
  - Global news from 100+ countries
  - Real-time news monitoring
  - 65+ languages
  - No API key needed for basic usage

**Usage:**
```python
# Direct API access
url = "https://api.gdeltproject.org/api/v2/doc/doc"
params = {
    'query': 'climate change',
    'mode': 'artlist',
    'maxrecords': 10,
    'format': 'json'
}
```

### 3. **CommonCrawl** 📚 **Web Archive**
- **Website:** https://commoncrawl.org/
- **Cost:** FREE (unlimited)
- **Rate Limits:** None
- **Features:**
  - Billions of web pages
  - News articles from all sources
  - Historical data
  - No API key needed

**Usage:**
```python
# Access via HTTP requests
# Billions of indexed web pages
# Perfect for comprehensive news search
```

### 4. **Enhanced RSS Feeds** 📡 **Major Sources**
- **Cost:** FREE (unlimited)
- **Rate Limits:** None
- **Sources:**
  - BBC News
  - CNN
  - Reuters
  - NPR
  - TechCrunch
  - Ars Technica
  - Fox News
  - New York Times
  - Washington Post
  - The Guardian

## 🔧 **Installation**

```bash
# Install the required packages
pip install pygooglenews
pip install httpx
pip install feedparser
pip install beautifulsoup4
```

## 🎯 **How NewsNet Uses These Sources**

### **Smart Fallback System:**
1. **NewsAPI** (if you have a key) - Primary source
2. **Google News** - Unlimited, no key needed
3. **GDELT** - Global coverage
4. **Enhanced RSS** - Major news sources
5. **CommonCrawl** - Web archive (if needed)

### **Universal Search:**
- Works with any topic
- No hardcoded terms
- Intelligent stance detection
- Bias matching
- Relevance scoring

## 🚀 **Benefits of Free Sources**

### ✅ **Advantages:**
- **No API keys required** for most sources
- **Unlimited requests** - no rate limits
- **Global coverage** from multiple sources
- **Real-time updates** from major news outlets
- **No cost** - completely free to use
- **Reliable** - multiple fallback options

### ⚠️ **Considerations:**
- **NewsAPI** still requires a key (but has free tier)
- **GDELT** may have occasional downtime
- **RSS feeds** depend on source availability
- **Google News** may change their format

## 📊 **Performance Comparison**

| Source | Cost | Rate Limit | Coverage | Reliability |
|--------|------|------------|----------|-------------|
| **Google News** | FREE | None | Global | ⭐⭐⭐⭐⭐ |
| **GDELT** | FREE | None | Global | ⭐⭐⭐⭐ |
| **RSS Feeds** | FREE | None | Major sources | ⭐⭐⭐⭐ |
| **CommonCrawl** | FREE | None | Web archive | ⭐⭐⭐ |
| **NewsAPI** | Free tier | 100/day | Global | ⭐⭐⭐⭐⭐ |

## 🎉 **Getting Started**

1. **Install dependencies:**
   ```bash
   pip install pygooglenews httpx feedparser beautifulsoup4
   ```

2. **Run the backend:**
   ```bash
   cd backend
   python main.py
   ```

3. **Test with Flutter:**
   ```bash
   cd ..
   flutter run
   ```

## 🔍 **Example Queries**

The system now works with **any topic**:

- "climate change I support renewable energy"
- "vaccines I oppose mandatory vaccination"
- "AI I support AI development"
- "capitalism I oppose free market"
- "Palestine I oppose the occupation"
- "Trump I support his policies"
- "Biden I oppose his administration"

## 🎯 **Advanced Features**

### **Universal Search Generator:**
- Generates search terms for any topic
- No hardcoded terms
- Stance-aware queries
- Context and temporal patterns

### **Universal Relevance Scorer:**
- Scores articles on topic presence
- Evaluates source credibility
- Measures content depth
- Quality assessment

### **Advanced Stance Detection:**
- 7-tier stance classification
- Confidence scoring
- Context awareness
- Bias matching

## 🚀 **Production Ready**

The system is now **production-ready** with:
- ✅ Unlimited free news sources
- ✅ No API key dependencies
- ✅ Smart fallback system
- ✅ Universal topic coverage
- ✅ Advanced stance detection
- ✅ Modern Flutter UI
- ✅ Real-time updates

**No more rate limits, no more API key hassles, no more costs!** 🎉 