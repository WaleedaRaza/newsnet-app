import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:firebase_auth/firebase_auth.dart';

import '../models/user_profile.dart';
import '../services/firebase_service.dart';

part 'auth_provider.g.dart';

@riverpod
class AuthNotifier extends _$AuthNotifier {
  @override
  Future<UserProfile?> build() async {
    final user = FirebaseService.getCurrentUser();
    if (user != null) {
      try {
        return await FirebaseService.getUserProfile(user.uid);
      } catch (e) {
        // If user profile doesn't exist, create one
        final profile = UserProfile(
          id: user.uid,
          email: user.email ?? '',
          name: user.displayName ?? '',
          interests: [],
          beliefFingerprint: <String, List<String>>{},
          biasSetting: 0.5,
          createdAt: DateTime.now(),
          updatedAt: DateTime.now(),
        );
        await FirebaseService.updateUserProfile(profile);
        return profile;
      }
    }
    return null;
  }

  Future<void> signUp({
    required String email,
    required String password,
    String? name,
  }) async {
    state = const AsyncValue.loading();
    try {
      await FirebaseService.signUp(
        email: email,
        password: password,
        name: name,
      );
      
      // Refresh the state to get the new user profile
      final user = FirebaseService.getCurrentUser();
      if (user != null) {
        final profile = await FirebaseService.getUserProfile(user.uid);
        state = AsyncValue.data(profile);
      }
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
    }
  }

  Future<void> signIn({
    required String email,
    required String password,
  }) async {
    state = const AsyncValue.loading();
    try {
      await FirebaseService.signIn(
        email: email,
        password: password,
      );
      
      // Refresh the state to get the user profile
      final user = FirebaseService.getCurrentUser();
      if (user != null) {
        final profile = await FirebaseService.getUserProfile(user.uid);
        state = AsyncValue.data(profile);
      }
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
    }
  }

  Future<void> signOut() async {
    state = const AsyncValue.loading();
    try {
      await FirebaseService.signOut();
      state = const AsyncValue.data(null);
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
    }
  }

  Future<void> updateProfile(UserProfile profile) async {
    try {
      await FirebaseService.updateUserProfile(profile);
      state = AsyncValue.data(profile);
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
    }
  }

  Future<void> updateBiasSetting(double bias) async {
    final currentProfile = state.value;
    if (currentProfile != null) {
      final updatedProfile = currentProfile.copyWith(
        biasSetting: bias,
        updatedAt: DateTime.now(),
      );
      await updateProfile(updatedProfile);
    }
  }

  Future<void> updateInterests(List<String> interests) async {
    final currentProfile = state.value;
    if (currentProfile != null) {
      final updatedProfile = currentProfile.copyWith(
        interests: interests,
        updatedAt: DateTime.now(),
      );
      await updateProfile(updatedProfile);
    }
  }

  Future<void> updateBeliefFingerprint(Map<String, List<String>> fingerprint) async {
    final currentProfile = state.value;
    if (currentProfile != null) {
      final updatedProfile = currentProfile.copyWith(
        beliefFingerprint: fingerprint,
        updatedAt: DateTime.now(),
      );
      await updateProfile(updatedProfile);
    }
  }
}

// Provider for Firebase Auth state
final firebaseAuthProvider = StreamProvider<User?>((ref) {
  return FirebaseService.authStateChanges;
});

// Provider for current user profile
final currentUserProvider = FutureProvider<UserProfile?>((ref) async {
  final authState = await ref.watch(firebaseAuthProvider.future);
  if (authState != null) {
    return await FirebaseService.getUserProfile(authState.uid);
  }
  return null;
}); 