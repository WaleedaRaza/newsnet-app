import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../models/article.dart';
import '../services/api_service.dart';

part 'article_provider.g.dart';

// State class for article aggregation
class ArticleAggregationState {
  final bool isLoading;
  final List<Article> articles;
  final String? error;
  final int totalArticles;
  final List<String> categoriesCovered;
  final double aggregationTime;
  final double currentBias;

  ArticleAggregationState({
    this.isLoading = false,
    this.articles = const [],
    this.error,
    this.totalArticles = 0,
    this.categoriesCovered = const [],
    this.aggregationTime = 0.0,
    this.currentBias = 0.5,
  });

  ArticleAggregationState copyWith({
    bool? isLoading,
    List<Article>? articles,
    String? error,
    int? totalArticles,
    List<String>? categoriesCovered,
    double? aggregationTime,
    double? currentBias,
  }) {
    return ArticleAggregationState(
      isLoading: isLoading ?? this.isLoading,
      articles: articles ?? this.articles,
      error: error,
      totalArticles: totalArticles ?? this.totalArticles,
      categoriesCovered: categoriesCovered ?? this.categoriesCovered,
      aggregationTime: aggregationTime ?? this.aggregationTime,
      currentBias: currentBias ?? this.currentBias,
    );
  }
}

// Notifier for article aggregation
class ArticleAggregationNotifier extends StateNotifier<ArticleAggregationState> {
  final ApiService _apiService;

  ArticleAggregationNotifier(this._apiService) : super(ArticleAggregationState());

  Future<void> aggregateArticlesByCategory({
    required List<String> categories,
    double bias = 0.5,
    int limitPerCategory = 10,
    String? authToken,
  }) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final articles = await _apiService.getArticlesByCategory(
        categories: categories,
        bias: bias,
        limitPerCategory: limitPerCategory,
        authToken: authToken,
      );

      state = state.copyWith(
        isLoading: false,
        articles: articles,
        totalArticles: articles.length,
        categoriesCovered: categories,
        currentBias: bias,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  Future<void> aggregateArticlesByCategoryPublic({
    required List<String> categories,
    double bias = 0.5,
    int limitPerCategory = 10,
  }) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final articles = await _apiService.getArticlesByCategoryPublic(
        categories: categories,
        bias: bias,
        limitPerCategory: limitPerCategory,
      );

      state = state.copyWith(
        isLoading: false,
        articles: articles,
        totalArticles: articles.length,
        categoriesCovered: categories,
        currentBias: bias,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  Future<void> getMockArticles() async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final articles = await _apiService.getMockArticles();
      state = state.copyWith(
        isLoading: false,
        articles: articles,
        totalArticles: articles.length,
        categoriesCovered: ['geopolitics', 'economics', 'tech_science'],
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  Future<void> testBackendConnection() async {
    try {
      final result = await _apiService.testBackendConnection();
      print('Backend test result: $result');
    } catch (e) {
      print('Backend test failed: $e');
    }
  }

  void clearArticles() {
    state = ArticleAggregationState();
  }

  void clearError() {
    state = state.copyWith(error: null);
  }

  void updateBias(double bias) {
    state = state.copyWith(currentBias: bias);
  }
}

// Provider
final articleAggregationProvider = StateNotifierProvider<ArticleAggregationNotifier, ArticleAggregationState>((ref) {
  return ArticleAggregationNotifier(ApiService());
});

@riverpod
class ArticleSearchNotifier extends _$ArticleSearchNotifier {
  @override
  Future<List<Article>?> build() async {
    // Initial state - no search performed yet
    return null;
  }

  Future<void> searchArticles(String query, double bias) async {
    print('🔍 ARTICLE PROVIDER: Searching for "$query" with bias $bias');
    print('🔍 ARTICLE PROVIDER: Raw query being sent to API: "$query"');
    state = const AsyncValue.loading();
    
    try {
      final apiService = ApiService();
      final articles = await apiService.searchArticles(query, bias);
      
      print('🔍 ARTICLE PROVIDER: Got ${articles.length} articles from API');
      print('🔍 ARTICLE PROVIDER: RAW API RESPONSE ANALYSIS:');
      print('🔍 ARTICLE PROVIDER: ==========================================');
      
      // Log bias analysis for ALL articles
      for (int i = 0; i < articles.length; i++) {
        final article = articles[i];
        print('🔍 ARTICLE PROVIDER: Article ${i + 1}: "${article.title}"');
        print('  - Source: ${article.source.name}');
        print('  - URL: ${article.url}');
        print('  - Description: ${article.description}');
        
        if (article.biasAnalysis != null) {
          print('  - Bias Analysis:');
          print('    - Stance: ${article.biasAnalysis!.stance}');
          print('    - Confidence: ${article.biasAnalysis!.stanceConfidence}');
          print('    - Method: ${article.biasAnalysis!.stanceMethod}');
          print('    - Evidence: ${article.biasAnalysis!.stanceEvidence}');
          print('    - User Belief: ${article.biasAnalysis!.userBelief}');
          print('    - Bias Match: ${article.biasAnalysis!.biasMatch}');
          print('    - User Bias Preference: ${article.biasAnalysis!.userBiasPreference}');
          print('    - Topic Sentiment Score: ${article.biasAnalysis!.topicSentimentScore}');
          print('    - Topic Sentiment: ${article.biasAnalysis!.topicSentiment}');
          print('    - Topic Mentions: ${article.biasAnalysis!.topicMentions}');
        } else {
          print('  - No bias analysis available');
        }
        
        // Relevance check
        final text = '${article.title} ${article.description}'.toLowerCase();
        print('  - Relevance Check:');
        print('    - Contains "Palestine": ${text.contains('palestine')}');
        print('    - Contains "Israel": ${text.contains('israel')}');
        print('    - Contains "occupation": ${text.contains('occupation')}');
        print('    - Contains query keywords: ${_containsQueryKeywords(text, query)}');
        print('  - Bias Match Score: ${(article.biasAnalysis?.biasMatch ?? 0.0) * 100}%');
        print('  - Stance: ${article.biasAnalysis?.stance ?? 'none'}');
        print('');
      }
      
      print('🔍 ARTICLE PROVIDER: ==========================================');
      print('🔍 ARTICLE PROVIDER: SUMMARY:');
      print('  - Total articles: ${articles.length}');
      print('  - Articles with bias analysis: ${articles.where((a) => a.biasAnalysis != null).length}');
      print('  - Average bias match: ${articles.where((a) => a.biasAnalysis != null).map((a) => a.biasAnalysis!.biasMatch).fold(0.0, (sum, match) => sum + match) / articles.where((a) => a.biasAnalysis != null).length}');
      print('  - Stance distribution:');
      final stanceCounts = <String, int>{};
      for (final article in articles) {
        if (article.biasAnalysis != null) {
          stanceCounts[article.biasAnalysis!.stance] = (stanceCounts[article.biasAnalysis!.stance] ?? 0) + 1;
        }
      }
      stanceCounts.forEach((stance, count) {
        print('    - $stance: $count articles');
      });
      
      state = AsyncValue.data(articles);
    } catch (e) {
      print('🔍 ARTICLE PROVIDER: Error searching articles: $e');
      state = AsyncValue.error(e, StackTrace.current);
    }
  }

  bool _containsQueryKeywords(String text, String query) {
    final keywords = query.toLowerCase().split(' ');
    return keywords.any((keyword) => text.contains(keyword));
  }

  void clearSearch() {
    state = const AsyncValue.data(null);
  }
}

// Helper function for min
int min(int a, int b) => a < b ? a : b; 