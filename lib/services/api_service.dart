import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/user_profile.dart';
import '../models/story.dart';
import '../models/fusion_result.dart';
import '../models/article.dart';
import '../services/firebase_service.dart';

class ApiService {
  static const String baseUrl = 'http://127.0.0.1:8000/v1';
  final Dio _dio = Dio(BaseOptions(
    baseUrl: baseUrl,
    connectTimeout: const Duration(seconds: 10),
    receiveTimeout: const Duration(seconds: 10),
  ));

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
  Future<void> _setAuthHeaders() async {
    final token = await _getAuthToken();
    if (token != null) {
      _dio.options.headers['Authorization'] = 'Bearer $token';
    } else {
      _dio.options.headers.remove('Authorization');
    }
  }

  // Set auth token
  void setAuthToken(String token) {
    _dio.options.headers['Authorization'] = 'Bearer $token';
  }

  // Clear auth token
  void clearAuthToken() {
    _dio.options.headers.remove('Authorization');
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
      final response = await _dio.post('/auth/register', data: {
        'email': email,
        'password': password,
        'name': name,
        'interests': interests,
        'belief_fingerprint': beliefFingerprint,
        'bias_setting': biasSetting,
      });
      return response.data;
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  Future<Map<String, dynamic>> login({
    required String email,
    required String password,
  }) async {
    try {
      final response = await _dio.post('/auth/login', data: {
        'email': email,
        'password': password,
      });
      return response.data;
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  Future<UserProfile> getUserProfile() async {
    try {
      final response = await _dio.get('/users/profile');
      return UserProfile.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleDioError(e);
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
      await _setAuthHeaders(); // Ensure auth headers are set
      
      final queryParams = <String, dynamic>{
        'page': page,
        'limit': limit,
      };
      
      if (category != null) queryParams['category'] = category;
      if (search != null) queryParams['search'] = search;

      final response = await _dio.get('/stories', queryParameters: queryParams);
      
      if (response.data['stories'] != null) {
        print('🔍 API: Got ${(response.data['stories'] as List).length} stories from authenticated endpoint');
        return (response.data['stories'] as List)
            .map((json) => Story.fromJson(json))
            .toList();
      }
      print('🔍 API: No stories in response data');
      return [];
    } on DioException catch (e) {
      // If auth fails or other error, try mock stories
      if (e.response?.statusCode == 401 || e.response?.statusCode == 403 || e.response?.statusCode == 500) {
        print('🔍 API: Stories endpoint failed with ${e.response?.statusCode}, trying mock stories...');
        return await _getMockStories();
      }
      print('🔍 API: Unexpected error: ${e.message}');
      throw _handleDioError(e);
    }
  }

  Future<List<Story>> _getMockStories() async {
    try {
      print('🔍 API: Calling mock stories endpoint...');
      final response = await _dio.get('/stories/test-mock');
      print('🔍 API: Mock endpoint response: ${response.data}');
      
      if (response.data['stories'] != null) {
        final storiesList = (response.data['stories'] as List);
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
      print('🔍 API: No stories in mock response');
      return [];
    } on DioException catch (e) {
      print('🔍 API: Mock stories error: ${e.message}');
      throw _handleDioError(e);
    } catch (e) {
      print('🔍 API: Unexpected error in _getMockStories: $e');
      rethrow;
    }
  }

  Future<Story> getStory(String storyId) async {
    try {
      final response = await _dio.get('/stories/$storyId');
      return Story.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  // Fusion endpoints
  Future<FusionResult> fuseStories({
    required List<String> storyIds,
    required double biasLevel,
    Map<String, dynamic>? userBeliefs,
  }) async {
    try {
      final response = await _dio.post('/fusion/fuse', data: {
        'story_ids': storyIds,
        'bias_level': biasLevel,
        'user_beliefs': userBeliefs,
      });
      return FusionResult.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  Future<String> chatWithStories({
    required String question,
    required List<String> storyIds,
    required double biasLevel,
    Map<String, dynamic>? userBeliefs,
  }) async {
    try {
      final response = await _dio.post('/fusion/chat', data: {
        'question': question,
        'story_ids': storyIds,
        'bias_level': biasLevel,
        'user_beliefs': userBeliefs,
      });
      return response.data['response'] ?? 'No response available';
    } on DioException catch (e) {
      throw _handleDioError(e);
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
      await _setAuthHeaders(); // Ensure auth headers are set
      
      final response = await _dio.post('/articles/aggregate', data: request.toJson());
      return ArticleAggregationResponse.fromJson(response.data);
    } on DioException catch (e) {
      // If auth fails, try public endpoint
      if (e.response?.statusCode == 401 || e.response?.statusCode == 403) {
        print('Auth failed, trying public endpoint...');
        return await _aggregateArticlesPublic(request);
      }
      throw _handleDioError(e);
    }
  }

  Future<ArticleAggregationResponse> _aggregateArticlesPublic(
    ArticleAggregationRequest request,
  ) async {
    try {
      final response = await _dio.post('/articles/aggregate-public', data: request.toJson());
      return ArticleAggregationResponse.fromJson(response.data);
    } on DioException catch (e) {
      // If public endpoint fails, try mock endpoint for testing
      print('Public aggregation failed, trying mock endpoint...');
      return await _getMockArticles();
    }
  }

  Future<ArticleAggregationResponse> _getMockArticles() async {
    try {
      final response = await _dio.get('/articles/test-mock');
      return ArticleAggregationResponse.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  Future<Map<String, dynamic>> testArticlesEndpoint() async {
    try {
      final response = await _dio.get('/articles/test');
      return response.data;
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  Future<List<Article>> getArticlesByTopic(String topic, {int limit = 20}) async {
    try {
      await _setAuthHeaders(); // Ensure auth headers are set
      
      final response = await _dio.get('/articles/topic/$topic', queryParameters: {
        'limit': limit,
      });
      
      if (response.data['articles'] != null) {
        return (response.data['articles'] as List)
            .map((json) => Article.fromJson(json))
            .toList();
      }
      return [];
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  // Error handling
  Exception _handleDioError(DioException e) {
    if (e.response != null) {
      final statusCode = e.response!.statusCode;
      final data = e.response!.data;
      
      switch (statusCode) {
        case 400:
          return Exception(data['detail'] ?? 'Bad request');
        case 401:
          return Exception('Unauthorized - Please login again');
        case 403:
          return Exception('Forbidden');
        case 404:
          return Exception('Resource not found');
        case 409:
          return Exception(data['detail'] ?? 'Conflict');
        case 422:
          return Exception('Validation error');
        case 500:
          return Exception('Server error');
        default:
          return Exception('Network error: $statusCode');
      }
    } else if (e.type == DioExceptionType.connectionTimeout) {
      return Exception('Connection timeout');
    } else if (e.type == DioExceptionType.receiveTimeout) {
      return Exception('Receive timeout');
    } else if (e.type == DioExceptionType.connectionError) {
      return Exception('Connection error - Please check your internet connection');
    } else {
      return Exception('Network error: ${e.message}');
    }
  }
}

// Provider
final apiServiceProvider = Provider<ApiService>((ref) => ApiService()); 