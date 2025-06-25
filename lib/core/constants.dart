class AppConstants {
  static const String appName = 'NewsNet';
  static const String appVersion = '1.0.0';
  
  // API Configuration
  static const String baseUrl = 'https://api.newsnet.app';
  static const String apiVersion = '/v1';
  
  // Storage Keys
  static const String userProfileKey = 'user_profile';
  static const String authTokenKey = 'auth_token';
  static const String biasSettingKey = 'bias_setting';
  
  // Default Values
  static const double defaultBiasSetting = 0.5;
  static const int maxSourcesPerStory = 10;
  static const int maxTimelineChunks = 50;
  
  // UI Constants
  static const double defaultPadding = 16.0;
  static const double borderRadius = 12.0;
  static const double sliderHeight = 48.0;
  
  // Animation Durations
  static const Duration shortAnimation = Duration(milliseconds: 200);
  static const Duration mediumAnimation = Duration(milliseconds: 300);
  static const Duration longAnimation = Duration(milliseconds: 500);
}

class TopicCategories {
  static const List<String> available = [
    'politics',
    'technology',
    'economy',
    'health',
    'environment',
    'international',
    'sports',
    'entertainment',
    'science',
    'education',
  ];
}

class BiasLabels {
  static const String challengeMe = 'Challenge Me';
  static const String question = 'Question';
  static const String neutral = 'Neutral';
  static const String support = 'Support';
  static const String proveMeRight = 'Prove Me Right';
  
  static String getLabel(double bias) {
    if (bias <= 0.25) return challengeMe;
    if (bias <= 0.5) return question;
    if (bias <= 0.75) return support;
    return proveMeRight;
  }
} 