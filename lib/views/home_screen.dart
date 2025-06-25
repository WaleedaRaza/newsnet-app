import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../models/story.dart';
import '../providers/story_provider.dart';
import '../providers/auth_provider.dart';
import '../services/news_service.dart';
import '../widgets/story_card.dart';
import '../widgets/category_chip.dart';
import '../widgets/trending_topics.dart';
import '../widgets/search_bar.dart';
import '../core/utils.dart';

class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> {
  String _selectedCategory = 'geopolitics';
  final TextEditingController _searchController = TextEditingController();
  bool _isSearching = false;
  double _currentBiasValue = 0.5; // Track bias value locally
  bool _biasChanged = false; // Track if bias has been changed

  @override
  void initState() {
    super.initState();
    // Load initial stories
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(storiesNotifierProvider.notifier).refresh();
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final storiesAsync = ref.watch(storiesNotifierProvider);
    final searchAsync = ref.watch(searchNotifierProvider);
    final trendingTopicsAsync = ref.watch(trendingTopicsProvider);
    final userProfile = ref.watch(authNotifierProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'NewsNet',
          style: TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 24,
          ),
        ),
        actions: [
          // Bias indicator
          _buildBiasIndicator(context, userProfile.value),
          IconButton(
            icon: const Icon(Icons.person),
            onPressed: () {
              // Navigate to profile or show user menu
              _showUserMenu(context);
            },
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          await ref.read(storiesNotifierProvider.notifier).refresh();
        },
        child: SingleChildScrollView(
        child: Column(
          children: [
            // Search Bar
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: NewsSearchBar(
                controller: _searchController,
                onSearch: (query) {
                  setState(() {
                    _isSearching = query.isNotEmpty;
                  });
                  if (query.isNotEmpty) {
                    ref.read(searchNotifierProvider.notifier).search(query);
                  } else {
                    ref.read(searchNotifierProvider.notifier).clearSearch();
                  }
                },
              ),
            ),

              // MAIN BIAS SLIDER - Prominent on main feed above categories
              _buildMainBiasSlider(context, userProfile.value),
              const SizedBox(height: 16),

            // Categories
            if (!_isSearching) ...[
              SizedBox(
                height: 50,
                child: ListView.builder(
                  scrollDirection: Axis.horizontal,
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  itemCount: NewsService.categories.length,
                  itemBuilder: (context, index) {
                    final category = NewsService.categories[index];
                    return Padding(
                      padding: const EdgeInsets.only(right: 8),
                      child: CategoryChip(
                        label: _getCategoryDisplayName(category),
                        isSelected: _selectedCategory == category,
                        onTap: () {
                          setState(() {
                            _selectedCategory = category;
                          });
                          ref.read(storiesNotifierProvider.notifier)
                              .filterByTopics([category]);
                        },
                      ),
                    );
                  },
                ),
              ),
              const SizedBox(height: 16),

              // Trending Topics
              if (trendingTopicsAsync.hasValue) ...[
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  child: TrendingTopics(
                    topics: trendingTopicsAsync.value!,
                    onTopicTap: (topic) {
                      ref.read(storiesNotifierProvider.notifier)
                          .filterByTopics([topic]);
                    },
                  ),
                ),
                const SizedBox(height: 16),
              ],
            ],

            // Stories List
              _isSearching
                  ? _buildSearchResults(searchAsync)
                  : _buildStoriesList(storiesAsync),
            ],
            ),
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          // Navigate to view management
          context.push('/views');
        },
        icon: const Icon(Icons.psychology),
        label: const Text('Views'),
        backgroundColor: Theme.of(context).colorScheme.primary,
        foregroundColor: Colors.white,
      ),
    );
  }

  Widget _buildMainBiasSlider(BuildContext context, userProfile) {
    // Always show the bias slider, even if user profile is null
    final initialBias = userProfile?.biasSetting ?? 0.5;
    
    // Initialize local bias value if not set
    if (!_biasChanged) {
      _currentBiasValue = initialBias;
    }
    
    print('🎛️ BIAS SLIDER BEING BUILT - Current bias: $_currentBiasValue'); // Debug print
    
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      child: Card(
        elevation: 4,
        color: Theme.of(context).colorScheme.surface,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(
                    Icons.psychology,
                    color: Theme.of(context).colorScheme.primary,
                    size: 20,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      '🎛️ Adjust News Bias',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: Theme.of(context).colorScheme.primary,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Text(
                'Control how stories are presented to you',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Theme.of(context).colorScheme.onSurfaceVariant,
                ),
              ),
              const SizedBox(height: 16),
              
              // COMPACT BIAS SLIDER
              Container(
                height: 60,
                child: GestureDetector(
                  onPanUpdate: (details) {
                    final RenderBox renderBox = context.findRenderObject() as RenderBox;
                    final localPosition = renderBox.globalToLocal(details.globalPosition);
                    
                    // Calculate the actual slider area (excluding padding)
                    final containerWidth = MediaQuery.of(context).size.width - 64; // 32px margins on each side
                    final sliderAreaWidth = containerWidth - 32; // 16px padding on each side
                    final sliderStartX = 16; // Left padding
                    final sliderEndX = sliderStartX + sliderAreaWidth;
                    
                    // Calculate new value based on touch position within slider area
                    final touchX = localPosition.dx.clamp(sliderStartX, sliderEndX);
                    final newValue = ((touchX - sliderStartX) / sliderAreaWidth).clamp(0.0, 1.0);
                    
                    setState(() {
                      _currentBiasValue = newValue;
                      _biasChanged = true;
                    });
                    
                    print('🎛️ SLIDER MOVED TO: $_currentBiasValue (touchX: $touchX, sliderArea: $sliderStartX-$sliderEndX)'); // Debug print
                  },
                  child: Container(
                    height: 40,
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(20),
                      gradient: LinearGradient(
                        colors: [
                          Colors.red.shade300,
                          Colors.orange.shade300,
                          Colors.blue.shade300,
                          Colors.green.shade300,
                        ],
                        stops: const [0.0, 0.25, 0.75, 1.0],
                      ),
                    ),
                    child: Stack(
                      children: [
                        // Slider track
                        Container(
                          width: double.infinity,
                          height: 6,
                          margin: const EdgeInsets.symmetric(vertical: 17, horizontal: 12),
                          decoration: BoxDecoration(
                            borderRadius: BorderRadius.circular(3),
                            color: Colors.white.withOpacity(0.3),
                          ),
                        ),
                        // Slider thumb - properly constrained on both sides
                        Positioned(
                          left: 12 + (_currentBiasValue * (MediaQuery.of(context).size.width - 120)),
                          top: 8,
                          child: Container(
                            width: 24,
                            height: 24,
                            decoration: BoxDecoration(
                              color: _getBiasColor(_currentBiasValue),
                              shape: BoxShape.circle,
                              boxShadow: [
                                BoxShadow(
                                  color: Colors.black.withOpacity(0.2),
                                  blurRadius: 4,
                                  offset: const Offset(0, 2),
                                ),
                              ],
                            ),
                            child: Icon(
                              _getBiasIcon(_currentBiasValue),
                              color: Colors.white,
                              size: 12,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
              
              const SizedBox(height: 8),
              
              // Compact bias labels
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Challenge',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: Colors.red,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  Text(
                    'Prove Right',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: Colors.green,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
              
              const SizedBox(height: 12),
              
              // Compact current bias indicator
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: _getBiasColor(_currentBiasValue).withOpacity(0.1),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(
                    color: _getBiasColor(_currentBiasValue).withOpacity(0.3),
                  ),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      _getBiasIcon(_currentBiasValue),
                      size: 14,
                      color: _getBiasColor(_currentBiasValue),
                    ),
                    const SizedBox(width: 6),
                    Text(
                      '${_getBiasLabel(_currentBiasValue)} (${(_currentBiasValue * 100).toInt()}%)',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: _getBiasColor(_currentBiasValue),
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
              ),
              
              const SizedBox(height: 12),
              
              // SHOW STORIES BUTTON
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _biasChanged ? () {
                    print('🎛️ SHOW STORIES BUTTON PRESSED - Bias: $_currentBiasValue');
                    // TODO: Implement story fetching with bias
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text('Stories will be fetched with bias: ${_getBiasLabel(_currentBiasValue)}'),
                        backgroundColor: _getBiasColor(_currentBiasValue),
                      ),
                    );
                  } : null,
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 12),
                    backgroundColor: _biasChanged ? _getBiasColor(_currentBiasValue) : Colors.grey,
                  ),
                  child: Text(
                    _biasChanged ? '🎯 Show Stories' : 'Move slider to enable',
                    style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildBiasIndicator(BuildContext context, userProfile) {
    if (userProfile == null) return const SizedBox.shrink();
    
    final biasSetting = userProfile.biasSetting ?? 0.5;
    final biasLabel = AppUtils.getBiasLabel(biasSetting);
    final biasColor = AppUtils.getBiasColor(biasSetting);
    
    return GestureDetector(
      onTap: () => context.push('/bias-settings'),
      child: Container(
        margin: const EdgeInsets.only(right: 8),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(
          color: biasColor.withOpacity(0.1),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: biasColor.withOpacity(0.3),
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              _getBiasIcon(biasSetting),
              size: 16,
              color: biasColor,
            ),
            const SizedBox(width: 4),
            Text(
              biasLabel,
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w600,
                color: biasColor,
              ),
            ),
          ],
        ),
      ),
    );
  }

  IconData _getBiasIcon(double value) {
    if (value <= 0.25) return Icons.help_outline;
    if (value <= 0.5) return Icons.question_mark;
    if (value <= 0.75) return Icons.thumb_up_outlined;
    return Icons.verified;
  }

  Widget _buildStoriesList(AsyncValue<List<Story>> storiesAsync) {
    return storiesAsync.when(
      data: (stories) {
        if (stories.isEmpty) {
          return Container(
            height: 200,
            child: const Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  Icons.newspaper_outlined,
                  size: 64,
                  color: Colors.grey,
                ),
                SizedBox(height: 16),
                Text(
                  'No stories available',
                  style: TextStyle(
                    fontSize: 18,
                    color: Colors.grey,
                  ),
                ),
              ],
              ),
            ),
          );
        }

        return Column(
          children: [
            ...stories.map((story) => Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: StoryCard(
                story: story,
              ),
            )).toList(),
            // Load more button
            Padding(
                padding: const EdgeInsets.all(16),
                child: ElevatedButton(
                  onPressed: () {
                    ref.read(storiesNotifierProvider.notifier).loadMore();
                  },
                  child: const Text('Load More'),
                ),
            ),
          ],
        );
      },
      loading: () => Container(
        height: 200,
        child: const Center(child: CircularProgressIndicator()),
      ),
      error: (error, stack) => Container(
        height: 200,
        child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
              const Icon(Icons.error_outline, size: 64, color: Colors.red),
            const SizedBox(height: 16),
              Text('Error: $error'),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () {
                ref.read(storiesNotifierProvider.notifier).refresh();
              },
              child: const Text('Retry'),
            ),
          ],
          ),
        ),
      ),
    );
  }

  Widget _buildSearchResults(AsyncValue<List<Story>?> searchAsync) {
    return searchAsync.when(
      data: (stories) {
        if (stories == null || stories.isEmpty) {
          return Container(
            height: 200,
            child: const Center(
              child: Text('No search results found'),
            ),
          );
        }

        return Column(
          children: stories.map((story) => Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: StoryCard(
                story: story,
              ),
          )).toList(),
        );
      },
      loading: () => Container(
        height: 200,
        child: const Center(child: CircularProgressIndicator()),
      ),
      error: (error, stack) => Container(
        height: 200,
        child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
              const Icon(Icons.error_outline, size: 64, color: Colors.red),
            const SizedBox(height: 16),
              Text('Search error: $error'),
            ],
          ),
        ),
      ),
    );
  }

  String _getCategoryDisplayName(String category) {
    final displayNames = {
      'geopolitics': 'Geopolitics',
      'economics': 'Economics',
      'social_issues': 'Social Issues',
      'tech_science': 'Tech & Science',
      'health': 'Health',
      'sports': 'Sports',
    };
    return displayNames[category] ?? category;
  }

  void _showUserMenu(BuildContext context) {
    showModalBottomSheet(
      context: context,
      builder: (context) => Container(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
              ListTile(
              leading: const Icon(Icons.psychology),
              title: const Text('Express Your Views'),
              subtitle: const Text('Manage your views on issues'),
                onTap: () {
                  Navigator.pop(context);
                context.push('/views');
                },
              ),
              ListTile(
              leading: const Icon(Icons.article),
              title: const Text('Show Me Articles'),
              subtitle: const Text('Get personalized news articles'),
                onTap: () {
                  Navigator.pop(context);
                  context.push('/articles');
                },
              ),
              ListTile(
              leading: const Icon(Icons.settings),
                title: const Text('Bias Settings'),
                onTap: () {
                  Navigator.pop(context);
                  context.push('/bias-settings');
                },
              ),
              ListTile(
              leading: const Icon(Icons.person),
              title: const Text('Profile'),
                onTap: () {
                  Navigator.pop(context);
                context.push('/profile');
                },
              ),
            ListTile(
              leading: const Icon(Icons.logout),
              title: const Text('Logout'),
              onTap: () {
                Navigator.pop(context);
                ref.read(authNotifierProvider.notifier).signOut();
              },
            ),
          ],
        ),
      ),
    );
  }

  String _getBiasLabel(double bias) {
    if (bias <= 0.25) return 'Challenge';
    if (bias <= 0.5) return 'Question';
    if (bias <= 0.75) return 'Support';
    return 'Prove Right';
  }

  Color _getBiasColor(double value) {
    if (value <= 0.25) return Colors.red;
    if (value <= 0.5) return Colors.orange;
    if (value <= 0.75) return Colors.blue;
    return Colors.green;
  }
} 