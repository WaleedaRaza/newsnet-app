import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/story.dart';
import '../services/firebase_service.dart';

class NewsService {
  static const String _baseUrl = 'https://newsapi.org/v2';
  // Use a real NewsAPI key - you'll need to replace this with your actual key
  static const String _apiKey = 'd0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0'; // Replace with your actual API key
  
  // News categories - matching view management system
  static const List<String> categories = [
    'geopolitics',
    'economics',
    'social_issues',
    'tech_science',
    'health',
    'sports',
  ];

  // Map our categories to News API categories and search terms
  static Map<String, dynamic> _mapToNewsApiCategory(String category) {
    final categoryMap = {
      'geopolitics': {
        'category': 'general',
        'keywords': ['politics', 'government', 'election', 'diplomacy', 'foreign policy', 'international'],
        'searchTerms': ['politics', 'government', 'election', 'diplomacy']
      },
      'economics': {
        'category': 'business',
        'keywords': ['economy', 'market', 'stock', 'trade', 'business', 'finance', 'economic'],
        'searchTerms': ['economy', 'business', 'finance', 'market']
      },
      'social_issues': {
        'category': 'general',
        'keywords': ['social', 'society', 'community', 'rights', 'justice', 'equality'],
        'searchTerms': ['social issues', 'society', 'rights']
      },
      'tech_science': {
        'category': 'technology',
        'keywords': ['technology', 'science', 'ai', 'artificial intelligence', 'software', 'research'],
        'searchTerms': ['technology', 'science', 'AI']
      },
      'health': {
        'category': 'health',
        'keywords': ['health', 'medical', 'covid', 'vaccine', 'hospital', 'doctor'],
        'searchTerms': ['health', 'medical', 'covid']
      },
      'sports': {
        'category': 'sports',
        'keywords': ['sports', 'football', 'basketball', 'baseball', 'soccer', 'olympics'],
        'searchTerms': ['sports', 'football', 'basketball']
      },
    };
    return categoryMap[category] ?? categoryMap['geopolitics']!;
  }

  // Fetch top headlines by category
  static Future<List<Story>> getTopHeadlines({
    String? category,
    String? country = 'us',
    int pageSize = 20,
  }) async {
    try {
      print('🔍 NEWSAPI: Fetching headlines for category: $category');
      
      final queryParams = {
        'apiKey': _apiKey,
        'pageSize': pageSize.toString(),
        'country': country ?? 'us',
      };

      if (category != null) {
        final categoryInfo = _mapToNewsApiCategory(category);
        queryParams['category'] = categoryInfo['category'];
      }

      final uri = Uri.parse('$_baseUrl/top-headlines').replace(queryParameters: queryParams);
      print('🔍 NEWSAPI: Requesting URL: $uri');
      
      final response = await http.get(uri);

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final articles = data['articles'] as List;
        
        print('🔍 NEWSAPI: Got ${articles.length} articles from NewsAPI');
        
        final stories = articles.map((article) => _convertArticleToStory(article, category)).toList();
        print('🔍 NEWSAPI: Converted ${stories.length} articles to stories');
        
        return stories;
      } else {
        print('🔍 NEWSAPI: HTTP Error ${response.statusCode}: ${response.body}');
        throw Exception('Failed to fetch news: ${response.statusCode}');
      }
    } catch (e) {
      print('🔍 NEWSAPI: Error fetching headlines: $e');
      throw Exception('Failed to fetch news: $e');
    }
  }

  // Search news with category-specific terms
  static Future<List<Story>> searchNewsByCategory({
    required String category,
    String? language = 'en',
    String? sortBy = 'publishedAt',
    int pageSize = 20,
  }) async {
    try {
      print('🔍 NEWSAPI: Searching news for category: $category');
      
      final categoryInfo = _mapToNewsApiCategory(category);
      final searchTerms = categoryInfo['searchTerms'] as List<String>;
      
      // Use the first search term for now
      final query = searchTerms.first;
      
      final queryParams = {
        'apiKey': _apiKey,
        'q': query,
        'language': language ?? 'en',
        'sortBy': sortBy ?? 'publishedAt',
        'pageSize': pageSize.toString(),
      };

      final uri = Uri.parse('$_baseUrl/everything').replace(queryParameters: queryParams);
      print('🔍 NEWSAPI: Searching URL: $uri');
      
      final response = await http.get(uri);

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final articles = data['articles'] as List;
        
        print('🔍 NEWSAPI: Got ${articles.length} articles from search');
        
        final stories = articles.map((article) => _convertArticleToStory(article, category)).toList();
        print('🔍 NEWSAPI: Converted ${stories.length} articles to stories');
        
        return stories;
      } else {
        print('🔍 NEWSAPI: HTTP Error ${response.statusCode}: ${response.body}');
        throw Exception('Failed to search news: ${response.statusCode}');
      }
    } catch (e) {
      print('🔍 NEWSAPI: Error searching news: $e');
      throw Exception('Failed to search news: $e');
    }
  }

  // Convert News API article to Story model
  static Story _convertArticleToStory(Map<String, dynamic> article, String? category) {
    final title = article['title'] ?? '';
    final description = article['description'] ?? '';
    final content = article['content'] ?? '';
    final source = article['source']?['name'] ?? 'Unknown Source';
    final url = article['url'] ?? '';
    final publishedAt = article['publishedAt'] != null 
        ? DateTime.parse(article['publishedAt'])
        : DateTime.now();
    final urlToImage = article['urlToImage'];

    // Generate event key from title
    final eventKey = _generateEventKey(title);
    
    // Extract topics from title and description
    final topics = _extractTopics(title, description);
    
    // Create neutral summary
    final neutralSummary = _createNeutralSummary(title, description, content);
    
    // Create modulated summary (will be updated based on user bias)
    final modulatedSummary = neutralSummary;

    return Story(
      id: _generateStoryId(eventKey, source),
      eventKey: eventKey,
      title: title,
      summaryNeutral: neutralSummary,
      summaryModulated: modulatedSummary,
      sources: [source],
      timelineChunks: [
        TimelineChunk(
          id: 'chunk_1',
          timestamp: publishedAt,
          content: neutralSummary,
          sources: [source],
          confidence: 0.9,
          hasContradictions: false,
          contradictions: [],
        ),
      ],
      publishedAt: publishedAt,
      updatedAt: DateTime.now(),
      topics: topics,
      confidence: 0.9,
    );
  }

  // Generate event key from title
  static String _generateEventKey(String title) {
    final words = title.toLowerCase().split(' ');
    final keyWords = words.take(3).join('-');
    return keyWords.replaceAll(RegExp(r'[^a-z0-9-]'), '');
  }

  // Generate story ID
  static String _generateStoryId(String eventKey, String source) {
    final timestamp = DateTime.now().millisecondsSinceEpoch;
    return '${eventKey}_${source.toLowerCase().replaceAll(RegExp(r'[^a-z0-9]'), '')}_$timestamp';
  }

  // Extract topics from text
  static List<String> _extractTopics(String title, String description) {
    final text = '${title.toLowerCase()} ${description.toLowerCase()}';
    final topics = <String>[];

    // Define topic keywords
    final topicKeywords = {
      'politics': ['president', 'congress', 'senate', 'election', 'vote', 'government', 'policy'],
      'technology': ['tech', 'ai', 'artificial intelligence', 'software', 'app', 'digital', 'cyber'],
      'economy': ['economy', 'market', 'stock', 'trade', 'business', 'finance', 'economic'],
      'health': ['health', 'medical', 'covid', 'vaccine', 'hospital', 'doctor', 'disease'],
      'environment': ['climate', 'environment', 'global warming', 'pollution', 'green', 'sustainability'],
      'international': ['international', 'foreign', 'diplomacy', 'trade war', 'sanctions'],
      'sports': ['sports', 'football', 'basketball', 'baseball', 'soccer', 'olympics'],
      'entertainment': ['movie', 'film', 'celebrity', 'hollywood', 'music', 'entertainment'],
      'science': ['science', 'research', 'study', 'discovery', 'scientific', 'experiment'],
      'education': ['education', 'school', 'university', 'student', 'learning', 'academic'],
    };

    for (final entry in topicKeywords.entries) {
      if (entry.value.any((keyword) => text.contains(keyword))) {
        topics.add(entry.key);
      }
    }

    // Add general if no specific topics found
    if (topics.isEmpty) {
      topics.add('general');
    }

    return topics;
  }

  // Create neutral summary
  static String _createNeutralSummary(String title, String description, String content) {
    if (description.isNotEmpty) {
      return description;
    } else if (content.isNotEmpty) {
      // Take first 200 characters of content
      return content.length > 200 ? '${content.substring(0, 200)}...' : content;
    } else {
      return title;
    }
  }

  // Fetch and save stories to Firebase
  static Future<List<Story>> fetchAndSaveStories({
    String? category,
    int limit = 20,
  }) async {
    try {
      final stories = await getTopHeadlines(
        category: category,
        pageSize: limit,
      );

      // Save stories to Firebase
      for (final story in stories) {
        await FirebaseService.createStory(story);
      }

      return stories;
    } catch (e) {
      throw Exception('Failed to fetch and save stories: $e');
    }
  }

  // Get trending topics
  static Future<List<String>> getTrendingTopics() async {
    try {
      final stories = await getTopHeadlines(pageSize: 50);
      final topicCounts = <String, int>{};

      for (final story in stories) {
        for (final topic in story.topics) {
          topicCounts[topic] = (topicCounts[topic] ?? 0) + 1;
        }
      }

      final sortedTopics = topicCounts.entries.toList()
        ..sort((a, b) => b.value.compareTo(a.value));

      return sortedTopics.take(10).map((e) => e.key).toList();
    } catch (e) {
      throw Exception('Failed to get trending topics: $e');
    }
  }
}

// Providers
final newsServiceProvider = Provider<NewsService>((ref) => NewsService());

final trendingTopicsProvider = FutureProvider<List<String>>((ref) async {
  return await NewsService.getTrendingTopics();
});

final categoryStoriesProvider = FutureProvider.family<List<Story>, String>((ref, category) async {
  return await NewsService.getTopHeadlines(category: category);
});

final searchStoriesProvider = FutureProvider.family<List<Story>, String>((ref, query) async {
  if (query.trim().isEmpty) return [];
  return await NewsService.searchNewsByCategory(category: query);
}); 