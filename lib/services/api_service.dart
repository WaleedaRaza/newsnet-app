import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/user_profile.dart';
import '../models/story.dart';
import '../models/fusion_result.dart';
import '../models/article.dart';
import '../services/firebase_service.dart';

class ApiService {
  static const String _baseUrl = 'http://localhost:8000';  // Backend URL
  static const String _apiVersion = '/v1';
  
  // NewsNet categories
  static const List<String> categories = [
    'geopolitics',
    'economics', 
    'social_issues',
    'tech_science',
    'health',
    'sports',
  ];

  // Singleton pattern
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal();

  // Get current auth token
  Future<String?> _getAuthToken() async {
    try {
      final user = FirebaseService.getCurrentUser();
      if (user != null) {
        return await user.getIdToken();
      }
    } catch (e) {
      print('Error getting auth token: $e');
    }
    return null;
  }

  // Set auth token for requests
  void setAuthToken(String token) {
    // Store token for future requests
    _authToken = token;
  }

  // Clear auth token
  void clearAuthToken() {
    _authToken = null;
  }

  // Private field to store auth token
  String? _authToken;

  // Instance methods for the provider
  Future<List<Article>> getArticlesByCategory({
    required List<String> categories,
    double bias = 0.5,
    int limitPerCategory = 10,
    String? authToken,
  }) async {
    return ApiService.getArticlesByCategoryStatic(
      categories: categories,
      bias: bias,
      limitPerCategory: limitPerCategory,
      authToken: authToken,
    );
  }

  Future<List<Article>> getArticlesByCategoryPublic({
    required List<String> categories,
    double bias = 0.5,
    int limitPerCategory = 10,
  }) async {
    return ApiService.getArticlesByCategoryPublicStatic(
      categories: categories,
      bias: bias,
      limitPerCategory: limitPerCategory,
    );
  }

  Future<List<Article>> getMockArticles() async {
    return ApiService.getMockArticlesStatic();
  }

  Future<Map<String, dynamic>> testBackendConnection() async {
    return ApiService.testBackendConnectionStatic();
  }

  Future<List<Article>> searchArticles(String query, double bias) async {
    try {
      final uri = Uri.parse('$_baseUrl$_apiVersion/articles/search').replace(
        queryParameters: {
          'q': query,
          'bias': bias.toString(),
          'limit': '20',
        },
      );
      
      final response = await http.get(uri);

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        if (data['status'] == 'success' && data['articles'] != null) {
          return (data['articles'] as List)
              .map((articleJson) => Article.fromJson(articleJson))
              .toList();
        }
      }
      return [];
    } catch (e) {
      print('Error searching articles: $e');
      return [];
    }
  }

  // Auth endpoints
  Future<Map<String, dynamic>> register({
    required String email,
    required String password,
    String? name,
    List<String> interests = const [],
    Map<String, dynamic> beliefFingerprint = const {},
    double biasSetting = 0.5,
  }) async {
    try {
      final uri = Uri.parse('$_baseUrl$_apiVersion/auth/register');
      final response = await http.post(
        uri,
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'email': email,
          'password': password,
          'name': name,
          'interests': interests,
          'belief_fingerprint': beliefFingerprint,
          'bias_setting': biasSetting,
        }),
      );
      
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Registration failed: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Registration failed: $e');
    }
  }

  Future<Map<String, dynamic>> login({
    required String email,
    required String password,
  }) async {
    try {
      final uri = Uri.parse('$_baseUrl$_apiVersion/auth/login');
      final response = await http.post(
        uri,
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'email': email,
          'password': password,
        }),
      );
      
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Login failed: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Login failed: $e');
    }
  }

  Future<UserProfile> getUserProfile() async {
    try {
      final uri = Uri.parse('$_baseUrl$_apiVersion/users/profile');
      
      final headers = {'Content-Type': 'application/json'};
      if (_authToken != null) {
        headers['Authorization'] = 'Bearer $_authToken';
      }
      
      final response = await http.get(uri, headers: headers);
      
      if (response.statusCode == 200) {
        return UserProfile.fromJson(json.decode(response.body));
      } else {
        throw Exception('Failed to get user profile: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Failed to get user profile: $e');
    }
  }

  // Stories endpoints
  Future<List<Story>> getStories({
    int page = 1,
    int limit = 20,
    String? category,
    String? search,
  }) async {
    try {
      print('🔍 API: Trying authenticated stories endpoint...');
      
      final queryParams = <String, String>{
        'page': page.toString(),
        'limit': limit.toString(),
      };
      
      if (category != null) queryParams['category'] = category;
      if (search != null) queryParams['search'] = search;

      final uri = Uri.parse('$_baseUrl$_apiVersion/stories').replace(queryParameters: queryParams);
      
      final headers = {'Content-Type': 'application/json'};
      if (_authToken != null) {
        headers['Authorization'] = 'Bearer $_authToken';
      }

      final response = await http.get(uri, headers: headers);
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        if (data['stories'] != null) {
          print('🔍 API: Got ${(data['stories'] as List).length} stories from authenticated endpoint');
          return (data['stories'] as List)
              .map((json) => Story.fromJson(json))
              .toList();
        }
      } else if (response.statusCode == 401 || response.statusCode == 403 || response.statusCode == 500) {
        print('🔍 API: Stories endpoint failed with ${response.statusCode}, trying mock stories...');
        return await _getMockStories();
      }
      
      print('🔍 API: No stories in response data');
      return [];
    } catch (e) {
      print('🔍 API: Unexpected error: $e');
      return await _getMockStories();
    }
  }

  Future<List<Story>> _getMockStories() async {
    try {
      print('🔍 API: Calling mock stories endpoint...');
      final uri = Uri.parse('$_baseUrl$_apiVersion/stories/test-mock');
      final response = await http.get(uri);
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        print('🔍 API: Mock endpoint response: $data');
        
        if (data['stories'] != null) {
          final storiesList = (data['stories'] as List);
          print('🔍 API: Got ${storiesList.length} mock stories');
          
          // Try to parse each story individually to catch errors
          final parsedStories = <Story>[];
          for (int i = 0; i < storiesList.length; i++) {
            try {
              print('🔍 API: Parsing story $i: ${storiesList[i]}');
              final story = Story.fromJson(storiesList[i]);
              parsedStories.add(story);
              print('🔍 API: Successfully parsed story $i: ${story.title}');
            } catch (e) {
              print('🔍 API: Error parsing story $i: $e');
              print('🔍 API: Story data: ${storiesList[i]}');
            }
          }
          
          print('🔍 API: Successfully parsed ${parsedStories.length} stories');
          return parsedStories;
        }
      }
      print('🔍 API: No stories in mock response');
      return [];
    } catch (e) {
      print('🔍 API: Mock stories error: $e');
      return [];
    }
  }

  Future<Story> getStory(String storyId) async {
    try {
      final uri = Uri.parse('$_baseUrl$_apiVersion/stories/$storyId');
      
      final headers = {'Content-Type': 'application/json'};
      if (_authToken != null) {
        headers['Authorization'] = 'Bearer $_authToken';
      }
      
      final response = await http.get(uri, headers: headers);
      
      if (response.statusCode == 200) {
        return Story.fromJson(json.decode(response.body));
      } else {
        throw Exception('Failed to get story: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Failed to get story: $e');
    }
  }

  // Fusion endpoints
  Future<FusionResult> fuseStories({
    required List<String> storyIds,
    required double biasLevel,
    Map<String, dynamic>? userBeliefs,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl$_apiVersion/fusion/fuse'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'story_ids': storyIds,
          'bias_level': biasLevel,
          'user_beliefs': userBeliefs,
        }),
      );
      return FusionResult.fromJson(json.decode(response.body));
    } catch (e) {
      throw Exception('Fusion failed: $e');
    }
  }

  Future<String> chatWithStories({
    required String question,
    required List<String> storyIds,
    required double biasLevel,
    Map<String, dynamic>? userBeliefs,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl$_apiVersion/fusion/chat'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'question': question,
          'story_ids': storyIds,
          'bias_level': biasLevel,
          'user_beliefs': userBeliefs,
        }),
      );
      return json.decode(response.body)['response'] ?? 'No response available';
    } catch (e) {
      throw Exception('Chat failed: $e');
    }
  }

  // Article aggregation endpoints
  Future<ArticleAggregationResponse> aggregateArticles({
    required List<String> topics,
    required Map<String, List<String>> beliefs,
    required double bias,
    int limitPerTopic = 10,
  }) async {
    final request = ArticleAggregationRequest(
      topics: topics,
      beliefs: beliefs,
      bias: bias,
      limitPerTopic: limitPerTopic,
    );
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl$_apiVersion/articles/aggregate'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(request.toJson()),
      );
      return ArticleAggregationResponse.fromJson(json.decode(response.body));
    } catch (e) {
      throw Exception('Aggregation failed: $e');
    }
  }

  Future<Map<String, dynamic>> testArticlesEndpoint() async {
    try {
      final response = await http.get(Uri.parse('$_baseUrl$_apiVersion/articles/test'));
      return json.decode(response.body);
    } catch (e) {
      throw Exception('Test endpoint failed: $e');
    }
  }

  Future<List<Article>> getArticlesByTopic(String topic, {int limit = 20}) async {
    try {
      final uri = Uri.parse('$_baseUrl$_apiVersion/articles/topic/$topic').replace(
        queryParameters: {'limit': limit.toString()},
      );
      
      final response = await http.get(
        uri,
        headers: {'Content-Type': 'application/json'},
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        if (data['articles'] != null) {
          return (data['articles'] as List)
              .map((json) => Article.fromJson(json))
              .toList();
        }
      }
      throw Exception('Failed to get articles: ${response.statusCode}');
    } catch (e) {
      throw Exception('Failed to get articles: $e');
    }
  }

  // Static methods for direct use
  static Future<List<Article>> getArticlesByCategoryStatic({
    required List<String> categories,
    double bias = 0.5,
    int limitPerCategory = 10,
    String? authToken,
  }) async {
    try {
      print('🔍 API: Fetching articles for categories: $categories');
      print('🔍 API: Bias setting: $bias');
      
      final uri = Uri.parse('$_baseUrl$_apiVersion/articles/aggregate');
      
      final headers = <String, String>{
        'Content-Type': 'application/json',
      };
      
      if (authToken != null) {
        headers['Authorization'] = 'Bearer $authToken';
      }
      
      final body = json.encode({
        'categories': categories,
        'bias': bias,
        'limit_per_category': limitPerCategory,
      });
      
      print('🔍 API: Requesting URL: $uri');
      print('🔍 API: Request body: $body');
      
      final response = await http.post(
        uri,
        headers: headers,
        body: body,
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final articlesData = data['articles'] as List;
        
        print('🔍 API: Got ${articlesData.length} articles from backend');
        
        final articles = articlesData.map((articleData) => 
          Article.fromJson(articleData)
        ).toList();
        
        print('🔍 API: Converted ${articles.length} articles');
        
        return articles;
      } else {
        print('🔍 API: HTTP Error ${response.statusCode}: ${response.body}');
        throw Exception('Failed to fetch articles: ${response.statusCode}');
      }
    } catch (e) {
      print('🔍 API: Error fetching articles: $e');
      throw Exception('Failed to fetch articles: $e');
    }
  }

  // Public endpoint for article aggregation (no auth required)
  static Future<List<Article>> getArticlesByCategoryPublicStatic({
    required List<String> categories,
    double bias = 0.5,
    int limitPerCategory = 10,
  }) async {
    try {
      print('🔍 API: Fetching articles (public) for categories: $categories');
      
      final uri = Uri.parse('$_baseUrl$_apiVersion/articles/aggregate-public');
      
      final headers = <String, String>{
        'Content-Type': 'application/json',
      };
      
      final body = json.encode({
        'categories': categories,
        'bias': bias,
        'limit_per_category': limitPerCategory,
      });
      
      print('🔍 API: Requesting URL: $uri');
      
      final response = await http.post(
        uri,
        headers: headers,
        body: body,
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final articlesData = data['articles'] as List;
        
        print('🔍 API: Got ${articlesData.length} articles from public endpoint');
        
        final articles = articlesData.map((articleData) => 
          Article.fromJson(articleData)
        ).toList();
        
        return articles;
      } else {
        print('🔍 API: HTTP Error ${response.statusCode}: ${response.body}');
        throw Exception('Failed to fetch articles: ${response.statusCode}');
      }
    } catch (e) {
      print('🔍 API: Error fetching articles: $e');
      throw Exception('Failed to fetch articles: $e');
    }
  }

  // Test endpoint to verify backend is working
  static Future<Map<String, dynamic>> testBackendConnectionStatic() async {
    try {
      final uri = Uri.parse('$_baseUrl$_apiVersion/articles/test');
      
      final response = await http.get(uri);
      
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Backend test failed: ${response.statusCode}');
      }
    } catch (e) {
      print('🔍 API: Error testing backend: $e');
      throw Exception('Backend connection failed: $e');
    }
  }

  // Get mock articles for testing
  static Future<List<Article>> getMockArticlesStatic() async {
    try {
      final uri = Uri.parse('$_baseUrl$_apiVersion/articles/test-mock');
      
      final response = await http.get(uri);
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final articlesData = data['articles'] as List;
        
        return articlesData.map((articleData) => 
          Article.fromJson(articleData)
        ).toList();
      } else {
        throw Exception('Failed to get mock articles: ${response.statusCode}');
      }
    } catch (e) {
      print('🔍 API: Error getting mock articles: $e');
      throw Exception('Failed to get mock articles: $e');
    }
  }

  // Helper method to get category display name
  static String getCategoryDisplayName(String category) {
    final displayNames = {
      'geopolitics': 'Geopolitics',
      'economics': 'Economics',
      'social_issues': 'Social Issues',
      'tech_science': 'Tech & Science',
      'health': 'Health',
      'sports': 'Sports',
    };
    return displayNames[category] ?? category;
  }

  // Helper method to get category icon
  static String getCategoryIcon(String category) {
    final icons = {
      'geopolitics': '🌍',
      'economics': '💰',
      'social_issues': '🤝',
      'tech_science': '🔬',
      'health': '🏥',
      'sports': '⚽',
    };
    return icons[category] ?? '📰';
  }

  // Error handling
  static String handleError(dynamic error) {
    if (error is Exception) {
      return error.toString().replaceAll('Exception: ', '');
    }
    return error.toString();
  }
}

// Provider
final apiServiceProvider = Provider<ApiService>((ref) => ApiService()); 