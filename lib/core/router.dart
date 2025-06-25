import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../providers/auth_provider.dart';
import '../providers/user_provider.dart';
import '../views/home_screen.dart';
import '../views/auth_screen.dart';
import '../views/story_screen.dart';
import '../views/chat_screen.dart';
import '../views/test_stories_screen.dart';
import '../views/debug_screen.dart';
import '../views/article_detail_screen.dart';
import '../views/onboarding/belief_form.dart';
import '../screens/onboarding_views_screen.dart';
import '../screens/category_selection_screen.dart';
import '../screens/articles_screen.dart';
import '../widgets/bias_slider.dart';
import '../core/constants.dart';

final routerProvider = Provider<GoRouter>((ref) {
  final authState = ref.watch(firebaseAuthProvider);

  return GoRouter(
    initialLocation: '/',
    redirect: (context, state) {
      final isAuthenticated = authState.value != null;
      final isAuthRoute = state.matchedLocation == '/auth';
      final isOnboardingRoute = state.matchedLocation == '/onboarding';
      final isViewsOnboardingRoute = state.matchedLocation == '/onboarding-views';

      // If not authenticated and not on auth route, redirect to auth
      if (!isAuthenticated && !isAuthRoute && !isOnboardingRoute && !isViewsOnboardingRoute) {
        return '/auth';
      }

      // If authenticated and on auth route, redirect to home
      if (isAuthenticated && isAuthRoute) {
        return '/';
      }

      return null;
    },
    routes: [
      GoRoute(
        path: '/',
        builder: (context, state) => const HomeScreen(),
      ),
      GoRoute(
        path: '/auth',
        builder: (context, state) => const AuthScreen(),
      ),
      GoRoute(
        path: '/onboarding',
        builder: (context, state) => const BeliefForm(),
      ),
      GoRoute(
        path: '/onboarding-views',
        builder: (context, state) => const OnboardingViewsScreen(),
      ),
      GoRoute(
        path: '/views',
        builder: (context, state) => const CategorySelectionScreen(),
      ),
      GoRoute(
        path: '/story/:id',
        builder: (context, state) {
          final storyId = state.pathParameters['id']!;
          return StoryScreen(storyId: storyId);
        },
      ),
      GoRoute(
        path: '/article/:id',
        builder: (context, state) {
          final storyId = state.pathParameters['id']!;
          return ArticleDetailScreen(storyId: storyId);
        },
      ),
      GoRoute(
        path: '/chat/:storyId',
        builder: (context, state) {
          final storyId = state.pathParameters['storyId']!;
          return ChatScreen(storyId: storyId);
        },
      ),
      GoRoute(
        path: '/bias-settings',
        builder: (context, state) => const BiasSettingsScreen(),
      ),
      GoRoute(
        path: '/profile',
        builder: (context, state) => const ProfileScreen(),
      ),
      GoRoute(
        path: '/interests',
        builder: (context, state) => const InterestsScreen(),
      ),
      GoRoute(
        path: '/articles',
        builder: (context, state) => const ArticlesScreen(),
      ),
      GoRoute(
        path: '/test-stories',
        builder: (context, state) => const TestStoriesScreen(),
      ),
      GoRoute(
        path: '/debug',
        builder: (context, state) => const DebugScreen(),
      ),
    ],
  );
});

// Proper Bias Settings Screen
class BiasSettingsScreen extends ConsumerStatefulWidget {
  const BiasSettingsScreen({super.key});

  @override
  ConsumerState<BiasSettingsScreen> createState() => _BiasSettingsScreenState();
}

class _BiasSettingsScreenState extends ConsumerState<BiasSettingsScreen> {
  double _biasSetting = 0.5;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    // Load current user's bias setting
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final user = ref.read(authNotifierProvider).value;
      if (user != null) {
        setState(() {
          _biasSetting = user.biasSetting ?? 0.5;
        });
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('Bias Settings'),
        actions: [
          if (_isLoading)
            const Padding(
              padding: EdgeInsets.all(16.0),
              child: SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(strokeWidth: 2),
              ),
            ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(AppConstants.defaultPadding),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Icon(
              Icons.psychology,
              size: 48,
              color: theme.colorScheme.primary,
            ),
            const SizedBox(height: 16),
            Text(
              'Adjust Your News Bias',
              style: theme.textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Control how news narratives are presented to you. Move the slider to adjust from challenging your views to supporting them.',
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 32),

            // Bias Slider
            BiasSliderCard(
              value: _biasSetting,
              onChanged: (value) {
                setState(() {
                  _biasSetting = value;
                });
              },
              title: 'Default Bias Setting',
              subtitle: 'This affects how all news stories are framed for you',
            ),
            
            const SizedBox(height: 24),

            // Bias Level Descriptions
            _buildBiasDescriptions(theme),
            
            const SizedBox(height: 32),

            // Save Button
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _isLoading ? null : _saveBiasSetting,
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
                child: const Text(
                  'Save Bias Setting',
                  style: TextStyle(fontSize: 16),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBiasDescriptions(ThemeData theme) {
    final descriptions = [
      {'range': '0.0 - 0.25', 'title': 'Challenge Me', 'desc': 'Presents counter-arguments and questions your assumptions'},
      {'range': '0.25 - 0.5', 'title': 'Question', 'desc': 'Raises questions and explores different angles'},
      {'range': '0.5', 'title': 'Neutral', 'desc': 'Balanced, factual presentation'},
      {'range': '0.5 - 0.75', 'title': 'Support', 'desc': 'Provides supporting evidence for your views'},
      {'range': '0.75 - 1.0', 'title': 'Prove Me Right', 'desc': 'Strongly supports and validates your perspectives'},
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Bias Level Guide',
          style: theme.textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 16),
        ...descriptions.map((desc) => Card(
          margin: const EdgeInsets.only(bottom: 8),
          child: Padding(
            padding: const EdgeInsets.all(12),
            child: Row(
              children: [
                Container(
                  width: 12,
                  height: 12,
                  decoration: BoxDecoration(
                    color: _getBiasColor(double.tryParse(desc['range']!.split(' - ').first) ?? 0.5),
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '${desc['title']} (${desc['range']})',
                        style: theme.textTheme.bodyMedium?.copyWith(
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      Text(
                        desc['desc']!,
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: theme.colorScheme.onSurfaceVariant,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        )).toList(),
      ],
    );
  }

  Color _getBiasColor(double value) {
    if (value <= 0.25) return Colors.red;
    if (value <= 0.5) return Colors.orange;
    if (value <= 0.75) return Colors.blue;
    return Colors.green;
  }

  Future<void> _saveBiasSetting() async {
    setState(() {
      _isLoading = true;
    });

    try {
      await ref.read(userNotifierProvider.notifier).updateBiasSetting(_biasSetting);
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Bias setting updated successfully!'),
            backgroundColor: Colors.green,
          ),
        );
        context.pop();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to update bias setting: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }
}

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Profile')),
      body: const Center(child: Text('Profile Screen')),
    );
  }
}

class InterestsScreen extends StatelessWidget {
  const InterestsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Interests')),
      body: const Center(child: Text('Interests Screen')),
    );
  }
} 