import 'package:flutter/material.dart';
import 'package:dio/dio.dart';
import 'dart:convert';

class DebugScreen extends StatefulWidget {
  const DebugScreen({super.key});

  @override
  State<DebugScreen> createState() => _DebugScreenState();
}

class _DebugScreenState extends State<DebugScreen> {
  String _status = 'Initializing...';
  List<Map<String, dynamic>> _stories = [];
  String? _error;

  @override
  void initState() {
    super.initState();
    _testApi();
  }

  Future<void> _testApi() async {
    setState(() {
      _status = 'Testing API...';
      _error = null;
    });

    try {
      // Test 1: Direct HTTP call
      setState(() => _status = 'Making direct HTTP call...');
      
      final dio = Dio();
      final response = await dio.get('http://127.0.0.1:8000/v1/stories/test-mock');
      
      setState(() => _status = 'Got response: ${response.statusCode}');
      
      if (response.statusCode == 200) {
        final data = response.data;
        setState(() => _status = 'Response data: ${json.encode(data).substring(0, 200)}...');
        
        if (data['stories'] != null) {
          final storiesList = data['stories'] as List;
          setState(() {
            _stories = storiesList.cast<Map<String, dynamic>>();
            _status = 'Found ${_stories.length} stories';
          });
          
          // Test 2: Try to parse first story
          if (_stories.isNotEmpty) {
            setState(() => _status = 'Testing story parsing...');
            final firstStory = _stories.first;
            setState(() => _status = 'First story: ${firstStory['title']}');
          }
        } else {
          setState(() => _error = 'No stories field in response');
        }
      } else {
        setState(() => _error = 'HTTP ${response.statusCode}');
      }
    } catch (e) {
      setState(() {
        _error = e.toString();
        _status = 'Error occurred';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Debug API Test'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _testApi,
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Status
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Status: $_status',
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    if (_error != null) ...[
                      const SizedBox(height: 8),
                      Text(
                        'Error: $_error',
                        style: const TextStyle(color: Colors.red),
                      ),
                    ],
                  ],
                ),
              ),
            ),
            
            const SizedBox(height: 16),
            
            // Stories
            Expanded(
              child: _stories.isEmpty
                  ? const Center(child: Text('No stories loaded'))
                  : ListView.builder(
                      itemCount: _stories.length,
                      itemBuilder: (context, index) {
                        final story = _stories[index];
                        return Card(
                          margin: const EdgeInsets.only(bottom: 8),
                          child: ListTile(
                            title: Text(story['title'] ?? 'No title'),
                            subtitle: Text(story['summary_neutral'] ?? 'No summary'),
                            trailing: Text('${story['topics']?.length ?? 0} topics'),
                          ),
                        );
                      },
                    ),
            ),
          ],
        ),
      ),
    );
  }
} 