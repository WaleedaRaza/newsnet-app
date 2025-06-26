import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/user_views.dart';
import '../services/view_categories_service.dart';

// Provider for the view categories service
final viewCategoriesServiceProvider = Provider<ViewCategoriesService>((ref) {
  return ViewCategoriesService();
});

// Provider for the user's view profile
final userViewProfileProvider = StateNotifierProvider<UserViewProfileNotifier, UserViewProfile?>((ref) {
  final categoriesService = ref.watch(viewCategoriesServiceProvider);
  return UserViewProfileNotifier(categoriesService);
});

// State notifier for managing user view profile
class UserViewProfileNotifier extends StateNotifier<UserViewProfile?> {
  final ViewCategoriesService _categoriesService;

  UserViewProfileNotifier(this._categoriesService) : super(null);

  // Initialize user profile with predefined categories
  void initializeProfile(String userId) {
    if (state == null) {
      state = UserViewProfile(
        userId: userId,
        categories: _categoriesService.getPredefinedCategories(),
        createdAt: DateTime.now(),
      );
    }
  }

  // Update a specific issue view
  void updateIssueView(IssueView updatedIssue) {
    if (state == null) return;

    final updatedCategories = state!.categories.map((category) {
      if (category.categoryId == updatedIssue.categoryId) {
        final updatedIssues = category.issues.map((issue) {
          if (issue.issueId == updatedIssue.issueId) {
            return updatedIssue;
          }
          return issue;
        }).toList();
        return category.copyWith(issues: updatedIssues);
      }
      return category;
    }).toList();

    state = state!.copyWith(
      categories: updatedCategories,
      lastUpdated: DateTime.now(),
    );
  }

  // Clear a specific issue view
  void clearIssueView(String issueId) {
    if (state == null) return;

    final updatedCategories = state!.categories.map((category) {
      final updatedIssues = category.issues.map((issue) {
        if (issue.issueId == issueId) {
          return issue.copyWith(
            stanceValue: null,
            stanceLevel: null,
            confidenceLevel: null,
            interestLevel: null,
            lastUpdated: DateTime.now(),
          );
        }
        return issue;
      }).toList();
      return category.copyWith(issues: updatedIssues);
    }).toList();

    state = state!.copyWith(
      categories: updatedCategories,
      lastUpdated: DateTime.now(),
    );
  }

  // Get completion percentage
  double getCompletionPercentage() {
    if (state == null) return 0.0;
    return state!.overallCompletionPercentage;
  }

  // Get issues with views
  List<IssueView> getIssuesWithViews() {
    if (state == null) return [];
    return state!.allIssuesWithViews;
  }

  // Get all active issues
  List<IssueView> getAllActiveIssues() {
    if (state == null) return [];
    return state!.allActiveIssues;
  }

  // Search issues
  List<IssueView> searchIssues(String query) {
    return _categoriesService.searchIssues(query);
  }

  // Get popular issues
  List<IssueView> getPopularIssues() {
    return _categoriesService.getPopularIssues();
  }

  // Get category by ID
  IssueCategory? getCategoryById(String categoryId) {
    if (state == null) return null;
    return state!.getCategoryById(categoryId);
  }

  // Get issue by ID
  IssueView? getIssueById(String issueId) {
    if (state == null) return null;
    return state!.getIssueById(issueId);
  }

  // Save profile to storage (placeholder for future implementation)
  Future<void> saveProfile() async {
    if (state == null) return;
    
    // TODO: Implement saving to local storage or backend
    // For now, just update the lastUpdated timestamp
    state = state!.copyWith(lastUpdated: DateTime.now());
  }

  // Load profile from storage (placeholder for future implementation)
  Future<void> loadProfile(String userId) async {
    // TODO: Implement loading from local storage or backend
    // For now, just initialize with predefined categories
    initializeProfile(userId);
  }

  // Reset profile
  void resetProfile() {
    state = null;
  }
} 