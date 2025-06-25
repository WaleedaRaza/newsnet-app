import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/api_service.dart';
import '../models/story.dart';

class TestStoriesScreen extends ConsumerStatefulWidget {
  const TestStoriesScreen({super.key});

  @override
  ConsumerState<TestStoriesScreen> createState() => _TestStoriesScreenState();
}

class _TestStoriesScreenState extends ConsumerState<TestStoriesScreen> {
  List<Story>? stories;
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

      final apiService = ApiService();
      final storiesList = await apiService.getStories();
      
      setState(() {
        stories = storiesList;
        isLoading = false;
      });
    } catch (e) {
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
              : stories == null || stories!.isEmpty
                  ? const Center(child: Text('No stories found'))
                  : ListView.builder(
                      itemCount: stories!.length,
                      itemBuilder: (context, index) {
                        final story = stories![index];
                        return Card(
                          margin: const EdgeInsets.all(8),
                          child: ListTile(
                            title: Text(story.title),
                            subtitle: Text(story.summaryNeutral),
                            trailing: Text('${story.topics.join(', ')}'),
                          ),
                        );
                      },
                    ),
    );
  }
} 