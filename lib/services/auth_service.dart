import 'package:shared_preferences/shared_preferences.dart';

import '../core/constants.dart';
import '../models/user_profile.dart';
import 'api_service.dart';

class AuthService {
  final ApiService _apiService;
  String? _token;
  UserProfile? _currentUser;

  AuthService(this._apiService) {
    _loadToken();
  }

  String? get token => _token;
  UserProfile? get currentUser => _currentUser;
  bool get isAuthenticated => _token != null;

  Future<void> _loadToken() async {
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString(AppConstants.authTokenKey);
    if (_token != null) {
      _apiService.setAuthToken(_token!);
    }
  }

  Future<void> _saveToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(AppConstants.authTokenKey, token);
    _token = token;
    _apiService.setAuthToken(token);
  }

  Future<void> _clearToken() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(AppConstants.authTokenKey);
    _token = null;
    _apiService.clearAuthToken();
  }

  Future<UserProfile> login(String email, String password) async {
    try {
      final response = await _apiService.login(
        email: email,
        password: password,
      );
      
      final accessToken = response['access_token'];
      if (accessToken == null) {
        throw AuthException('No access token returned from server');
      }
      await _saveToken(accessToken as String);
      
      final userData = response['user'];
      if (userData == null) {
        throw AuthException('No user data returned from server');
      }
      _currentUser = UserProfile.fromJson(userData as Map<String, dynamic>);
      
      return _currentUser!;
    } catch (e) {
      throw _handleAuthError(e);
    }
  }

  Future<UserProfile> register(String email, String password, {String? name}) async {
    try {
      final response = await _apiService.register(
        email: email,
        password: password,
        name: name,
      );
      
      final accessToken = response['access_token'];
      if (accessToken == null) {
        throw AuthException('No access token returned from server');
      }
      await _saveToken(accessToken as String);
      
      final userData = response['user'];
      if (userData == null) {
        throw AuthException('No user data returned from server');
      }
      _currentUser = UserProfile.fromJson(userData as Map<String, dynamic>);
      
      return _currentUser!;
    } catch (e) {
      throw _handleAuthError(e);
    }
  }

  Future<void> logout() async {
    try {
      await _clearToken();
      _currentUser = null;
    } catch (e) {
      // Ignore logout errors
    }
  }

  Future<UserProfile> getCurrentUser() async {
    if (_currentUser != null) return _currentUser!;
    
    try {
      _currentUser = await _apiService.getUserProfile();
      return _currentUser!;
    } catch (e) {
      await logout();
      throw _handleAuthError(e);
    }
  }

  Future<UserProfile> updateProfile(UserProfile profile) async {
    try {
      // For now, just update local state since our test API doesn't have update endpoints
      _currentUser = profile;
      return _currentUser!;
    } catch (e) {
      throw _handleAuthError(e);
    }
  }

  Future<void> updateBeliefs(String topic, List<String> beliefs) async {
    try {
      // Update local user profile
      if (_currentUser != null) {
        final updatedBeliefs = Map<String, List<String>>.from(_currentUser!.beliefFingerprint);
        updatedBeliefs[topic] = beliefs;
        
        _currentUser = _currentUser!.copyWith(beliefFingerprint: updatedBeliefs);
      }
    } catch (e) {
      throw _handleAuthError(e);
    }
  }

  Exception _handleAuthError(dynamic error) {
    if (error is Exception) {
      return AuthException(error.toString());
    }
    
    return AuthException('Network error occurred');
  }
}

class AuthException implements Exception {
  final String message;
  
  AuthException(this.message);
  
  @override
  String toString() => message;
} 