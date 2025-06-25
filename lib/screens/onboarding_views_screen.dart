import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../models/user_views.dart';
import '../widgets/view_expression_widget.dart';
import '../providers/user_views_provider.dart';

class OnboardingViewsScreen extends ConsumerStatefulWidget {
  final Function(UserViewProfile)? onOnboardingComplete;

  const OnboardingViewsScreen({
    super.key,
    this.onOnboardingComplete,
  });

  @override
  ConsumerState<OnboardingViewsScreen> createState() => _OnboardingViewsScreenState();
}

class _OnboardingViewsScreenState extends ConsumerState<OnboardingViewsScreen> {
  int _currentStep = 0;
  final int _totalSteps = 8; // Number of popular issues to show

  @override
  void initState() {
    super.initState();
    
    // Initialize user profile if not already done
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final userProfile = ref.read(userViewProfileProvider);
      if (userProfile == null) {
        ref.read(userViewProfileProvider.notifier).initializeProfile('current_user');
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final userProfile = ref.watch(userViewProfileProvider);
    final popularIssues = ref.read(userViewProfileProvider.notifier).getPopularIssues();
    
    if (userProfile == null) {
      return const Scaffold(
        body: Center(
          child: CircularProgressIndicator(),
        ),
      );
    }
    
    if (_currentStep >= popularIssues.length) {
      return _buildCompletionScreen(userProfile);
    }

    final currentIssue = popularIssues[_currentStep];

    return Scaffold(
      appBar: AppBar(
        title: const Text('Express Your Views'),
        backgroundColor: Theme.of(context).primaryColor,
        foregroundColor: Colors.white,
        elevation: 0,
        automaticallyImplyLeading: false,
      ),
      body: Column(
        children: [
          // Progress header
          _buildProgressHeader(),
          
          // Issue content
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  // Welcome message for first step
                  if (_currentStep == 0) ...[
                    _buildWelcomeMessage(),
                    const SizedBox(height: 24),
                  ],
                  
                  // Current issue
                  _buildCurrentIssueCard(currentIssue),
                  const SizedBox(height: 24),
                  
                  // View expression widget
                  ViewExpressionWidget(
                    issue: currentIssue,
                    onViewChanged: (updatedIssue) {
                      ref.read(userViewProfileProvider.notifier).updateIssueView(updatedIssue);
                      _nextStep();
                    },
                    showConfidence: true,
                    showInterest: true,
                  ),
                ],
              ),
            ),
          ),
          
          // Navigation buttons
          _buildNavigationButtons(),
        ],
      ),
    );
  }

  Widget _buildProgressHeader() {
    final progress = (_currentStep / _totalSteps) * 100;
    
    return Container(
      padding: const EdgeInsets.all(16),
      color: Theme.of(context).primaryColor.withOpacity(0.1),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Step ${_currentStep + 1} of $_totalSteps',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                  color: Theme.of(context).primaryColor,
                ),
              ),
              Text(
                '${progress.round()}% Complete',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: Theme.of(context).primaryColor,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          LinearProgressIndicator(
            value: progress / 100,
            backgroundColor: Colors.grey[300],
            valueColor: AlwaysStoppedAnimation<Color>(
              progress >= 50 
                  ? Colors.green 
                  : progress >= 25 
                      ? Colors.orange 
                      : Colors.red,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildWelcomeMessage() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Theme.of(context).primaryColor.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: Theme.of(context).primaryColor.withOpacity(0.3),
        ),
      ),
      child: Column(
        children: [
          Icon(
            Icons.psychology,
            size: 48,
            color: Theme.of(context).primaryColor,
          ),
          const SizedBox(height: 16),
          Text(
            'Welcome to NewsNet!',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: Theme.of(context).primaryColor,
            ),
          ),
          const SizedBox(height: 12),
          const Text(
            'To personalize your news experience, we\'d like to understand your views on some key issues. This helps us show you stories that match your interests and perspectives.',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 16,
              color: Colors.grey,
            ),
          ),
          const SizedBox(height: 16),
          const Text(
            'Don\'t worry - you can always update these later, and your views are private.',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 14,
              fontStyle: FontStyle.italic,
              color: Colors.grey,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCurrentIssueCard(IssueView issue) {
    return Card(
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            // Category badge
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              decoration: BoxDecoration(
                color: Theme.of(context).primaryColor.withOpacity(0.1),
                borderRadius: BorderRadius.circular(20),
              ),
              child: Text(
                issue.categoryName,
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                  color: Theme.of(context).primaryColor,
                ),
              ),
            ),
            const SizedBox(height: 16),
            
            // Issue name
            Text(
              issue.issueName,
              style: const TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 12),
            
            // Description based on category
            Text(
              _getIssueDescription(issue),
              style: const TextStyle(
                fontSize: 16,
                color: Colors.grey,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildNavigationButtons() {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Row(
        children: [
          // Skip button
          Expanded(
            child: OutlinedButton(
              onPressed: _skipStep,
              style: OutlinedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 12),
                foregroundColor: Colors.grey,
              ),
              child: const Text('Skip'),
            ),
          ),
          const SizedBox(width: 16),
          
          // Next button
          Expanded(
            child: ElevatedButton(
              onPressed: _nextStep,
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 12),
                backgroundColor: Theme.of(context).primaryColor,
                foregroundColor: Colors.white,
              ),
              child: const Text('Next'),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCompletionScreen(UserViewProfile userProfile) {
    final completedIssues = userProfile.allIssuesWithViews.length;
    final totalIssues = userProfile.allActiveIssues.length;
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('Setup Complete!'),
        backgroundColor: Theme.of(context).primaryColor,
        foregroundColor: Colors.white,
        elevation: 0,
        automaticallyImplyLeading: false,
      ),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Success icon
            Container(
              width: 100,
              height: 100,
              decoration: BoxDecoration(
                color: Colors.green.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.check_circle,
                size: 60,
                color: Colors.green,
              ),
            ),
            const SizedBox(height: 32),
            
            // Success message
            const Text(
              'Great job!',
              style: TextStyle(
                fontSize: 28,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            
            Text(
              'You\'ve expressed your views on $completedIssues issues.',
              style: const TextStyle(
                fontSize: 18,
                color: Colors.grey,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),
            
            // Stats
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Colors.grey[100],
                borderRadius: BorderRadius.circular(12),
              ),
              child: Column(
                children: [
                  const Text(
                    'Your Profile Summary',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 16),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceAround,
                    children: [
                      _buildStatItem('Issues', completedIssues.toString()),
                      _buildStatItem('Categories', userProfile.categories.length.toString()),
                      _buildStatItem('Completion', '${((completedIssues / totalIssues) * 100).round()}%'),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 32),
            
            // Continue button
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () {
                  if (widget.onOnboardingComplete != null) {
                    widget.onOnboardingComplete!(userProfile);
                  } else {
                    // Navigate to home if no callback provided
                    context.go('/');
                  }
                },
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  backgroundColor: Theme.of(context).primaryColor,
                  foregroundColor: Colors.white,
                ),
                child: const Text(
                  'Continue to NewsNet',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ),
            const SizedBox(height: 16),
            
            // Edit profile option
            TextButton(
              onPressed: () {
                // Navigate to full profile editing
                // This would open the CategorySelectionScreen
              },
              child: const Text(
                'I want to add more views first',
                style: TextStyle(
                  fontSize: 16,
                  color: Colors.grey,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatItem(String label, String value) {
    return Column(
      children: [
        Text(
          value,
          style: const TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            color: Colors.green,
          ),
        ),
        Text(
          label,
          style: const TextStyle(
            fontSize: 14,
            color: Colors.grey,
          ),
        ),
      ],
    );
  }

  void _nextStep() {
    if (_currentStep < _totalSteps - 1) {
      setState(() {
        _currentStep++;
      });
    } else {
      // Onboarding is complete
      final userProfile = ref.read(userViewProfileProvider);
      if (userProfile != null) {
        if (widget.onOnboardingComplete != null) {
          widget.onOnboardingComplete!(userProfile);
        } else {
          // Navigate to home if no callback provided
          context.go('/');
        }
      }
    }
  }

  void _skipStep() {
    _nextStep();
  }

  String _getIssueDescription(IssueView issue) {
    switch (issue.categoryId) {
      case 'geopolitics':
        return 'Share your perspective on this important global issue.';
      case 'sports':
        return 'What\'s your take on this team or athlete?';
      case 'entertainment':
        return 'How do you feel about this entertainment topic?';
      case 'technology':
        return 'What\'s your opinion on this technological development?';
      case 'economics':
        return 'What\'s your view on this economic issue?';
      case 'social_issues':
        return 'Share your thoughts on this social matter.';
      default:
        return 'Express your view on this topic.';
    }
  }
} 