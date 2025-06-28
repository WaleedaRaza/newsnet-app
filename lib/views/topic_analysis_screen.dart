import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:url_launcher/url_launcher.dart';

import '../models/article.dart';
import '../providers/article_provider.dart';

class TopicAnalysisScreen extends ConsumerStatefulWidget {
  const TopicAnalysisScreen({super.key});

  @override
  ConsumerState<TopicAnalysisScreen> createState() => _TopicAnalysisScreenState();
}

class _TopicAnalysisScreenState extends ConsumerState<TopicAnalysisScreen> {
  final TextEditingController _topicController = TextEditingController();
  final TextEditingController _viewController = TextEditingController();
  double _biasValue = 0.5;
  bool _isSearching = false;

  @override
  void dispose() {
    _topicController.dispose();
    _viewController.dispose();
    super.dispose();
  }

  void _performSearch() async {
    if (_topicController.text.trim().isEmpty) return;

    final query = _topicController.text.trim();
    final view = _viewController.text.trim();
    
    // Combine topic and view for search
    final searchQuery = view.isNotEmpty ? '$query $view' : query;
    
    print('🔍 SEARCHING: Topic="$query", View="$view", Combined="$searchQuery", Bias=$_biasValue');
    print('🔍 SEARCHING: Raw query being sent to backend: "$searchQuery"');
    
    setState(() {
      _isSearching = true;
    });

    try {
      await ref.read(articleSearchNotifierProvider.notifier).searchArticles(
        searchQuery,
        _biasValue,
      );
      
      // Log the results
      final articles = ref.read(articleSearchNotifierProvider).value;
      if (articles != null) {
        print('📰 ARTICLES RETURNED (${articles.length}):');
        print('📰 RAW BACKEND RESPONSE ANALYSIS:');
        print('📰 ==========================================');
        for (int i = 0; i < articles.length; i++) {
          final article = articles[i];
          print('${i + 1}. "${article.title}"');
          print('   Source: ${article.source.name}');
          print('   URL: ${article.url}');
          print('   Description: ${article.description}');
          if (article.biasAnalysis != null) {
            print('   Bias Analysis:');
            print('     - Stance: ${article.biasAnalysis!.stance}');
            print('     - Confidence: ${article.biasAnalysis!.stanceConfidence}');
            print('     - Method: ${article.biasAnalysis!.stanceMethod}');
            print('     - Evidence: ${article.biasAnalysis!.stanceEvidence}');
            print('     - User Belief: ${article.biasAnalysis!.userBelief}');
            print('     - Bias Match: ${article.biasAnalysis!.biasMatch}');
            print('     - User Bias Preference: ${article.biasAnalysis!.userBiasPreference}');
            print('     - Topic Sentiment Score: ${article.biasAnalysis!.topicSentimentScore}');
            print('     - Topic Sentiment: ${article.biasAnalysis!.topicSentiment}');
            print('     - Topic Mentions: ${article.biasAnalysis!.topicMentions}');
          }
          print('   Relevance Check:');
          print('     - Contains "Palestine": ${article.title.toLowerCase().contains('palestine') || article.description.toLowerCase().contains('palestine')}');
          print('     - Contains "Israel": ${article.title.toLowerCase().contains('israel') || article.description.toLowerCase().contains('israel')}');
          print('     - Contains "occupation": ${article.title.toLowerCase().contains('occupation') || article.description.toLowerCase().contains('occupation')}');
          print('     - Contains user view keywords: ${_containsUserViewKeywords(article, view)}');
          print('   Bias Match Score: ${(article.biasAnalysis?.biasMatch ?? 0.0) * 100}%');
          print('   Stance: ${article.biasAnalysis?.stance ?? 'none'}');
          print('');
        }
        
        print('📰 ==========================================');
        print('📰 SUMMARY:');
        print('  - Total articles: ${articles.length}');
        print('  - Articles with bias analysis: ${articles.where((a) => a.biasAnalysis != null).length}');
        print('  - Average bias match: ${articles.where((a) => a.biasAnalysis != null).map((a) => a.biasAnalysis!.biasMatch).fold(0.0, (sum, match) => sum + match) / articles.where((a) => a.biasAnalysis != null).length}');
        print('  - Stance distribution:');
        final stanceCounts = <String, int>{};
        for (final article in articles) {
          if (article.biasAnalysis != null) {
            stanceCounts[article.biasAnalysis!.stance] = (stanceCounts[article.biasAnalysis!.stance] ?? 0) + 1;
          }
        }
        stanceCounts.forEach((stance, count) {
          print('    - $stance: $count articles');
        });
      }
    } finally {
      setState(() {
        _isSearching = false;
      });
    }
  }

  bool _containsUserViewKeywords(Article article, String userView) {
    if (userView.isEmpty) return true;
    final keywords = userView.toLowerCase().split(' ');
    final text = '${article.title} ${article.description}'.toLowerCase();
    return keywords.any((keyword) => text.contains(keyword));
  }

  void _updateSearchWithBias() {
    if (_topicController.text.trim().isNotEmpty) {
      print('🔄 UPDATING SEARCH: Bias changed to $_biasValue');
      _performSearch();
    }
  }

  String _getBiasLabel(double value) {
    if (value < 0.3) return 'Prove me wrong';
    if (value < 0.7) return 'Balanced';
    return 'Prove me right';
  }

  String _getBiasDescription(double value) {
    if (value < 0.3) {
      return 'Show articles that challenge or oppose your view';
    } else if (value < 0.7) {
      return 'Show a balanced mix of supporting and challenging perspectives';
    } else {
      return 'Show articles that support or reinforce your view';
    }
  }

  Color _getBiasColor(double score) {
    if (score < 0.3) return Colors.red;
    if (score < 0.7) return Colors.orange;
    return Colors.green;
  }

  @override
  Widget build(BuildContext context) {
    final searchAsync = ref.watch(articleSearchNotifierProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Topic Analysis'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
      ),
      body: SingleChildScrollView(
        child: Column(
          children: [
            _buildSearchSection(),
            _buildBiasSliderSection(),
            _buildSearchResults(searchAsync),
          ],
        ),
      ),
    );
  }

  Widget _buildSearchSection() {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Card(
        elevation: 4,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(
                    Icons.search,
                    color: Theme.of(context).primaryColor,
                    size: 20,
                  ),
                  const SizedBox(width: 8),
                  const Text(
                    'Analyze Topic',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              // Topic input
              TextField(
                controller: _topicController,
                decoration: const InputDecoration(
                  labelText: 'What topic do you want to analyze?',
                  hintText: 'e.g., Trump, Palestine, Climate Change, Economy',
                  border: OutlineInputBorder(),
                ),
                onSubmitted: (_) => _performSearch(),
              ),
              const SizedBox(height: 16),
              // View input
              TextField(
                controller: _viewController,
                decoration: const InputDecoration(
                  labelText: 'What\'s your view on this topic? (optional)',
                  hintText: 'e.g., Trump is a great leader, Palestine deserves freedom',
                  border: OutlineInputBorder(),
                ),
                onSubmitted: (_) => _performSearch(),
              ),
              const SizedBox(height: 16),
              // Search button
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: _isSearching ? null : _performSearch,
                  icon: _isSearching 
                      ? const SizedBox(
                          width: 16,
                          height: 16,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Icon(Icons.search),
                  label: Text(_isSearching ? 'Analyzing...' : 'Analyze Topic'),
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 12),
                  ),
                ),
              ),
              const SizedBox(height: 16),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildBiasSliderSection() {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Card(
        elevation: 4,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(
                    Icons.psychology,
                    color: Theme.of(context).primaryColor,
                    size: 20,
                  ),
                  const SizedBox(width: 8),
                  const Text(
                    'Adjust Analysis Focus',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Text(
                'Your view: "${_viewController.text}"',
                style: const TextStyle(
                  fontSize: 14,
                  color: Colors.grey,
                  fontStyle: FontStyle.italic,
                ),
              ),
              const SizedBox(height: 16),
              
              // Bias slider
              Row(
                children: [
                  const Text(
                    'Prove me wrong',
                    style: TextStyle(fontSize: 12),
                  ),
                  Expanded(
                    child: Slider(
                      value: _biasValue,
                      onChanged: (value) {
                        setState(() {
                          _biasValue = value;
                        });
                      },
                      onChangeEnd: (value) {
                        // Only trigger search when user finishes sliding
                        _updateSearchWithBias();
                      },
                      divisions: 10,
                      label: _getBiasLabel(_biasValue),
                    ),
                  ),
                  const Text(
                    'Prove me right',
                    style: TextStyle(fontSize: 12),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Text(
                _getBiasDescription(_biasValue),
                style: const TextStyle(
                  fontSize: 14,
                  color: Colors.grey,
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSearchResults(AsyncValue<List<Article>?> searchAsync) {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.article,
                color: Theme.of(context).primaryColor,
                size: 20,
              ),
              const SizedBox(width: 8),
              const Text(
                'Analysis Results',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Container(
            height: 400, // Fixed height for the results section
            child: searchAsync.when(
              data: (articles) {
                if (articles == null) {
                  return const Center(
                    child: Text(
                      'Enter a topic and click "Analyze Topic" to get started.',
                      style: TextStyle(fontSize: 16, color: Colors.grey),
                    ),
                  );
                }
                
                if (articles.isEmpty) {
                  return const Center(
                    child: Text(
                      'No articles found for this topic and view combination.',
                      style: TextStyle(fontSize: 16, color: Colors.grey),
                    ),
                  );
                }
                
                return ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: articles.length,
                  itemBuilder: (context, index) {
                    final article = articles[index];
                    return Card(
                      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                      child: ListTile(
                        title: Text(
                          article.title,
                          style: const TextStyle(fontWeight: FontWeight.bold),
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        ),
                        subtitle: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              article.description,
                              maxLines: 3,
                              overflow: TextOverflow.ellipsis,
                            ),
                            const SizedBox(height: 8),
                            if (article.biasAnalysis != null) ...[
                              Wrap(
                                spacing: 8,
                                runSpacing: 4,
                                children: [
                                  Container(
                                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                    decoration: BoxDecoration(
                                      color: article.biasAnalysis!.sentimentColor,
                                      borderRadius: BorderRadius.circular(12),
                                    ),
                                    child: Text(
                                      article.biasAnalysis!.biasLabel,
                                      style: const TextStyle(
                                        color: Colors.white,
                                        fontSize: 12,
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                  ),
                                  Text(
                                    'Match: ${(article.biasAnalysis!.biasMatch * 100).toInt()}%',
                                    style: TextStyle(
                                      fontSize: 12,
                                      color: Colors.grey[600],
                                    ),
                                  ),
                                  Text(
                                    'Confidence: ${article.biasAnalysis!.confidenceLabel}',
                                    style: TextStyle(
                                      fontSize: 12,
                                      color: Colors.grey[600],
                                    ),
                                  ),
                                  Text(
                                    'Mentions: ${article.biasAnalysis!.topicMentions}',
                                    style: TextStyle(
                                      fontSize: 12,
                                      color: Colors.grey[600],
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 4),
                              Text(
                                'Source: ${article.source.name}',
                                style: TextStyle(
                                  fontSize: 12,
                                  color: Colors.grey[600],
                                ),
                              ),
                            ],
                          ],
                        ),
                        onTap: () {
                          // Open article URL
                          launchUrl(Uri.parse(article.url));
                        },
                      ),
                    );
                  },
                );
              },
              loading: () => const Center(
                child: CircularProgressIndicator(),
              ),
              error: (error, stack) => Center(
                child: Text(
                  'Error loading articles: $error',
                  style: const TextStyle(color: Colors.red),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
} 