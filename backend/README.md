# NewsNet Backend v2.0

## 🚀 Multi-API News Aggregation Platform

NewsNet is an AI-powered news analysis platform that aggregates content from multiple APIs to provide comprehensive, bias-aware news coverage for debate users.

## 🏗️ Architecture

### Core Services
- **Multi-API Service**: Orchestrates 10+ news APIs for comprehensive coverage
- **Bias Scoring Service**: Advanced bias detection with 50+ source mappings
- **Article Aggregator**: Intelligent article filtering and ranking
- **Stance Detection**: AI-powered stance analysis
- **User Belief Fingerprinting**: Personalized content recommendations
- **Semantic Search & Q&A**: Advanced content search capabilities

### Supported APIs
1. **NewsAPI.org** - Mainstream news coverage
2. **GNews API** - Alternative mainstream coverage
3. **Mediastack API** - Real-time + historical data
4. **Webz.io** - 3.5M+ articles/day coverage
5. **Newscatcher API** - 20K+ outlets, sentiment analysis
6. **World News API** - 86+ languages, semantic tagging
7. **The Guardian API** - Deep left-leaning content
8. **NYT API** - Historical data, multimedia
9. **Aylien News API** - 90K+ sources, NLP tools
10. **Contify API** - 500K+ sources, ML-enhanced

## 🛠️ Setup

### 1. Environment Setup
```bash
# Copy environment template
cp env.example .env

# Edit .env with your API keys
# At minimum, set NEWS_API_KEY for basic functionality
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## 🔧 Configuration

### Required API Keys
- `NEWS_API_KEY`: NewsAPI.org (minimum for basic functionality)
- `GNEWS_API_KEY`: GNews API (recommended)
- `MEDIASTACK_API_KEY`: Mediastack API (recommended)

### Optional API Keys
- `WEBZ_API_KEY`: Webz.io API
- `NEWSCATCHER_API_KEY`: Newscatcher API
- `WORLDNEWS_API_KEY`: World News API
- `GUARDIAN_API_KEY`: The Guardian API
- `NYT_API_KEY`: NYT API
- `AYLIEN_API_KEY`: Aylien News API
- `CONTIFY_API_KEY`: Contify API

## 📊 Features

### Multi-API Aggregation
- Concurrent API requests for maximum coverage
- Intelligent fallback handling
- Automatic deduplication
- Rate limit management

### Advanced Bias Detection
- 7-tier bias classification (Far-Left to Far-Right)
- 50+ source bias mappings
- Content-based bias analysis
- Extremity scoring (0.2-1.0)

### Debate-Ready Content
- Extreme viewpoint filtering
- Controversial topic identification
- Multi-perspective article pairing
- Argumentative content scoring

## 🔌 API Endpoints

### Core Endpoints
- `GET /` - API information
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation

### Authentication
- `POST /v1/auth/register` - User registration
- `POST /v1/auth/login` - User login
- `POST /v1/auth/logout` - User logout
- `GET /v1/auth/me` - Current user info

### Articles
- `POST /v1/articles/aggregate` - Aggregate articles with bias filtering
- `POST /v1/articles/aggregate-public` - Public article aggregation
- `GET /v1/articles/search` - Search articles with bias analysis

### Intelligence
- `POST /v1/intelligence/stance/detect` - Stance detection
- `GET /v1/intelligence/health` - Intelligence services health
- `POST /v1/intelligence/beliefs/create` - Create user belief fingerprint
- `POST /v1/intelligence/search/semantic` - Semantic search

## 🧪 Testing

The application preserves all current functionality while adding multi-API capabilities. Test endpoints:

```bash
# Test basic functionality
curl http://localhost:8000/health

# Test stance detection
curl -X POST http://localhost:8000/v1/intelligence/stance/detect \
  -H "Content-Type: application/json" \
  -d '{"belief": "Climate change is real", "article_text": "Scientists agree that climate change is happening."}'

# Test article aggregation
curl -X POST http://localhost:8000/v1/articles/aggregate-public \
  -H "Content-Type: application/json" \
  -d '{"categories": ["politics"], "bias": 0.1, "limit_per_category": 5}'
```

## 🔄 Migration from v1.0

- All existing endpoints remain functional
- Enhanced with multi-API capabilities
- Improved bias detection and filtering
- Better error handling and fallbacks
- Backward compatible

## 🚧 Development

### Adding New APIs
1. Create new client class in `services/multi_api_service.py`
2. Add API key to `config.py`
3. Update `env.example`
4. Test integration

### Extending Bias Detection
1. Add sources to `services/bias_scoring_service.py`
2. Update bias mappings and extremity ratings
3. Test with content analysis

## 📈 Performance

- Concurrent API requests for faster response times
- Intelligent caching to reduce API calls
- Fallback systems for reliability
- Rate limit management across APIs

## 🔒 Security

- JWT-based authentication
- API key management
- Rate limiting
- Input validation
- Error handling

## 📝 License

This project is part of the NewsNet platform for AI-powered news analysis. 