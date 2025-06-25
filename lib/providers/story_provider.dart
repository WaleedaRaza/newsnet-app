import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../models/story.dart';
import '../models/fusion_result.dart';
import '../models/chat_message.dart';
import '../services/firebase_service.dart';
import '../services/news_service.dart';

part 'story_provider.g.dart';

@riverpod
class StoriesNotifier extends _$StoriesNotifier {
  @override
  Future<List<Story>> build() async {
    // Try to get stories from Firebase first, then fetch from News API if needed
    try {
      final stories = await FirebaseService.getStories(limit: 20);
      if (stories.isNotEmpty) {
        return stories;
      }
    } catch (e) {
      // If Firebase fails, fetch from News API
    }

    // Fetch fresh stories from News API
    return await NewsService.getTopHeadlines(pageSize: 20);
  }

  Future<void> refresh() async {
    state = const AsyncValue.loading();
    try {
      // Fetch fresh stories from News API
      final stories = await NewsService.getTopHeadlines(pageSize: 20);
      
      // Save to Firebase
      for (final story in stories) {
        await FirebaseService.createStory(story);
      }
      
      state = AsyncValue.data(stories);
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
    }
  }

  Future<void> loadMore() async {
    final currentState = state.value;
    if (currentState == null) return;

    try {
      final newStories = await NewsService.getTopHeadlines(pageSize: 20);
      
      // Combine with existing stories
      final combinedStories = [...currentState, ...newStories];
      state = AsyncValue.data(combinedStories);
    } catch (e) {
      // Don't update state on error for pagination
    }
  }

  Future<void> filterByTopics(List<String> topics) async {
    state = const AsyncValue.loading();
    try {
      final stories = await FirebaseService.getStories(topics: topics);
      if (stories.isNotEmpty) {
        state = AsyncValue.data(stories);
      } else {
        // If no stories in Firebase, fetch from News API
        final newsStories = await NewsService.getTopHeadlines(pageSize: 20);
        final filteredStories = newsStories.where((story) => 
          story.topics.any((topic) => topics.contains(topic))
        ).toList();
        state = AsyncValue.data(filteredStories);
      }
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
  try {
    return await FirebaseService.getStory(storyId);
  } catch (e) {
    // If story not found in Firebase, create a mock story
    return Story(
      id: storyId,
      eventKey: 'mock-event',
      title: 'Story not found',
      summaryNeutral: 'This story could not be loaded.',
      summaryModulated: 'This story could not be loaded.',
      sources: ['Unknown'],
      timelineChunks: [],
      publishedAt: DateTime.now(),
      updatedAt: DateTime.now(),
      topics: ['general'],
      confidence: 0.0,
    );
  }
}

@riverpod
Future<FusionResult> fusionResult(FusionResultRef ref, String storyId, double bias) async {
  try {
    return await FirebaseService.getFusionResult(storyId, bias);
  } catch (e) {
    // Return a mock fusion result if Firebase fails
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
      final stories = await NewsService.searchNews(query: query);
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
  try {
    final story = await FirebaseService.getStory(storyId);
    return story.timelineChunks;
  } catch (e) {
    return [];
  }
}

@riverpod
class ChatNotifier extends _$ChatNotifier {
  String? _storyId;

  @override
  Future<List<ChatMessage>> build(String storyId) async {
    _storyId = storyId;
    try {
      return await FirebaseService.getChatMessages(storyId);
    } catch (e) {
      return [];
    }
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
      
      final updatedMessages = [...currentMessages, userMessage, aiMessage];
      
      // Save messages to Firebase
      await FirebaseService.saveChatMessage(userMessage);
      await FirebaseService.saveChatMessage(aiMessage);
      
      state = AsyncValue.data(updatedMessages);
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
    }
  }

  Future<void> refresh() async {
    state = const AsyncValue.loading();
    try {
      final messages = await FirebaseService.getChatMessages(_storyId ?? '');
      state = AsyncValue.data(messages);
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
    }
  }

  String _generateAIResponse(String userMessage, double bias) {
    final biasLabels = {
      0.0: 'Challenge Me',
      0.25: 'Question',
      0.5: 'Neutral',
      0.75: 'Support',
      1.0: 'Prove Me Right',
    };

    final biasLabel = biasLabels.entries
        .where((entry) => bias <= entry.key)
        .first
        .value;

    final responses = {
      'Challenge Me': [
        "That's an interesting perspective, but let me challenge that view...",
        "I understand your point, though there might be another angle to consider...",
        "That's a valid question, but let me provide some counterpoints...",
      ],
      'Question': [
        "That's a good question. Let me explore this further...",
        "I see where you're coming from. Let me add some context...",
        "That's an interesting point. Let me provide some additional information...",
      ],
      'Neutral': [
        "Based on the available information, here's what I can tell you...",
        "Looking at the facts, it appears that...",
        "From what I can analyze, the situation seems to be...",
      ],
      'Support': [
        "You're absolutely right about that. Let me add some supporting evidence...",
        "I agree with your perspective. Here's some additional context...",
        "That's a valid point. Let me provide some supporting information...",
      ],
      'Prove Me Right': [
        "You're absolutely correct! Here's the evidence that supports your view...",
        "Exactly! Let me show you why you're right about this...",
        "You've got it right! Here's the proof that backs up your position...",
      ],
    };

    final responseList = responses[biasLabel] ?? responses['Neutral']!;
    final randomIndex = DateTime.now().millisecondsSinceEpoch % responseList.length;
    
    return responseList[randomIndex];
  }
} 