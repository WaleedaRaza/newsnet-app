import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:url_launcher/url_launcher.dart';
import '../providers/article_provider.dart';
import '../providers/auth_provider.dart';
import '../models/article.dart';

class ArticlesScreen extends ConsumerStatefulWidget {
  const ArticlesScreen({super.key});

  @override
  ConsumerState<ArticlesScreen> createState() => _ArticlesScreenState();
}

class _ArticlesScreenState extends ConsumerState<ArticlesScreen> {
  final List<String> _selectedTopics = [];
  final Map<String, List<String>> _beliefs = {};
  double _biasLevel = 0.5;

  @override
  void initState() {
    super.initState();
    _loadUserBeliefs();
  }

  void _loadUserBeliefs() {
    final userProfileAsync = ref.read(authNotifierProvider);
    userProfileAsync.whenData((userProfile) {
      if (userProfile != null) {
        setState(() {
          _biasLevel = userProfile.biasSetting;
          // Convert user beliefs to the format expected by the API
          if (userProfile.beliefFingerprint != null) {
            for (final entry in userProfile.beliefFingerprint!.entries) {
              if (entry.value is List) {
                _beliefs[entry.key] = List<String>.from(entry.value);
              }
            }
          }
        });
      }
    });
  }

  void _aggregateArticles() {
    if (_selectedTopics.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select at least one topic')),
      );
      return;
    }

    ref.read(articleAggregationProvider.notifier).aggregateArticles(
      topics: _selectedTopics,
      beliefs: _beliefs,
      bias: _biasLevel,
    );
  }

  @override
  Widget build(BuildContext context) {
    final articleState = ref.watch(articleAggregationProvider);
    final userProfileAsync = ref.watch(authNotifierProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Show Me Articles'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
      ),
      body: userProfileAsync.when(
        data: (userProfile) => Column(
          children: [
            // Configuration Section
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.surface,
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.1),
                    blurRadius: 4,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Configure Your News Feed',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  const SizedBox(height: 16),
                  
                  // Topics Selection
                  Text(
                    'Select Topics',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 8,
                    children: [
                      'Israel-Palestine',
                      'Climate Change',
                      'US Politics',
                      'Technology',
                      'Healthcare',
                      'Economy',
                    ].map((topic) {
                      final isSelected = _selectedTopics.contains(topic);
                      return FilterChip(
                        label: Text(topic),
                        selected: isSelected,
                        onSelected: (selected) {
                          setState(() {
                            if (selected) {
                              _selectedTopics.add(topic);
                            } else {
                              _selectedTopics.remove(topic);
                            }
                          });
                        },
                      );
                    }).toList(),
                  ),
                  
                  const SizedBox(height: 16),
                  
                  // Bias Level Slider
                  Text(
                    'Bias Level: ${(_biasLevel * 100).round()}%',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  Slider(
                    value: _biasLevel,
                    min: 0.0,
                    max: 1.0,
                    divisions: 10,
                    label: '${(_biasLevel * 100).round()}%',
                    onChanged: (value) {
                      setState(() {
                        _biasLevel = value;
                      });
                    },
                  ),
                  
                  const SizedBox(height: 16),
                  
                  // Aggregate Button
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      onPressed: articleState.isLoading ? null : _aggregateArticles,
                      icon: articleState.isLoading
                          ? const SizedBox(
                              width: 16,
                              height: 16,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Icon(Icons.search),
                      label: Text(articleState.isLoading ? 'Aggregating...' : 'Show Me Articles'),
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 12),
                      ),
                    ),
                  ),
                ],
              ),
            ),
            
            // Results Section
            Expanded(
              child: articleState.isLoading
                  ? const Center(child: CircularProgressIndicator())
                  : articleState.error != null
                      ? _buildErrorWidget(articleState.error!)
                      : articleState.articles.isEmpty
                          ? _buildEmptyState()
                          : _buildArticlesList(articleState),
            ),
          ],
        ),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stack) => Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                Icons.error_outline,
                size: 64,
                color: Theme.of(context).colorScheme.error,
              ),
              const SizedBox(height: 16),
              Text(
                'Error Loading User Profile',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: 8),
              Text(
                error.toString(),
                style: Theme.of(context).textTheme.bodyMedium,
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildErrorWidget(String error) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.error_outline,
            size: 64,
            color: Theme.of(context).colorScheme.error,
          ),
          const SizedBox(height: 16),
          Text(
            'Error Loading Articles',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const SizedBox(height: 8),
          Text(
            error,
            style: Theme.of(context).textTheme.bodyMedium,
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 16),
          ElevatedButton(
            onPressed: _aggregateArticles,
            child: const Text('Try Again'),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.article_outlined,
            size: 64,
            color: Theme.of(context).colorScheme.outline,
          ),
          const SizedBox(height: 16),
          Text(
            'No Articles Yet',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const SizedBox(height: 8),
          Text(
            'Select topics and click "Show Me Articles" to get started',
            style: Theme.of(context).textTheme.bodyMedium,
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildArticlesList(ArticleAggregationState state) {
    return Column(
      children: [
        // Stats Header
        Container(
          padding: const EdgeInsets.all(16),
          color: Theme.of(context).colorScheme.surfaceVariant,
          child: Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '${state.totalArticles} Articles',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    Text(
                      'Topics: ${state.topicsCovered.join(", ")}',
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                  ],
                ),
              ),
              Text(
                '${state.aggregationTime.toStringAsFixed(2)}s',
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ],
          ),
        ),
        
        // Articles List
        Expanded(
          child: ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: state.articles.length,
            itemBuilder: (context, index) {
              final article = state.articles[index];
              return _buildArticleCard(article);
            },
          ),
        ),
      ],
    );
  }

  Widget _buildArticleCard(Article article) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Title and Source
            Row(
              children: [
                Expanded(
                  child: Text(
                    article.title,
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: Theme.of(context).colorScheme.primaryContainer,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    article.sourceName,
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ),
              ],
            ),
            
            const SizedBox(height: 8),
            
            // Content Preview
            Text(
              article.content.length > 200
                  ? '${article.content.substring(0, 200)}...'
                  : article.content,
              style: Theme.of(context).textTheme.bodyMedium,
              maxLines: 3,
              overflow: TextOverflow.ellipsis,
            ),
            
            const SizedBox(height: 12),
            
            // Metadata Row
            Row(
              children: [
                // Topics
                Expanded(
                  child: Wrap(
                    spacing: 4,
                    children: article.topics.take(3).map((topic) {
                      return Chip(
                        label: Text(
                          topic,
                          style: const TextStyle(fontSize: 10),
                        ),
                        padding: EdgeInsets.zero,
                        materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                      );
                    }).toList(),
                  ),
                ),
                
                // Scores
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Text(
                      'Score: ${(article.finalScore * 100).round()}%',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Text(
                      'Published: ${_formatDate(article.publishedAt)}',
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                  ],
                ),
              ],
            ),
            
            const SizedBox(height: 12),
            
            // Action Buttons
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () => _launchUrl(article.url),
                    icon: const Icon(Icons.open_in_new, size: 16),
                    label: const Text('Read Full Article'),
                  ),
                ),
                const SizedBox(width: 8),
                IconButton(
                  onPressed: () => _showArticleDetails(article),
                  icon: const Icon(Icons.info_outline),
                  tooltip: 'Article Details',
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  String _formatDate(DateTime date) {
    final now = DateTime.now();
    final difference = now.difference(date);
    
    if (difference.inDays == 0) {
      return 'Today';
    } else if (difference.inDays == 1) {
      return 'Yesterday';
    } else if (difference.inDays < 7) {
      return '${difference.inDays} days ago';
    } else {
      return '${date.day}/${date.month}/${date.year}';
    }
  }

  Future<void> _launchUrl(String url) async {
    final uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    } else {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Could not open: $url')),
        );
      }
    }
  }

  void _showArticleDetails(Article article) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Article Details'),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text('Title: ${article.title}'),
              const SizedBox(height: 8),
              Text('Source: ${article.sourceName} (${article.sourceDomain})'),
              if (article.sourceBias != null) ...[
                const SizedBox(height: 8),
                Text('Bias: ${article.sourceBias}'),
              ],
              const SizedBox(height: 8),
              Text('Reliability: ${(article.sourceReliability * 100).round()}%'),
              const SizedBox(height: 8),
              Text('Topics: ${article.topics.join(", ")}'),
              const SizedBox(height: 8),
              Text('Topical Score: ${(article.topicalScore * 100).round()}%'),
              Text('Belief Alignment: ${(article.beliefAlignmentScore * 100).round()}%'),
              Text('Ideological Score: ${(article.ideologicalScore * 100).round()}%'),
              Text('Final Score: ${(article.finalScore * 100).round()}%'),
              const SizedBox(height: 8),
              Text('Published: ${article.publishedAt.toString()}'),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }
} 