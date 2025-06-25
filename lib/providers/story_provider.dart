import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../models/story.dart';
import '../models/fusion_result.dart';
import '../models/chat_message.dart';
import '../services/firebase_service.dart';
import '../services/news_service.dart';
import '../services/api_service.dart';

part 'story_provider.g.dart';

@riverpod
class StoriesNotifier extends _$StoriesNotifier {
  @override
  Future<List<Story>> build() async {
    print('🔍 STORY PROVIDER: build() called');
    // Use our API service with mock fallback
    try {
      final apiService = ApiService();
      print('🔍 STORY PROVIDER: Calling apiService.getStories()');
      final stories = await apiService.getStories();
      print('🔍 STORY PROVIDER: Got ${stories.length} stories');
      return stories;
    } catch (e) {
      print('🔍 STORY PROVIDER: Error in build(): $e');
      // If API service fails, return empty list
      return [];
    }
  }

  Future<void> refresh() async {
    print('🔍 STORY PROVIDER: refresh() called');
    state = const AsyncValue.loading();
    try {
      final apiService = ApiService();
      print('🔍 STORY PROVIDER: Calling apiService.getStories() in refresh');
      final stories = await apiService.getStories();
      print('🔍 STORY PROVIDER: Got ${stories.length} stories in refresh');
      state = AsyncValue.data(stories);
    } catch (e) {
      print('🔍 STORY PROVIDER: Error in refresh(): $e');
      state = AsyncValue.error(e, StackTrace.current);
    }
  }

  Future<void> loadMore() async {
    final currentState = state.value;
    if (currentState == null) return;

    try {
      final apiService = ApiService();
      final newStories = await apiService.getStories();
      
      // Combine with existing stories, avoiding duplicates
      final existingIds = currentState.map((s) => s.id).toSet();
      final uniqueNewStories = newStories.where((s) => !existingIds.contains(s.id)).toList();
      
      final combinedStories = [...currentState, ...uniqueNewStories];
      state = AsyncValue.data(combinedStories);
    } catch (e) {
      // Don't update state on error for pagination
    }
  }

  Future<void> filterByTopics(List<String> topics) async {
    state = const AsyncValue.loading();
    try {
      final apiService = ApiService();
      // For now, just get all stories and filter them client-side
      final stories = await apiService.getStories();
      final filteredStories = stories.where((story) => 
        story.topics.any((topic) => topics.contains(topic))
      ).toList();
      state = AsyncValue.data(filteredStories);
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
    }
  }

  Future<void> setBias(double bias) async {
    // For now, just refresh stories since bias is handled per story
    await refresh();
  }
}

@riverpod
Future<Story> story(StoryRef ref, String storyId) async {
  // For now, return a mock story since we're using API service
  return Story(
    id: storyId,
    eventKey: 'mock-event',
    title: 'Sample Story',
    summaryNeutral: 'This is a sample story for testing purposes.',
    summaryModulated: 'This is a sample story with bias modulation.',
    sources: ['Sample News'],
    timelineChunks: [],
    publishedAt: DateTime.now(),
    updatedAt: DateTime.now(),
    topics: ['general'],
    confidence: 0.9,
  );
}

@riverpod
Future<FusionResult> fusionResult(FusionResultRef ref, String storyId, double bias) async {
  // Return a mock fusion result
  return FusionResult(
    id: 'mock-fusion-$storyId',
    storyId: storyId,
    fusedNarrative: 'This is a neutral narrative for the story.',
    modulatedNarrative: 'This is a bias-modulated narrative for the story.',
    biasLevel: bias,
    confidence: 0.85,
    contradictions: [],
    entities: [],
    createdAt: DateTime.now(),
  );
}

@riverpod
class SearchNotifier extends _$SearchNotifier {
  @override
  Future<List<Story>?> build() async {
    return null; // Initial state is no search
  }

  Future<void> search(String query) async {
    if (query.trim().isEmpty) {
      state = const AsyncValue.data(null);
      return;
    }

    state = const AsyncValue.loading();
    try {
      final apiService = ApiService();
      final stories = await apiService.getStories(search: query);
      state = AsyncValue.data(stories);
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
    }
  }

  void clearSearch() {
    state = const AsyncValue.data(null);
  }
}

@riverpod
Future<List<TimelineChunk>> timeline(TimelineRef ref, String storyId) async {
  // Return mock timeline chunks
  return [
    TimelineChunk(
      id: 'chunk_1',
      timestamp: DateTime.now(),
      content: 'Sample timeline content',
      sources: ['Sample Source'],
      confidence: 0.9,
      hasContradictions: false,
      contradictions: [],
    ),
  ];
}

@riverpod
class ChatNotifier extends _$ChatNotifier {
  String? _storyId;

  @override
  Future<List<ChatMessage>> build(String storyId) async {
    _storyId = storyId;
    return []; // Start with empty chat
  }

  Future<void> sendMessage(String message, double bias) async {
    try {
      final currentMessages = state.value ?? [];
      
      // Add user message
      final userMessage = ChatMessage(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        storyId: _storyId ?? '',
        content: message,
        isUser: true,
        timestamp: DateTime.now(),
      );
      
      // Add AI response
      final aiResponse = _generateAIResponse(message, bias);
      final aiMessage = ChatMessage(
        id: (DateTime.now().millisecondsSinceEpoch + 1).toString(),
        storyId: _storyId ?? '',
        content: aiResponse,
        isUser: false,
        timestamp: DateTime.now(),
      );
      
      // Update state with new messages
      state = AsyncValue.data([...currentMessages, userMessage, aiMessage]);
    } catch (e) {
      // Handle error
    }
  }

  String _generateAIResponse(String message, double bias) {
    // Simple mock AI response
    return 'This is a mock AI response to: "$message" with bias level: $bias';
  }
} 