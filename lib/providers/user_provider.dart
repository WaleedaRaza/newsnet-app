import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:dio/dio.dart';

import '../models/user_profile.dart';
import '../services/auth_service.dart';
import '../services/api_service.dart';

part 'user_provider.g.dart';

@riverpod
ApiService apiService(ApiServiceRef ref) {
  return ApiService();
}

@riverpod
AuthService authService(AuthServiceRef ref) {
  return AuthService(ref.read(apiServiceProvider));
}

@riverpod
class UserNotifier extends _$UserNotifier {
  @override
  Future<UserProfile?> build() async {
    final authService = ref.read(authServiceProvider);
    
    if (authService.isAuthenticated) {
      try {
        return await authService.getCurrentUser();
      } catch (e) {
        return null;
      }
    }
    
    return null;
  }

  Future<void> login(String email, String password) async {
    state = const AsyncValue.loading();
    
    try {
      final authService = ref.read(authServiceProvider);
      final user = await authService.login(email, password);
      state = AsyncValue.data(user);
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
    }
  }

  Future<void> register(String email, String password, {String? name}) async {
    state = const AsyncValue.loading();
    
    try {
      final authService = ref.read(authServiceProvider);
      final user = await authService.register(email, password, name: name);
      state = AsyncValue.data(user);
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
    }
  }

  Future<void> logout() async {
    try {
      final authService = ref.read(authServiceProvider);
      await authService.logout();
      state = const AsyncValue.data(null);
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
    }
  }

  Future<void> updateProfile(UserProfile profile) async {
    try {
      final authService = ref.read(authServiceProvider);
      final updatedUser = await authService.updateProfile(profile);
      state = AsyncValue.data(updatedUser);
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
    }
  }

  Future<void> updateBeliefs(String topic, List<String> beliefs) async {
    try {
      final authService = ref.read(authServiceProvider);
      await authService.updateBeliefs(topic, beliefs);
      
      // Update local state
      final currentUser = state.value;
      if (currentUser != null) {
        final updatedBeliefs = Map<String, List<String>>.from(currentUser.beliefFingerprint);
        updatedBeliefs[topic] = beliefs;
        
        final updatedUser = currentUser.copyWith(beliefFingerprint: updatedBeliefs);
        state = AsyncValue.data(updatedUser);
      }
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
    }
  }

  Future<void> updateBiasSetting(double biasSetting) async {
    try {
      final currentUser = state.value;
      if (currentUser != null) {
        final updatedUser = currentUser.copyWith(biasSetting: biasSetting);
        await updateProfile(updatedUser);
      }
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
    }
  }
}

@riverpod
class BiasNotifier extends _$BiasNotifier {
  @override
  double build() {
    return 0.5; // Default neutral bias
  }

  void setBias(double bias) {
    state = bias.clamp(0.0, 1.0);
  }

  String getBiasLabel() {
    if (state <= 0.25) return 'Challenge Me';
    if (state <= 0.5) return 'Question';
    if (state <= 0.75) return 'Support';
    return 'Prove Me Right';
  }
} 