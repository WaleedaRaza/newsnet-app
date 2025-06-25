import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/api_service.dart';
import '../services/news_service.dart';
import '../models/story.dart';

class TestStoriesScreen extends ConsumerStatefulWidget {
  const TestStoriesScreen({super.key});

  @override
  ConsumerState<TestStoriesScreen> createState() => _TestStoriesScreenState();
}

class _TestStoriesScreenState extends ConsumerState<TestStoriesScreen> {
  List<Story>? mockStories;
  List<Story>? realStories;
  String? error;
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadStories();
  }

  Future<void> _loadStories() async {
    try {
      setState(() {
        isLoading = true;
        error = null;
      });

      print('🔍 TEST: Starting API test...');
      
      // Test 1: Mock stories
      print('🔍 TEST: Loading mock stories...');
      final apiService = ApiService();
      final mockStoriesList = await apiService.getStories();
      print('🔍 TEST: Got ${mockStoriesList.length} mock stories');
      
      setState(() {
        mockStories = mockStoriesList;
      });

      // Test 2: Real stories from NewsAPI
      print('🔍 TEST: Loading real stories from NewsAPI...');
      try {
        final realStoriesList = await NewsService.getTopHeadlines(category: 'geopolitics');
        print('🔍 TEST: Got ${realStoriesList.length} real stories');
        
        setState(() {
          realStories = realStoriesList;
          isLoading = false;
        });
      } catch (e) {
        print('🔍 TEST: NewsAPI failed: $e');
        setState(() {
          error = 'NewsAPI failed: $e';
          isLoading = false;
        });
      }
    } catch (e) {
      print('🔍 TEST: Error: $e');
      setState(() {
        error = e.toString();
        isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Test Stories'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadStories,
          ),
        ],
      ),
      body: isLoading
          ? const Center(child: CircularProgressIndicator())
          : error != null
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text('Error: $error'),
                      const SizedBox(height: 16),
                      ElevatedButton(
                        onPressed: _loadStories,
                        child: const Text('Retry'),
                      ),
                    ],
                  ),
                )
              : SingleChildScrollView(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Mock Stories Section
                      if (mockStories != null) ...[
                        Text(
                          'Mock Stories (${mockStories!.length})',
                          style: Theme.of(context).textTheme.headlineSmall,
                        ),
                        const SizedBox(height: 8),
                        ...mockStories!.map((story) => Card(
                          margin: const EdgeInsets.only(bottom: 8),
                          child: ListTile(
                            title: Text(story.title),
                            subtitle: Text(story.summaryNeutral),
                            trailing: Text('${story.topics.join(', ')}'),
                          ),
                        )),
                        const SizedBox(height: 24),
                      ],

                      // Real Stories Section
                      if (realStories != null) ...[
                        Text(
                          'Real Stories from NewsAPI (${realStories!.length})',
                          style: Theme.of(context).textTheme.headlineSmall,
                        ),
                        const SizedBox(height: 8),
                        ...realStories!.map((story) => Card(
                          margin: const EdgeInsets.only(bottom: 8),
                          child: ListTile(
                            title: Text(story.title),
                            subtitle: Text(story.summaryNeutral),
                            trailing: Text('${story.topics.join(', ')}'),
                          ),
                        )),
                      ],

                      if (realStories == null && mockStories != null) ...[
                        const SizedBox(height: 24),
                        const Card(
                          color: Colors.orange,
                          child: Padding(
                            padding: EdgeInsets.all(16),
                            child: Text(
                              'Note: Real stories failed to load. You may need to add a valid NewsAPI key.',
                              style: TextStyle(color: Colors.white),
                            ),
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
    );
  }
} 