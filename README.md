# NewsNet - AI-Powered News Analysis App

(RETIRED)
STARTED OFF WITH SENTIMENT ANALYSIS, IT YIELDED MORE POSITIVE OR NEGATIVE RATHER THAN VIEW UNDERSTANDING, S O A PIVOT WAS MADE TO STANCE DETECTION, IN TANDEM WITH LANGCHAIN AND RAG, LATER INTEGRATED WITH GOOGLE SEARCH API, IT BECAME CLEAR AT THAT POINT THAT THIS WAS BASICALY A GOOGLE SEARCH WRAPPER WITH MORE COSTS AND LIKE 20 APIS LOL. Stance detection algorithm yielded promising results for earnings calls, s othis transitioned to stockscouter :) (i know this is pretty brainrot)



NewsNet is a comprehensive news analysis application that combines real-time news aggregation with AI-powered analysis and personalized content filtering. The app features a Flutter frontend and a FastAPI backend with advanced NLP capabilities.

---

## 🚀 Features

### Frontend (Flutter)
- **Modern UI:** Beautiful, responsive design with dark/light theme support
- **State Management:** Riverpod for efficient state management
- **Authentication:** Firebase Authentication integration
- **Article Aggregation:** Personalized news feed with bias-aware filtering
- **Story Management:** View and interact with news stories
- **User Profiles:** Customizable user preferences and belief fingerprints
- **Cross-Platform:** iOS, Android, Web, macOS, Linux, and Windows support

### Backend (FastAPI)
- **News API Integration:** Real-time news from multiple sources (NewsAPI, GNews, Guardian, and more)
- **NLP Analysis:** Sentiment analysis, bias detection, stance detection, and topic modeling
- **Article Aggregation:** Intelligent content filtering and scoring
- **User Management:** Authentication and profile management
- **Database:** SQLite for local development, PostgreSQL ready
- **Mock Endpoints:** Testing endpoints for development

---

## 🛠️ Tech Stack

### Frontend
- **Flutter:** Cross-platform UI framework
- **Riverpod:** State management
- **Dio:** HTTP client
- **Firebase Auth:** Authentication
- **url_launcher:** External link handling

### Backend
- **FastAPI:** Modern Python web framework
- **SQLAlchemy:** Database ORM
- **NewsAPI, GNews, Guardian:** News aggregation
- **LangChain:** AI/LLM integration
- **Transformers & SentenceTransformers:** NLP processing
- **Pydantic:** Data validation

---

## 📦 Installation

### Prerequisites
- Flutter SDK (3.0+)
- Python 3.8+
- Git

### Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Environment Configuration
```bash
cd backend
cp env.example .env
# Edit .env with your API keys
```
Required environment variables:
- `NEWS_API_KEY`: Your NewsAPI key ([get from NewsAPI](https://newsapi.org))
- `OPENAI_API_KEY`: Your OpenAI API key (optional)
- `DATABASE_URL`: Database connection string

### Firebase Configuration
1. Create a Firebase project at [Firebase Console](https://console.firebase.google.com/)
2. Add Android app and download `google-services.json`
3. Add iOS app and download `GoogleService-Info.plist`
4. Copy the files to their respective locations:
   ```bash
   cp google-services.json android/app/
   cp GoogleService-Info.plist ios/Runner/
   ```

#### Security Notes
> ⚠️ **Important:** Never commit API keys or sensitive configuration files to the repository. The `.gitignore` file is configured to exclude:
> - `backend/.env` (contains API keys)
> - `android/app/google-services.json` (Firebase config)
> - `ios/Runner/GoogleService-Info.plist` (Firebase config)
>
> Use the example files provided as templates:
> - `backend/env.example`
> - `android/app/google-services.example.json`
> - `ios/Runner/GoogleService-Info.example.plist`

### Frontend Setup
```bash
flutter pub get
flutter packages pub run build_runner build
```

---

## 🚀 Running the Application

### Backend
```bash
cd backend
python3 main.py
```
The backend will start on [http://127.0.0.1:8000](http://127.0.0.1:8000)

### Frontend
```bash
flutter run
```

---

## 📱 Usage
- Launch the app and sign up/login with Firebase
- Set your preferences in the profile tab
- Browse stories on the main feed
- Use "Show Me Articles" to get personalized news aggregation
- Adjust bias settings to control content filtering

---

## 🔧 Development

### Project Structure
```
NewsNet/
├── lib/                    # Flutter frontend
│   ├── models/            # Data models
│   ├── providers/         # Riverpod providers
│   ├── screens/           # UI screens
│   ├── services/          # API services
│   └── widgets/           # Reusable widgets
├── backend/               # FastAPI backend
│   ├── api/routes/        # API endpoints
│   ├── db/               # Database models
│   ├── services/         # Business logic
│   └── schemas/          # Pydantic schemas
└── assets/               # Static assets
```

### API Endpoints (Backend)
- `GET /v1/stories` - Get news stories
- `POST /v1/articles/aggregate` - Aggregate articles
- `GET /v1/articles/test-mock` - Mock articles for testing
- `GET /v1/stories/test-mock` - Mock stories for testing

### Testing
#### Backend tests
```bash
cd backend
python3 -m pytest
```
#### Frontend tests
```bash
flutter test
```

---

## 🤝 Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🆘 Support
- Create an issue on GitHub
- Check the documentation in the code
- Review the test files for usage examples

---

## 🔮 Roadmap
- Real-time notifications
- Advanced NLP features (stance detection, ideology classification, semantic search)
- Social sharing
- Offline support
- Multi-language support
- Advanced analytics
- Content recommendations
- User-generated content

---

## About
AI-powered news analysis app with Flutter frontend and FastAPI backend 
