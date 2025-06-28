import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:url_launcher/url_launcher.dart';
import '../providers/article_provider.dart';
import '../providers/auth_provider.dart';
import '../models/article.dart';
import '../services/api_service.dart';

class ArticlesScreen extends ConsumerStatefulWidget {
  const ArticlesScreen({super.key});

  @override
  ConsumerState<ArticlesScreen> createState() => _ArticlesScreenState();
}

class _ArticlesScreenState extends ConsumerState<ArticlesScreen> {
  final List<String> _selectedCategories = [];
  double _biasLevel = 0.5;
  final TextEditingController _searchController = TextEditingController();
  bool _showUniversalSearch = false;

  @override
  void initState() {
    super.initState();
    _loadUserPreferences();
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  void _loadUserPreferences() {
    final userProfileAsync = ref.read(authNotifierProvider);
    userProfileAsync.whenData((userProfile) {
      if (userProfile != null) {
        setState(() {
          _biasLevel = userProfile.biasSetting;
        });
      }
    });
  }

  void _aggregateArticles() {
    if (_selectedCategories.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select at least one category')),
      );
      return;
    }

    // For now, use the public endpoint (no auth required)
    ref.read(articleAggregationProvider.notifier).aggregateArticlesByCategoryPublic(
      categories: _selectedCategories,
      bias: _biasLevel,
      limitPerCategory: 10,
    );
  }

  void _performUniversalSearch() {
    final query = _searchController.text.trim();
    if (query.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter a search query')),
      );
      return;
    }

    print('🔍 ARTICLES SCREEN: Performing universal search for: "$query"');
    ref.read(articleProvider.notifier).searchArticles(query, _biasLevel);
  }

  void _loadMockArticles() {
    ref.read(articleAggregationProvider.notifier).getMockArticles();
  }

  @override
  Widget build(BuildContext context) {
    final articleState = ref.watch(articleAggregationProvider);
    final universalArticleState = ref.watch(articleProvider);
    final userProfileAsync = ref.watch(authNotifierProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('NewsNet Articles'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        actions: [
          IconButton(
            icon: Icon(_showUniversalSearch ? Icons.category : Icons.search),
            onPressed: () {
              setState(() {
                _showUniversalSearch = !_showUniversalSearch;
                if (!_showUniversalSearch) {
                  _searchController.clear();
                }
              });
            },
            tooltip: _showUniversalSearch ? 'Category Search' : 'Universal Search',
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadMockArticles,
            tooltip: 'Load Mock Articles',
          ),
        ],
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
                    _showUniversalSearch ? 'Universal Search' : 'Configure Your News Feed',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  const SizedBox(height: 16),
                  
                  if (_showUniversalSearch) ...[
                    // Universal Search Section
                    Text(
                      'Search ANY Topic',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const SizedBox(height: 8),
                    TextField(
                      controller: _searchController,
                      decoration: InputDecoration(
                        hintText: 'e.g., "Climate change I believe it\'s a serious threat"',
                        border: const OutlineInputBorder(),
                        suffixIcon: IconButton(
                          icon: const Icon(Icons.search),
                          onPressed: _performUniversalSearch,
                        ),
                      ),
                      onSubmitted: (_) => _performUniversalSearch(),
                    ),
                    const SizedBox(height: 8),
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: Colors.green.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Row(
                        children: [
                          Icon(Icons.lightbulb_outline, size: 16, color: Colors.green[700]),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              'Tip: Include your view in the search (e.g., "AI I love artificial intelligence")',
                              style: TextStyle(
                                fontSize: 12,
                                color: Colors.green[700],
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ] else ...[
                    // Categories Selection
                    Text(
                      'Select Categories',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const SizedBox(height: 8),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: ApiService.categories.map((category) {
                        final isSelected = _selectedCategories.contains(category);
                        return FilterChip(
                          label: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Text(ApiService.getCategoryIcon(category)),
                              const SizedBox(width: 4),
                              Text(ApiService.getCategoryDisplayName(category)),
                            ],
                          ),
                          selected: isSelected,
                          onSelected: (selected) {
                            setState(() {
                              if (selected) {
                                _selectedCategories.add(category);
                              } else {
                                _selectedCategories.remove(category);
                              }
                            });
                          },
                        );
                      }).toList(),
                    ),
                  ],
                  
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
                  
                  // Bias explanation
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: Colors.blue.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Row(
                      children: [
                        Icon(Icons.info_outline, size: 16, color: Colors.blue[700]),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            _getBiasExplanation(_biasLevel),
                            style: TextStyle(
                              fontSize: 12,
                              color: Colors.blue[700],
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                  
                  const SizedBox(height: 16),
                  
                  // Search/Aggregate Button
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      onPressed: (_showUniversalSearch ? universalArticleState.isLoading : articleState.isLoading) 
                          ? null 
                          : (_showUniversalSearch ? _performUniversalSearch : _aggregateArticles),
                      icon: (_showUniversalSearch ? universalArticleState.isLoading : articleState.isLoading)
                          ? const SizedBox(
                              width: 16,
                              height: 16,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : Icon(_showUniversalSearch ? Icons.search : Icons.search),
                      label: Text(_showUniversalSearch 
                          ? (universalArticleState.isLoading ? 'Searching...' : 'Search Articles')
                          : (articleState.isLoading ? 'Aggregating...' : 'Show Me Articles')),
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
              child: _showUniversalSearch 
                  ? _buildUniversalSearchResults(universalArticleState)
                  : _buildCategorySearchResults(articleState),
            ),
          ],
        ),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stack) => Center(
          child: Text('Error loading user profile: $error'),
        ),
      ),
    );
  }

  Widget _buildUniversalSearchResults(AsyncValue<List<Article>> articleState) {
    return articleState.when(
      data: (articles) {
        if (articles.isEmpty) {
          return const Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.search, size: 64, color: Colors.grey),
                SizedBox(height: 16),
                Text(
                  'Search for any topic to see articles',
                  style: TextStyle(fontSize: 18, color: Colors.grey),
                ),
                SizedBox(height: 8),
                Text(
                  'Try: "Climate change I believe it\'s a serious threat"',
                  style: TextStyle(fontSize: 14, color: Colors.grey),
                ),
              ],
            ),
          );
        }

        return ListView.builder(
          padding: const EdgeInsets.all(16),
          itemCount: articles.length,
          itemBuilder: (context, index) {
            final article = articles[index];
            return _buildArticleCard(article, index);
          },
        );
      },
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (error, stack) => Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error, size: 64, color: Colors.red),
            const SizedBox(height: 16),
            Text('Error: $error'),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () {
                if (_searchController.text.isNotEmpty) {
                  _performUniversalSearch();
                }
              },
              child: const Text('Try Again'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCategorySearchResults(ArticleAggregationState articleState) {
    if (articleState.isLoading) {
      return const Center(child: CircularProgressIndicator());
    }
    
    if (articleState.error != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error, size: 64, color: Colors.red),
            const SizedBox(height: 16),
            Text('Error: ${articleState.error}'),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _aggregateArticles,
              child: const Text('Try Again'),
            ),
          ],
        ),
      );
    }
    
    if (articleState.articles.isEmpty) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.article, size: 64, color: Colors.grey),
            const SizedBox(height: 16),
            Text(
              'Select categories and click "Show Me Articles"',
              style: TextStyle(fontSize: 18, color: Colors.grey),
            ),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: articleState.articles.length,
      itemBuilder: (context, index) {
        final article = articleState.articles[index];
        return _buildArticleCard(article, index);
      },
    );
  }

  Widget _buildArticleCard(Article article, int index) {
    final biasAnalysis = article.biasAnalysis;
    
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (article.urlToImage != null && article.urlToImage!.isNotEmpty)
            ClipRRect(
              borderRadius: const BorderRadius.vertical(top: Radius.circular(12)),
              child: Image.network(
                article.urlToImage!,
                height: 200,
                width: double.infinity,
                fit: BoxFit.cover,
                errorBuilder: (context, error, stackTrace) => Container(
                  height: 200,
                  color: Colors.grey[300],
                  child: const Icon(Icons.image, size: 64, color: Colors.grey),
                ),
              ),
            ),
          
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
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
                    if (biasAnalysis != null) ...[
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: _getStanceColor(biasAnalysis.stance).withOpacity(0.2),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Text(
                          biasAnalysis.stance.toUpperCase(),
                          style: TextStyle(
                            fontSize: 10,
                            fontWeight: FontWeight.bold,
                            color: _getStanceColor(biasAnalysis.stance),
                          ),
                        ),
                      ),
                    ],
                  ],
                ),
                
                const SizedBox(height: 8),
                
                Text(
                  article.description ?? 'No description available',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Colors.grey[600],
                  ),
                ),
                
                const SizedBox(height: 12),
                
                Row(
                  children: [
                    Icon(Icons.source, size: 16, color: Colors.grey[600]),
                    const SizedBox(width: 4),
                    Text(
                      article.sourceName,
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey[600],
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    const Spacer(),
                    if (article.publishedAt != null) ...[
                      Icon(Icons.schedule, size: 16, color: Colors.grey[600]),
                      const SizedBox(width: 4),
                      Text(
                        _formatDate(article.publishedAt!),
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey[600],
                        ),
                      ),
                    ],
                  ],
                ),
                
                if (biasAnalysis != null) ...[
                  const SizedBox(height: 12),
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: Colors.blue.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Analysis',
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                            color: Colors.blue[700],
                          ),
                        ),
                        const SizedBox(height: 4),
                        Row(
                          children: [
                            Expanded(
                              child: Text(
                                'Bias Match: ${(biasAnalysis.biasMatch * 100).toStringAsFixed(1)}%',
                                style: TextStyle(fontSize: 11, color: Colors.blue[700]),
                              ),
                            ),
                            if (biasAnalysis.relevanceScore != null)
                              Expanded(
                                child: Text(
                                  'Relevance: ${(biasAnalysis.relevanceScore! * 100).toStringAsFixed(1)}%',
                                  style: TextStyle(fontSize: 11, color: Colors.blue[700]),
                                ),
                              ),
                            if (biasAnalysis.finalScore != null)
                              Expanded(
                                child: Text(
                                  'Final Score: ${(biasAnalysis.finalScore! * 100).toStringAsFixed(1)}%',
                                  style: TextStyle(fontSize: 11, color: Colors.blue[700]),
                                ),
                              ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ],
                
                const SizedBox(height: 12),
                
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: () => _launchUrl(article.url),
                    child: const Text('Read Article'),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Color _getStanceColor(String stance) {
    switch (stance.toLowerCase()) {
      case 'support':
        return Colors.green;
      case 'oppose':
        return Colors.red;
      case 'neutral':
        return Colors.orange;
      default:
        return Colors.grey;
    }
  }

  String _formatDate(String dateString) {
    try {
      final date = DateTime.parse(dateString);
      final now = DateTime.now();
      final difference = now.difference(date);
      
      if (difference.inDays == 0) {
        return 'Today';
      } else if (difference.inDays == 1) {
        return 'Yesterday';
      } else if (difference.inDays < 7) {
        return '${difference.inDays} days ago';
      } else {
        return '${date.month}/${date.day}/${date.year}';
      }
    } catch (e) {
      return dateString;
    }
  }

  String _getBiasExplanation(double bias) {
    if (bias >= 0.8) {
      return 'Strong preference for articles that support your views';
    } else if (bias >= 0.6) {
      return 'Moderate preference for articles that support your views';
    } else if (bias >= 0.4) {
      return 'Balanced mix of supporting and challenging views';
    } else if (bias >= 0.2) {
      return 'Moderate preference for articles that challenge your views';
    } else {
      return 'Strong preference for articles that challenge your views';
    }
  }

  Future<void> _launchUrl(String url) async {
    if (await canLaunchUrl(Uri.parse(url))) {
      await launchUrl(Uri.parse(url));
    } else {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Could not launch $url')),
        );
      }
    }
  }
} 