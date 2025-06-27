import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/stance_detection.dart';
import '../services/stance_detection_service.dart';
import '../services/firebase_service.dart';

// Service provider
final stanceDetectionServiceProvider = Provider<StanceDetectionService>((ref) {
  return StanceDetectionService();
});

// Current user's belief fingerprint
final userBeliefFingerprintProvider = StateNotifierProvider<UserBeliefFingerprintNotifier, AsyncValue<UserBeliefFingerprint?>>((ref) {
  return UserBeliefFingerprintNotifier(ref.read(stanceDetectionServiceProvider));
});

// Stance detection results
final stanceDetectionResultsProvider = StateNotifierProvider<StanceDetectionResultsNotifier, AsyncValue<List<StanceDetectionResponse>>>((ref) {
  return StanceDetectionResultsNotifier(ref.read(stanceDetectionServiceProvider));
});

// Content scoring results
final contentScoringProvider = StateNotifierProvider<ContentScoringNotifier, AsyncValue<ContentScoringResponse?>>((ref) {
  return ContentScoringNotifier(ref.read(stanceDetectionServiceProvider));
});

// Belief templates
final beliefTemplatesProvider = FutureProvider<List<Map<String, dynamic>>>((ref) async {
  final service = ref.read(stanceDetectionServiceProvider);
  return await service.getBeliefTemplates();
});

// Service health status
final stanceDetectionHealthProvider = FutureProvider<bool>((ref) async {
  final service = ref.read(stanceDetectionServiceProvider);
  return await service.testConnection();
});

// User Belief Fingerprint Notifier
class UserBeliefFingerprintNotifier extends StateNotifier<AsyncValue<UserBeliefFingerprint?>> {
  final StanceDetectionService _service;

  UserBeliefFingerprintNotifier(this._service) : super(const AsyncValue.loading());

  Future<void> createFingerprint(List<BeliefStatement> beliefs) async {
    try {
      state = const AsyncValue.loading();
      
      final user = FirebaseService.getCurrentUser();
      if (user == null) {
        throw Exception('User not authenticated');
      }

      final result = await _service.createUserFingerprint(
        userId: user.uid,
        beliefs: beliefs,
      );

      // Create a UserBeliefFingerprint from the result
      final fingerprint = UserBeliefFingerprint(
        userId: user.uid,
        beliefs: beliefs,
        categories: beliefs.map((b) => b.category).toSet().toList(),
        lastUpdated: DateTime.now(),
      );

      state = AsyncValue.data(fingerprint);
    } catch (error, stackTrace) {
      state = AsyncValue.error(error, stackTrace);
    }
  }

  Future<void> updateFingerprint(List<BeliefStatement> newBeliefs) async {
    try {
      final user = FirebaseService.getCurrentUser();
      if (user == null) {
        throw Exception('User not authenticated');
      }

      final result = await _service.updateUserFingerprint(
        userId: user.uid,
        newBeliefs: newBeliefs,
      );

      // Update the current fingerprint
      final currentFingerprint = state.value;
      if (currentFingerprint != null) {
        final updatedFingerprint = UserBeliefFingerprint(
          userId: user.uid,
          beliefs: [...currentFingerprint.beliefs, ...newBeliefs],
          categories: [...currentFingerprint.categories, ...newBeliefs.map((b) => b.category)],
          lastUpdated: DateTime.now(),
        );
        state = AsyncValue.data(updatedFingerprint);
      }
    } catch (error, stackTrace) {
      state = AsyncValue.error(error, stackTrace);
    }
  }

  Future<void> analyzeBeliefs() async {
    try {
      final user = FirebaseService.getCurrentUser();
      if (user == null) {
        throw Exception('User not authenticated');
      }

      final analysis = await _service.analyzeUserBeliefs(user.uid);
      // You could store the analysis results or update the fingerprint
      print('Belief analysis: $analysis');
    } catch (error, stackTrace) {
      state = AsyncValue.error(error, stackTrace);
    }
  }

  void clearFingerprint() {
    state = const AsyncValue.data(null);
  }
}

// Stance Detection Results Notifier
class StanceDetectionResultsNotifier extends StateNotifier<AsyncValue<List<StanceDetectionResponse>>> {
  final StanceDetectionService _service;

  StanceDetectionResultsNotifier(this._service) : super(const AsyncValue.data([]));

  Future<void> detectStance({
    required String belief,
    required String articleText,
    String methodPreference = 'auto',
  }) async {
    try {
      state = const AsyncValue.loading();
      
      final result = await _service.detectStance(
        belief: belief,
        articleText: articleText,
        methodPreference: methodPreference,
      );

      state = AsyncValue.data([result]);
    } catch (error, stackTrace) {
      state = AsyncValue.error(error, stackTrace);
    }
  }

  Future<void> batchDetectStances(List<Map<String, String>> beliefArticlePairs) async {
    try {
      state = const AsyncValue.loading();
      
      final results = await _service.batchDetectStances(
        beliefArticlePairs: beliefArticlePairs,
      );

      state = AsyncValue.data(results);
    } catch (error, stackTrace) {
      state = AsyncValue.error(error, stackTrace);
    }
  }

  void clearResults() {
    state = const AsyncValue.data([]);
  }

  void addResult(StanceDetectionResponse result) {
    final currentResults = state.value ?? [];
    state = AsyncValue.data([...currentResults, result]);
  }
}

// Content Scoring Notifier
class ContentScoringNotifier extends StateNotifier<AsyncValue<ContentScoringResponse?>> {
  final StanceDetectionService _service;

  ContentScoringNotifier(this._service) : super(const AsyncValue.data(null));

  Future<void> scoreContent({
    required String contentText,
    Map<String, dynamic>? contentMetadata,
  }) async {
    try {
      state = const AsyncValue.loading();
      
      final user = FirebaseService.getCurrentUser();
      if (user == null) {
        throw Exception('User not authenticated');
      }

      final result = await _service.scoreContentForUser(
        userId: user.uid,
        contentText: contentText,
        contentMetadata: contentMetadata,
      );

      state = AsyncValue.data(result);
    } catch (error, stackTrace) {
      state = AsyncValue.error(error, stackTrace);
    }
  }

  void clearScoring() {
    state = const AsyncValue.data(null);
  }
}

// Helper providers for common operations
final stanceDetectionProvider = Provider<StanceDetectionService>((ref) {
  return StanceDetectionService();
});

// Provider for getting belief categories
final beliefCategoriesProvider = Provider<List<String>>((ref) {
  return BeliefCategories.categories;
});

// Provider for getting belief examples by category
final beliefExamplesProvider = Provider<Map<String, List<String>>>((ref) {
  return BeliefCategories.categoryExamples;
});

// Provider for checking if stance detection is available
final stanceDetectionAvailableProvider = FutureProvider<bool>((ref) async {
  final service = ref.read(stanceDetectionServiceProvider);
  return await service.testConnection();
}); 