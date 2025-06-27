import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/stance_detection.dart';
import 'firebase_service.dart';

class StanceDetectionService {
  static const String _baseUrl = 'http://localhost:8000';
  static const String _apiVersion = '/v1/intelligence';

  // Singleton pattern
  static final StanceDetectionService _instance = StanceDetectionService._internal();
  factory StanceDetectionService() => _instance;
  StanceDetectionService._internal();

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

  // Stance Detection Methods
  Future<StanceDetectionResponse> detectStance({
    required String belief,
    required String articleText,
    String methodPreference = 'auto',
  }) async {
    try {
      final uri = Uri.parse('$_baseUrl$_apiVersion/stance/detect');
      
      final headers = {'Content-Type': 'application/json'};
      final token = await _getAuthToken();
      if (token != null) {
        headers['Authorization'] = 'Bearer $token';
      }

      final request = StanceDetectionRequest(
        belief: belief,
        articleText: articleText,
        methodPreference: methodPreference,
      );

      final response = await http.post(
        uri,
        headers: headers,
        body: json.encode(request.toJson()),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return StanceDetectionResponse.fromJson(data);
      } else {
        throw Exception('Stance detection failed: ${response.statusCode} - ${response.body}');
      }
    } catch (e) {
      throw Exception('Stance detection failed: $e');
    }
  }

  Future<List<StanceDetectionResponse>> batchDetectStances({
    required List<Map<String, String>> beliefArticlePairs,
  }) async {
    try {
      final uri = Uri.parse('$_baseUrl$_apiVersion/stance/batch');
      
      final headers = {'Content-Type': 'application/json'};
      final token = await _getAuthToken();
      if (token != null) {
        headers['Authorization'] = 'Bearer $token';
      }

      final response = await http.post(
        uri,
        headers: headers,
        body: json.encode(beliefArticlePairs),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body) as List;
        return data.map((json) => StanceDetectionResponse.fromJson(json)).toList();
      } else {
        throw Exception('Batch stance detection failed: ${response.statusCode} - ${response.body}');
      }
    } catch (e) {
      throw Exception('Batch stance detection failed: $e');
    }
  }

  Future<Map<String, dynamic>> getStanceMetrics() async {
    try {
      final uri = Uri.parse('$_baseUrl$_apiVersion/stance/metrics');
      
      final headers = {'Content-Type': 'application/json'};
      final token = await _getAuthToken();
      if (token != null) {
        headers['Authorization'] = 'Bearer $token';
      }

      final response = await http.get(uri, headers: headers);

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to get stance metrics: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Failed to get stance metrics: $e');
    }
  }

  // User Belief Fingerprinting Methods
  Future<Map<String, dynamic>> createUserFingerprint({
    required String userId,
    required List<BeliefStatement> beliefs,
  }) async {
    try {
      final uri = Uri.parse('$_baseUrl$_apiVersion/beliefs/create');
      
      final headers = {'Content-Type': 'application/json'};
      final token = await _getAuthToken();
      if (token != null) {
        headers['Authorization'] = 'Bearer $token';
      }

      final request = {
        'user_id': userId,
        'beliefs': beliefs.map((belief) => belief.toJson()).toList(),
      };

      final response = await http.post(
        uri,
        headers: headers,
        body: json.encode(request),
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to create user fingerprint: ${response.statusCode} - ${response.body}');
      }
    } catch (e) {
      throw Exception('Failed to create user fingerprint: $e');
    }
  }

  Future<Map<String, dynamic>> updateUserFingerprint({
    required String userId,
    required List<BeliefStatement> newBeliefs,
  }) async {
    try {
      final uri = Uri.parse('$_baseUrl$_apiVersion/beliefs/update');
      
      final headers = {'Content-Type': 'application/json'};
      final token = await _getAuthToken();
      if (token != null) {
        headers['Authorization'] = 'Bearer $token';
      }

      final request = {
        'user_id': userId,
        'new_beliefs': newBeliefs.map((belief) => belief.toJson()).toList(),
      };

      final response = await http.post(
        uri,
        headers: headers,
        body: json.encode(request),
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to update user fingerprint: ${response.statusCode} - ${response.body}');
      }
    } catch (e) {
      throw Exception('Failed to update user fingerprint: $e');
    }
  }

  Future<ContentScoringResponse> scoreContentForUser({
    required String userId,
    required String contentText,
    Map<String, dynamic>? contentMetadata,
  }) async {
    try {
      final uri = Uri.parse('$_baseUrl$_apiVersion/beliefs/score');
      
      final headers = {'Content-Type': 'application/json'};
      final token = await _getAuthToken();
      if (token != null) {
        headers['Authorization'] = 'Bearer $token';
      }

      final request = ContentScoringRequest(
        userId: userId,
        contentText: contentText,
        contentMetadata: contentMetadata,
      );

      final response = await http.post(
        uri,
        headers: headers,
        body: json.encode(request.toJson()),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return ContentScoringResponse.fromJson(data);
      } else {
        throw Exception('Failed to score content: ${response.statusCode} - ${response.body}');
      }
    } catch (e) {
      throw Exception('Failed to score content: $e');
    }
  }

  Future<List<Map<String, dynamic>>> getPersonalizedRecommendations({
    required String userId,
    required List<Map<String, dynamic>> contentList,
    int limit = 10,
  }) async {
    try {
      final uri = Uri.parse('$_baseUrl$_apiVersion/beliefs/recommendations');
      
      final headers = {'Content-Type': 'application/json'};
      final token = await _getAuthToken();
      if (token != null) {
        headers['Authorization'] = 'Bearer $token';
      }

      final request = {
        'user_id': userId,
        'content_list': contentList,
        'limit': limit,
      };

      final response = await http.post(
        uri,
        headers: headers,
        body: json.encode(request),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return List<Map<String, dynamic>>.from(data['recommendations'] ?? []);
      } else {
        throw Exception('Failed to get recommendations: ${response.statusCode} - ${response.body}');
      }
    } catch (e) {
      throw Exception('Failed to get recommendations: $e');
    }
  }

  Future<Map<String, dynamic>> analyzeUserBeliefs(String userId) async {
    try {
      final uri = Uri.parse('$_baseUrl$_apiVersion/beliefs/analyze/$userId');
      
      final headers = {'Content-Type': 'application/json'};
      final token = await _getAuthToken();
      if (token != null) {
        headers['Authorization'] = 'Bearer $token';
      }

      final response = await http.get(uri, headers: headers);

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to analyze user beliefs: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Failed to analyze user beliefs: $e');
    }
  }

  Future<List<Map<String, dynamic>>> getBeliefTemplates({String? category}) async {
    try {
      final queryParams = <String, String>{};
      if (category != null) {
        queryParams['categories'] = category;
      }

      final uri = Uri.parse('$_baseUrl$_apiVersion/beliefs/templates')
          .replace(queryParameters: queryParams);
      
      final headers = {'Content-Type': 'application/json'};
      final token = await _getAuthToken();
      if (token != null) {
        headers['Authorization'] = 'Bearer $token';
      }

      final response = await http.get(uri, headers: headers);

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return List<Map<String, dynamic>>.from(data['templates'] ?? []);
      } else {
        throw Exception('Failed to get belief templates: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Failed to get belief templates: $e');
    }
  }

  // Health Check
  Future<List<Map<String, dynamic>>> healthCheck() async {
    try {
      final uri = Uri.parse('$_baseUrl$_apiVersion/health');
      
      final headers = {'Content-Type': 'application/json'};
      final token = await _getAuthToken();
      if (token != null) {
        headers['Authorization'] = 'Bearer $token';
      }

      final response = await http.get(uri, headers: headers);

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return List<Map<String, dynamic>>.from(data);
      } else {
        throw Exception('Health check failed: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Health check failed: $e');
    }
  }

  // Test backend connection
  Future<bool> testConnection() async {
    try {
      final uri = Uri.parse('$_baseUrl$_apiVersion/health');
      final response = await http.get(uri);
      return response.statusCode == 200;
    } catch (e) {
      print('Stance detection service connection test failed: $e');
      return false;
    }
  }
} 