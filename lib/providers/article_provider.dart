import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/article.dart';
import '../services/api_service.dart';

// Universal Search Provider for ANY topic
class ArticleProvider extends StateNotifier<AsyncValue<List<Article>>> {
  final ApiService _apiService;

  ArticleProvider(this._apiService) : super(const AsyncValue.loading());

  // Search articles using the universal search system
  Future<void> searchArticles(String query, double bias) async {
    try {
      print('🔍 ARTICLE PROVIDER: ==========================================');
      print('🔍 ARTICLE PROVIDER: Starting universal search');
      print('🔍 ARTICLE PROVIDER: Query: "$query"');
      print('🔍 ARTICLE PROVIDER: Bias: $bias (${_getBiasLabel(bias)})');
      print('🔍 ARTICLE PROVIDER: ==========================================');

      state = const AsyncValue.loading();

      final articles = await _apiService.searchArticles(query, bias);

      print('🔍 ARTICLE PROVIDER: ==========================================');
      print('🔍 ARTICLE PROVIDER: SEARCH RESULTS:');
      print('🔍 ARTICLE PROVIDER: Total articles returned: ${articles.length}');
      
      // Log each article with detailed analysis
      for (int i = 0; i < articles.length; i++) {
        final article = articles[i];
        final biasAnalysis = article.biasAnalysis;
        
        print('🔍 ARTICLE PROVIDER: Article ${i + 1}:');
        print('  - Title: ${article.title}');
        print('  - Source: ${article.sourceName}');
        print('  - Published: ${article.publishedAt}');
        print('  - URL: ${article.url}');
        
        if (biasAnalysis != null) {
          print('  - Stance: ${biasAnalysis.stance} (confidence: ${biasAnalysis.stanceConfidence})');
          print('  - Stance Method: ${biasAnalysis.stanceMethod}');
          print('  - Bias Match: ${biasAnalysis.biasMatch}');
          print('  - Relevance Score: ${biasAnalysis.relevanceScore}');
          print('  - Final Score: ${biasAnalysis.finalScore}');
          print('  - User Belief: ${biasAnalysis.userBelief}');
          print('  - Analysis Method: ${biasAnalysis.analysisMethod}');
          
          if (biasAnalysis.stanceEvidence.isNotEmpty) {
            print('  - Stance Evidence: ${biasAnalysis.stanceEvidence.take(3).join(', ')}');
          }
        } else {
          print('  - No bias analysis available');
        }
        print('');
      }

      // Calculate and log summary statistics
      _logSearchSummary(articles, query, bias);

      state = AsyncValue.data(articles);
      
    } catch (e, stackTrace) {
      print('🔍 ARTICLE PROVIDER: Error searching articles: $e');
      print('🔍 ARTICLE PROVIDER: Stack trace: $stackTrace');
      state = AsyncValue.error(e, stackTrace);
    }
  }

  void _logSearchSummary(List<Article> articles, String query, double bias) {
    print('🔍 ARTICLE PROVIDER: ==========================================');
    print('🔍 ARTICLE PROVIDER: SUMMARY STATISTICS:');
    print('  - Query: "$query"');
    print('  - Bias Setting: $bias (${_getBiasLabel(bias)})');
    print('  - Total articles: ${articles.length}');
    print('  - Articles with bias analysis: ${articles.where((a) => a.biasAnalysis != null).length}');
    
    // Calculate average bias match
    final articlesWithBias = articles.where((a) => a.biasAnalysis != null).toList();
    if (articlesWithBias.isNotEmpty) {
      final avgBiasMatch = articlesWithBias
          .map((a) => a.biasAnalysis!.biasMatch)
          .reduce((a, b) => a + b) / articlesWithBias.length;
      print('  - Average bias match: ${avgBiasMatch.toStringAsFixed(3)}');
      
      // Calculate average relevance score
      final avgRelevance = articlesWithBias
          .where((a) => a.biasAnalysis!.relevanceScore != null)
          .map((a) => a.biasAnalysis!.relevanceScore!)
          .reduce((a, b) => a + b) / articlesWithBias.where((a) => a.biasAnalysis!.relevanceScore != null).length;
      print('  - Average relevance score: ${avgRelevance.toStringAsFixed(3)}');
      
      // Calculate average final score
      final avgFinalScore = articlesWithBias
          .where((a) => a.biasAnalysis!.finalScore != null)
          .map((a) => a.biasAnalysis!.finalScore!)
          .reduce((a, b) => a + b) / articlesWithBias.where((a) => a.biasAnalysis!.finalScore != null).length;
      print('  - Average final score: ${avgFinalScore.toStringAsFixed(3)}');
      
      // Stance distribution
      final stanceCounts = <String, int>{};
      for (final article in articlesWithBias) {
        final stance = article.biasAnalysis!.stance;
        stanceCounts[stance] = (stanceCounts[stance] ?? 0) + 1;
      }
      print('  - Stance distribution: $stanceCounts');
      
      // Top sources
      final sourceCounts = <String, int>{};
      for (final article in articles) {
        final source = article.sourceName;
        sourceCounts[source] = (sourceCounts[source] ?? 0) + 1;
      }
      final topSources = sourceCounts.entries.toList()
        ..sort((a, b) => b.value.compareTo(a.value));
      print('  - Top 5 sources: ${topSources.take(5).map((e) => '${e.key}(${e.value})').join(', ')}');
      
      // Date range
      if (articles.isNotEmpty) {
        final dates = articles.map((a) => a.publishedAt).toList()..sort();
        print('  - Date range: ${dates.first} to ${dates.last}');
      }
    }
    print('🔍 ARTICLE PROVIDER: ==========================================');
  }

  String _getBiasLabel(double bias) {
    if (bias >= 0.8) return 'Prove me right (strong)';
    if (bias >= 0.6) return 'Prove me right (moderate)';
    if (bias >= 0.4) return 'Balanced';
    if (bias >= 0.2) return 'Prove me wrong (moderate)';
    return 'Prove me wrong (strong)';
  }

  // Get articles by category (legacy method)
  Future<void> getArticlesByCategory(List<String> categories, double bias) async {
    try {
      state = const AsyncValue.loading();
      final articles = await _apiService.getArticlesByCategory(
        categories: categories,
        bias: bias,
        limitPerCategory: 10,
      );
      state = AsyncValue.data(articles);
    } catch (e, stackTrace) {
      state = AsyncValue.error(e, stackTrace);
    }
  }

  // Clear articles
  void clearArticles() {
    state = const AsyncValue.data([]);
  }

  // Get current articles
  List<Article> get articles {
    return state.when(
      data: (articles) => articles,
      loading: () => [],
      error: (_, __) => [],
    );
  }

  // Check if loading
  bool get isLoading {
    return state.isLoading;
  }

  // Check if has error
  bool get hasError {
    return state.hasError;
  }

  // Get error
  Object? get error {
    return state.error;
  }
}

// Category Aggregation State
class ArticleAggregationState {
  final List<Article> articles;
  final bool isLoading;
  final String? error;
  final int totalArticles;
  final List<String> categoriesCovered;
  final double currentBias;

  ArticleAggregationState({
    this.articles = const [],
    this.isLoading = false,
    this.error,
    this.totalArticles = 0,
    this.categoriesCovered = const [],
    this.currentBias = 0.5,
  });

  ArticleAggregationState copyWith({
    List<Article>? articles,
    bool? isLoading,
    String? error,
    int? totalArticles,
    List<String>? categoriesCovered,
    double? currentBias,
  }) {
    return ArticleAggregationState(
      articles: articles ?? this.articles,
      isLoading: isLoading ?? this.isLoading,
      error: error,
      totalArticles: totalArticles ?? this.totalArticles,
      categoriesCovered: categoriesCovered ?? this.categoriesCovered,
      currentBias: currentBias ?? this.currentBias,
    );
  }
}

// Category Aggregation Provider
class ArticleAggregationNotifier extends StateNotifier<ArticleAggregationState> {
  final ApiService _apiService;

  ArticleAggregationNotifier(this._apiService) : super(ArticleAggregationState());

  Future<void> aggregateArticlesByCategoryPublic({
    required List<String> categories,
    required double bias,
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

// Provider exports
final articleProvider = StateNotifierProvider<ArticleProvider, AsyncValue<List<Article>>>(
  (ref) => ArticleProvider(ApiService()),
);

final articleAggregationProvider = StateNotifierProvider<ArticleAggregationNotifier, ArticleAggregationState>(
  (ref) => ArticleAggregationNotifier(ApiService()),
); 