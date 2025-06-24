# NewsNet - AI-Powered News Analysis App

NewsNet is a Flutter-based iOS news analysis app that uses AI to provide personalized news narratives based on user bias preferences. The app features real-time news from News API, Firebase authentication, and intelligent story analysis.

## Features

- 🔐 **Firebase Authentication** - Secure user registration and login
- 📰 **Real News Integration** - Live news from News API
- 🧠 **AI-Powered Analysis** - Personalized narratives based on bias settings
- 🎯 **Bias Control** - Adjust how stories are framed (Challenge Me to Prove Me Right)
- 💬 **Interactive Chat** - Ask questions about stories with AI responses
- 📱 **Modern UI** - Beautiful, responsive Flutter interface
- 🔄 **Real-time Updates** - Live news updates and trending topics
- 🏷️ **Category Filtering** - Filter news by categories and topics

## Tech Stack

- **Frontend**: Flutter with Riverpod for state management
- **Backend**: Firebase (Authentication, Firestore, Storage)
- **News API**: News API for real-time news data
- **AI**: Custom fusion engine for narrative analysis
- **Architecture**: Clean architecture with providers and services

## Setup Instructions

### 1. Prerequisites

- Flutter SDK (latest stable version)
- iOS Simulator or physical device
- Firebase project
- News API key

### 2. Firebase Setup

1. **Create a Firebase Project**:
   - Go to [Firebase Console](https://console.firebase.google.com/)
   - Create a new project
   - Enable Authentication (Email/Password)
   - Create a Firestore database
   - Enable Storage (optional)

2. **Configure iOS App**:
   - Add iOS app to your Firebase project
   - Download `GoogleService-Info.plist`
   - Place it in `ios/Runner/GoogleService-Info.plist`

3. **Update Firebase Configuration**:
   - Open `lib/firebase_options.dart`
   - Replace placeholder values with your actual Firebase configuration

### 3. News API Setup

1. **Get API Key**:
   - Sign up at [News API](https://newsapi.org/)
   - Get your API key from the dashboard

2. **Update API Key**:
   - Open `lib/services/news_service.dart`
   - Replace `YOUR_NEWS_API_KEY` with your actual API key

### 4. Install Dependencies

```bash
flutter pub get
```

### 5. Generate Code

```bash
dart run build_runner build
```

### 6. Run the App

```bash
flutter run
```

## Project Structure

```
lib/
├── core/
│   ├── constants.dart
│   ├── router.dart
│   ├── theme.dart
│   └── utils.dart
├── models/
│   ├── story.dart
│   ├── fusion_result.dart
│   └── user_profile.dart
├── providers/
│   ├── auth_provider.dart
│   └── story_provider.dart
├── services/
│   ├── firebase_service.dart
│   └── news_service.dart
├── views/
│   ├── auth_screen.dart
│   ├── home_screen.dart
│   ├── story_screen.dart
│   └── chat_screen.dart
├── widgets/
│   ├── story_card.dart
│   ├── category_chip.dart
│   ├── trending_topics.dart
│   └── search_bar.dart
├── firebase_options.dart
└── main.dart
```

## Key Features Explained

### Bias Settings

The app allows users to control how news narratives are presented:

- **Challenge Me (0.0)**: Presents counter-arguments and challenges user views
- **Question (0.25)**: Raises questions and explores different angles
- **Neutral (0.5)**: Balanced, factual presentation
- **Support (0.75)**: Provides supporting evidence for user views
- **Prove Me Right (1.0)**: Strongly supports and validates user perspectives

### AI Fusion Engine

The app uses an intelligent fusion engine that:

- Analyzes multiple news sources
- Identifies contradictions and biases
- Generates personalized narratives
- Provides confidence scores
- Extracts key entities and events

### Real-time Features

- Live news updates from News API
- Trending topics analysis
- User preference learning
- Chat history persistence
- Cross-device synchronization

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
NEWS_API_KEY=your_news_api_key_here
FIREBASE_PROJECT_ID=your_firebase_project_id
```

### Firebase Security Rules

Set up Firestore security rules:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    match /stories/{storyId} {
      allow read: if request.auth != null;
      allow write: if false; // Only allow admin writes
    }
    match /chat_messages/{messageId} {
      allow read, write: if request.auth != null;
    }
  }
}
```

## Development

### Adding New Features

1. **New Models**: Add to `lib/models/`
2. **New Services**: Add to `lib/services/`
3. **New Providers**: Add to `lib/providers/`
4. **New Views**: Add to `lib/views/`
5. **New Widgets**: Add to `lib/widgets/`

### Code Generation

The project uses code generation for:
- Riverpod providers (`@riverpod`)
- JSON serialization (`@JsonSerializable`)
- API clients (`@RestApi`)

Run code generation after changes:
```bash
dart run build_runner build --delete-conflicting-outputs
```

## Testing

```bash
# Run unit tests
flutter test

# Run widget tests
flutter test test/widget_test.dart

# Run integration tests
flutter test integration_test/
```

## Deployment

### iOS App Store

1. Update version in `pubspec.yaml`
2. Build release version:
   ```bash
   flutter build ios --release
   ```
3. Archive and upload via Xcode

### Firebase Hosting (Web)

```bash
flutter build web
firebase deploy
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the code examples

## Roadmap

- [ ] Advanced AI analysis with GPT integration
- [ ] Offline news caching
- [ ] Push notifications for breaking news
- [ ] Social sharing features
- [ ] Multi-language support
- [ ] Dark mode improvements
- [ ] Voice commands
- [ ] News summarization
- [ ] Fact-checking integration
- [ ] User-generated content moderation

---

**NewsNet** - Redefining how we consume and understand news through AI-powered narrative synthesis. 