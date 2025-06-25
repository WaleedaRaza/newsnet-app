import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/article.dart';
import '../services/api_service.dart';

// State class for article aggregation
class ArticleAggregationState {
  final bool isLoading;
  final List<Article> articles;
  final String? error;
  final int totalArticles;
  final List<String> topicsCovered;
  final double aggregationTime;

  ArticleAggregationState({
    this.isLoading = false,
    this.articles = const [],
    this.error,
    this.totalArticles = 0,
    this.topicsCovered = const [],
    this.aggregationTime = 0.0,
  });

  ArticleAggregationState copyWith({
    bool? isLoading,
    List<Article>? articles,
    String? error,
    int? totalArticles,
    List<String>? topicsCovered,
    double? aggregationTime,
  }) {
    return ArticleAggregationState(
      isLoading: isLoading ?? this.isLoading,
      articles: articles ?? this.articles,
      error: error,
      totalArticles: totalArticles ?? this.totalArticles,
      topicsCovered: topicsCovered ?? this.topicsCovered,
      aggregationTime: aggregationTime ?? this.aggregationTime,
    );
  }
}

// Notifier for article aggregation
class ArticleAggregationNotifier extends StateNotifier<ArticleAggregationState> {
  final ApiService _apiService;

  ArticleAggregationNotifier(this._apiService) : super(ArticleAggregationState());

  Future<void> aggregateArticles({
    required List<String> topics,
    required Map<String, List<String>> beliefs,
    required double bias,
    int limitPerTopic = 10,
  }) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final response = await _apiService.aggregateArticles(
        topics: topics,
        beliefs: beliefs,
        bias: bias,
        limitPerTopic: limitPerTopic,
      );

      state = state.copyWith(
        isLoading: false,
        articles: response.articles,
        totalArticles: response.totalArticles,
        topicsCovered: response.topicsCovered,
        aggregationTime: response.aggregationTime,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  Future<void> getArticlesByTopic(String topic, {int limit = 20}) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final articles = await _apiService.getArticlesByTopic(topic, limit: limit);
      state = state.copyWith(
        isLoading: false,
        articles: articles,
        totalArticles: articles.length,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  void clearArticles() {
    state = ArticleAggregationState();
  }

  void clearError() {
    state = state.copyWith(error: null);
  }
}

// Provider
final articleAggregationProvider = StateNotifierProvider<ArticleAggregationNotifier, ArticleAggregationState>((ref) {
  final apiService = ref.watch(apiServiceProvider);
  return ArticleAggregationNotifier(apiService);
}); 