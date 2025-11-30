import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/article_provider.dart';
import '../widgets/bias_slider.dart';
import '../views/article_detail_screen.dart';
import '../models/article.dart';

class LangChainSearchScreen extends ConsumerStatefulWidget {
  const LangChainSearchScreen({super.key});

  @override
  ConsumerState<LangChainSearchScreen> createState() => _LangChainSearchScreenState();
}

class _LangChainSearchScreenState extends ConsumerState<LangChainSearchScreen> {
  final TextEditingController _searchController = TextEditingController();
  double _biasPreference = 0.5;
  bool _isSearching = false;
  Map<String, dynamic>? _analysis;

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _performSearch() async {
    if (_searchController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter a search query')),
      );
      return;
    }

    setState(() {
      _isSearching = true;
      _analysis = null;
    });

    try {
      final articleProvider = ref.read(articleProvider.notifier);
      await articleProvider.langchainSearch(
        _searchController.text.trim(),
        _biasPreference,
      );

      // Get analysis if available
      final articles = ref.read(articleProvider).value ?? [];
      if (articles.isNotEmpty) {
        try {
          final analysis = await articleProvider.langchainAnalyzeArticles(articles);
          setState(() {
            _analysis = analysis;
          });
        } catch (e) {
          print('Analysis failed: $e');
        }
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Search failed: $e')),
      );
    } finally {
      setState(() {
        _isSearching = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final articleState = ref.watch(articleProvider);
    final articles = articleState.value ?? [];

    return Scaffold(
      appBar: AppBar(
        title: const Text('🧠 LangChain Search'),
        backgroundColor: Theme.of(context).colorScheme.primary,
        foregroundColor: Colors.white,
        elevation: 0,
      ),
      body: Column(
        children: [
          // Search Section
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Theme.of(context).colorScheme.primary,
              borderRadius: const BorderRadius.only(
                bottomLeft: Radius.circular(20),
                bottomRight: Radius.circular(20),
              ),
            ),
            child: Column(
              children: [
                // Search Bar
                TextField(
                  controller: _searchController,
                  decoration: InputDecoration(
                    hintText: 'Enter any topic or query...',
                    hintStyle: TextStyle(color: Colors.grey[300]),
                    filled: true,
                    fillColor: Colors.white,
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: BorderSide.none,
                    ),
                    prefixIcon: const Icon(Icons.search, color: Colors.grey),
                    suffixIcon: _isSearching
                        ? const Padding(
                            padding: EdgeInsets.all(12),
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : IconButton(
                            icon: const Icon(Icons.send, color: Colors.grey),
                            onPressed: _performSearch,
                          ),
                  ),
                  onSubmitted: (_) => _performSearch(),
                ),
                const SizedBox(height: 16),
                
                // Bias Slider
                BiasSlider(
                  value: _biasPreference,
                  onChanged: (value) {
                    setState(() {
                      _biasPreference = value;
                    });
                  },
                ),
                
                // Search Tips
                Container(
                  margin: const EdgeInsets.only(top: 12),
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.lightbulb_outline, color: Colors.white, size: 20),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          'Try queries like "climate change", "AI regulation", or "economic policy"',
                          style: TextStyle(color: Colors.white[200], fontSize: 12),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          // Results Section
          Expanded(
            child: articleState.when(
              data: (articles) => _buildResults(articles),
              loading: () => const Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    CircularProgressIndicator(),
                    SizedBox(height: 16),
                    Text('Searching with LangChain...'),
                    SizedBox(height: 8),
                    Text(
                      'Analyzing articles with AI-powered intelligence',
                      style: TextStyle(color: Colors.grey, fontSize: 12),
                    ),
                  ],
                ),
              ),
              error: (error, stack) => Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(Icons.error_outline, size: 64, color: Colors.red),
                    const SizedBox(height: 16),
                    Text('Search failed: $error'),
                    const SizedBox(height: 16),
                    ElevatedButton(
                      onPressed: _performSearch,
                      child: const Text('Try Again'),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildResults(List<Article> articles) {
    if (articles.isEmpty) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.search, size: 64, color: Colors.grey),
            SizedBox(height: 16),
            Text('No articles found'),
            SizedBox(height: 8),
            Text(
              'Try a different search query or adjust your bias preference',
              style: TextStyle(color: Colors.grey, fontSize: 12),
            ),
          ],
        ),
      );
    }

    return Column(
      children: [
        // Analysis Section
        if (_analysis != null) _buildAnalysisSection(),
        
        // Articles List
        Expanded(
          child: ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: articles.length,
            itemBuilder: (context, index) {
              final article = articles[index];
              return _buildArticleCard(article);
            },
          ),
        ),
      ],
    );
  }

  Widget _buildAnalysisSection() {
    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.blue[50],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.blue[200]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.psychology, color: Colors.blue),
              const SizedBox(width: 8),
              const Text(
                'AI Analysis',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Colors.blue,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          
          if (_analysis!['narrative_synthesis'] != null) ...[
            const Text(
              'Narrative Synthesis:',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 4),
            Text(_analysis!['narrative_synthesis']),
            const SizedBox(height: 12),
          ],
          
          if (_analysis!['stance_distribution'] != null) ...[
            const Text(
              'Stance Distribution:',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 4),
            Text(_analysis!['stance_distribution'].toString()),
            const SizedBox(height: 12),
          ],
          
          if (_analysis!['bias_analysis'] != null) ...[
            const Text(
              'Bias Analysis:',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 4),
            Text(_analysis!['bias_analysis']),
          ],
        ],
      ),
    );
  }

  Widget _buildArticleCard(Article article) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      elevation: 2,
      child: InkWell(
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => ArticleDetailScreen(article: article),
            ),
          );
        },
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Title
              Text(
                article.title,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 8),
              
              // Description
              if (article.description.isNotEmpty) ...[
                Text(
                  article.description,
                  style: TextStyle(
                    color: Colors.grey[600],
                    fontSize: 14,
                  ),
                  maxLines: 3,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 8),
              ],
              
              // Metadata Row
              Row(
                children: [
                  // Source
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: Colors.grey[200],
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      article.sourceName,
                      style: const TextStyle(fontSize: 12),
                    ),
                  ),
                  const SizedBox(width: 8),
                  
                  // API Source
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: Colors.blue[100],
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      article.apiSource,
                      style: TextStyle(fontSize: 12, color: Colors.blue[700]),
                    ),
                  ),
                  const Spacer(),
                  
                  // Date
                  Text(
                    article.formattedDate,
                    style: TextStyle(
                      color: Colors.grey[500],
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              
              // Scores Row
              if (article.biasAnalysis != null) ...[
                Row(
                  children: [
                    _buildScoreChip('Stance', article.stance, _getStanceColor(article.stance)),
                    const SizedBox(width: 8),
                    _buildScoreChip('Confidence', '${(article.confidence * 100).toInt()}%', Colors.orange),
                    const SizedBox(width: 8),
                    _buildScoreChip('Relevance', '${(article.relevanceScore * 100).toInt()}%', Colors.green),
                    const Spacer(),
                    _buildScoreChip('Final Score', '${(article.finalScore * 100).toInt()}%', Colors.purple),
                  ],
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildScoreChip(String label, String value, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Text(
        '$label: $value',
        style: TextStyle(
          fontSize: 10,
          color: color,
          fontWeight: FontWeight.w500,
        ),
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
        return Colors.grey;
      default:
        return Colors.blue;
    }
  }
} 