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
    state = const AsyncValue.loading();
    
    try {
      final apiService = ApiService();
      final articles = await apiService.searchArticles(query, bias);
      
      print('🔍 ARTICLE PROVIDER: Got ${articles.length} articles');
      
      // Log bias analysis for debugging
      for (final article in articles.take(3)) {
        if (article.biasAnalysis != null) {
          print('🔍 ARTICLE PROVIDER: Article "${article.title.substring(0, min(50, article.title.length))}..."');
          print('  - Sentiment Score: ${article.biasAnalysis!.topicSentimentScore}');
          print('  - Sentiment: ${article.biasAnalysis!.topicSentiment}');
          print('  - Match: ${(article.biasAnalysis!.biasMatch * 100).toInt()}%');
          print('  - Confidence: ${article.biasAnalysis!.confidenceLabel}');
          print('  - Topic Mentions: ${article.biasAnalysis!.topicMentions}');
        }
      }
      
      state = AsyncValue.data(articles);
    } catch (e) {
      print('🔍 ARTICLE PROVIDER: Error searching articles: $e');
      state = AsyncValue.error(e, StackTrace.current);
    }
  }

  void clearSearch() {
    state = const AsyncValue.data(null);
  }
}

// Helper function for min
int min(int a, int b) => a < b ? a : b; 