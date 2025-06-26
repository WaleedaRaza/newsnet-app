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
    // Try to get real stories from NewsAPI first, then fallback to mock
    try {
      print('🔍 STORY PROVIDER: Trying NewsAPI for general stories...');
      final newsStories = await NewsService.getTopHeadlines(category: 'geopolitics');
      print('🔍 STORY PROVIDER: NewsAPI returned ${newsStories.length} stories');
      
      if (newsStories.isNotEmpty) {
        // Debug: Check the first story to see if it's real
        final firstStory = newsStories.first;
        print('🔍 STORY PROVIDER: First story title: ${firstStory.title}');
        print('🔍 STORY PROVIDER: First story source: ${firstStory.sources}');
        print('🔍 STORY PROVIDER: First story URL: ${firstStory.url}');
        
        if (firstStory.sources.contains('Sample News')) {
          print('🔍 STORY PROVIDER: WARNING - Still getting mock stories from NewsAPI!');
        } else {
          print('🔍 STORY PROVIDER: SUCCESS - Got real stories from NewsAPI');
        }
        
        return newsStories;
      } else {
        print('🔍 STORY PROVIDER: NewsAPI returned empty list');
      }
    } catch (e) {
      print('🔍 STORY PROVIDER: NewsAPI failed: $e');
    }

    // Fallback to mock stories
    try {
      print('🔍 STORY PROVIDER: Falling back to mock stories...');
      final apiService = ApiService();
      final mockStories = await apiService.getStories();
      print('🔍 STORY PROVIDER: Got ${mockStories.length} mock stories');
      return mockStories;
    } catch (e) {
      print('🔍 STORY PROVIDER: Mock stories also failed: $e');
      return [];
    }
  }

  Future<void> refresh() async {
    print('🔍 STORY PROVIDER: refresh() called');
    state = const AsyncValue.loading();
    try {
      print('🔍 STORY PROVIDER: Trying NewsAPI for fresh stories...');
      final newsStories = await NewsService.getTopHeadlines(category: 'geopolitics');
      if (newsStories.isNotEmpty) {
        print('🔍 STORY PROVIDER: Got ${newsStories.length} fresh stories from NewsAPI');
        state = AsyncValue.data(newsStories);
        return;
      }
    } catch (e) {
      print('🔍 STORY PROVIDER: NewsAPI refresh failed: $e');
    }

    // Fallback to mock stories
    try {
      print('🔍 STORY PROVIDER: Falling back to mock stories for refresh...');
      final apiService = ApiService();
      final mockStories = await apiService.getStories();
      print('🔍 STORY PROVIDER: Got ${mockStories.length} mock stories for refresh');
      state = AsyncValue.data(mockStories);
    } catch (e) {
      print('🔍 STORY PROVIDER: Error in refresh(): $e');
      state = AsyncValue.error(e, StackTrace.current);
    }
  }

  Future<void> loadMore() async {
    final currentState = state.value;
    if (currentState == null) return;

    try {
      print('🔍 STORY PROVIDER: loadMore() called');
      final apiService = ApiService();
      final newStories = await apiService.getStories();
      
      // Combine with existing stories, avoiding duplicates
      final existingIds = currentState.map((s) => s.id).toSet();
      final uniqueNewStories = newStories.where((s) => !existingIds.contains(s.id)).toList();
      
      final combinedStories = [...currentState, ...uniqueNewStories];
      print('🔍 STORY PROVIDER: Loaded ${uniqueNewStories.length} more stories');
      state = AsyncValue.data(combinedStories);
    } catch (e) {
      print('🔍 STORY PROVIDER: Error in loadMore(): $e');
      // Don't update state on error for pagination
    }
  }

  Future<void> filterByTopics(List<String> topics) async {
    print('🔍 STORY PROVIDER: filterByTopics() called with topics: $topics');
    state = const AsyncValue.loading();
    
    try {
      // Try to get real stories for the first topic
      if (topics.isNotEmpty) {
        final category = topics.first;
        print('🔍 STORY PROVIDER: Trying NewsAPI for category: $category');
        
        try {
          final newsStories = await NewsService.getTopHeadlines(category: category);
          if (newsStories.isNotEmpty) {
            print('🔍 STORY PROVIDER: Got ${newsStories.length} real stories for $category');
            state = AsyncValue.data(newsStories);
            return;
          }
        } catch (e) {
          print('🔍 STORY PROVIDER: NewsAPI failed for $category: $e');
        }
      }

      // Fallback to mock stories and filter
      print('🔍 STORY PROVIDER: Falling back to mock stories for filtering...');
      final apiService = ApiService();
      final stories = await apiService.getStories();
      final filteredStories = stories.where((story) => 
        story.topics.any((topic) => topics.contains(topic))
      ).toList();
      
      print('🔍 STORY PROVIDER: Filtered to ${filteredStories.length} stories');
      state = AsyncValue.data(filteredStories);
    } catch (e) {
      print('🔍 STORY PROVIDER: Error in filterByTopics(): $e');
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
  print('🔍 STORY PROVIDER: story() called for ID: $storyId');
  
  // Try to get the story from the current stories list
  final storiesState = ref.watch(storiesNotifierProvider);
  
  return storiesState.when(
    data: (stories) {
      // Find the story with the matching ID
      final story = stories.firstWhere(
        (s) => s.id == storyId,
        orElse: () {
          print('🔍 STORY PROVIDER: Story not found in list, creating fallback');
          // If not found, create a fallback story
          return Story(
            id: storyId,
            eventKey: 'fallback-event',
            title: 'Story Not Found',
            summaryNeutral: 'This story could not be loaded.',
            summaryModulated: 'This story could not be loaded.',
            sources: ['Unknown Source'],
            timelineChunks: [],
            publishedAt: DateTime.now(),
            updatedAt: DateTime.now(),
            topics: ['general'],
            confidence: 0.0,
          );
        },
      );
      
      print('🔍 STORY PROVIDER: Found story: ${story.title}');
      print('🔍 STORY PROVIDER: Story URL: ${story.url}');
      return story;
    },
    loading: () {
      print('🔍 STORY PROVIDER: Stories still loading, returning fallback');
      return Story(
        id: storyId,
        eventKey: 'loading-event',
        title: 'Loading...',
        summaryNeutral: 'Story is loading...',
        summaryModulated: 'Story is loading...',
        sources: ['Loading'],
        timelineChunks: [],
        publishedAt: DateTime.now(),
        updatedAt: DateTime.now(),
        topics: ['general'],
        confidence: 0.0,
      );
    },
    error: (error, stack) {
      print('🔍 STORY PROVIDER: Error loading stories: $error');
      return Story(
        id: storyId,
        eventKey: 'error-event',
        title: 'Error Loading Story',
        summaryNeutral: 'Failed to load story: $error',
        summaryModulated: 'Failed to load story: $error',
        sources: ['Error'],
        timelineChunks: [],
        publishedAt: DateTime.now(),
        updatedAt: DateTime.now(),
        topics: ['general'],
        confidence: 0.0,
      );
    },
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

  Future<void> search(String query, {double bias = 0.5}) async {
    if (query.trim().isEmpty) {
      state = const AsyncValue.data(null);
      return;
    }

    state = const AsyncValue.loading();
    try {
      print('🔍 SEARCH: Searching for query: $query with bias: $bias');
      final apiService = ApiService();
      final articles = await apiService.searchArticles(query, bias);
      
      // Convert Article objects to Story objects
      final stories = articles.map((article) => Story(
        id: 'search-${article.url.hashCode}',
        eventKey: 'search-${article.url.hashCode}',
        title: article.title,
        summaryNeutral: article.description,
        summaryModulated: article.description, // For now, use same content
        sources: [article.source.name],
        timelineChunks: [], // Empty for search results
        publishedAt: article.publishedAt != null 
            ? DateTime.tryParse(article.publishedAt!) ?? DateTime.now()
            : DateTime.now(),
        updatedAt: DateTime.now(),
        topics: ['search-result'],
        confidence: article.biasAnalysis?.stanceConfidence ?? 0.5,
        url: article.url,
      )).toList();
      
      print('🔍 SEARCH: Found ${stories.length} stories');
      state = AsyncValue.data(stories);
    } catch (e) {
      print('🔍 SEARCH: Error searching: $e');
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