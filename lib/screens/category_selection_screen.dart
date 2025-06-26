import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/user_views.dart';
import '../widgets/view_expression_widget.dart';
import '../providers/user_views_provider.dart';
import '../services/view_categories_service.dart';

class CategorySelectionScreen extends ConsumerStatefulWidget {
  const CategorySelectionScreen({super.key});

  @override
  ConsumerState<CategorySelectionScreen> createState() => _CategorySelectionScreenState();
}

class _CategorySelectionScreenState extends ConsumerState<CategorySelectionScreen>
    with TickerProviderStateMixin {
  TabController? _tabController;
  String _searchQuery = '';
  Map<String, bool> _expandedSubcategories = {};

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
  void dispose() {
    _tabController?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final userProfile = ref.watch(userViewProfileProvider);
    
    if (userProfile == null) {
      return const Scaffold(
        body: Center(
          child: CircularProgressIndicator(),
        ),
      );
    }

    // Initialize tab controller if not already done
    if (_tabController == null) {
      _tabController = TabController(
        length: userProfile.categories.length,
        vsync: this,
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Express Your Views'),
        backgroundColor: Theme.of(context).primaryColor,
        foregroundColor: Colors.white,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.search),
            onPressed: () {
              _showSearchDialog();
            },
          ),
          IconButton(
            icon: const Icon(Icons.analytics),
            onPressed: () {
              _showProfileSummary();
            },
          ),
        ],
        bottom: TabBar(
          controller: _tabController!,
          isScrollable: true,
          indicatorColor: Colors.white,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white70,
          tabs: userProfile.categories.map((category) {
            return Tab(
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(category.icon),
                  const SizedBox(width: 4),
                  Text(category.categoryName),
                ],
              ),
            );
          }).toList(),
        ),
      ),
      body: Column(
        children: [
          // Progress indicator
          _buildProgressIndicator(userProfile),
          
          // Tab content
          Expanded(
            child: TabBarView(
              controller: _tabController!,
              children: userProfile.categories.map((category) {
                return _buildCategoryContent(category);
              }).toList(),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildProgressIndicator(UserViewProfile userProfile) {
    final completionPercentage = userProfile.overallCompletionPercentage;
    
    return Container(
      padding: const EdgeInsets.all(16),
      color: Theme.of(context).primaryColor.withOpacity(0.1),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Profile Completion',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                  color: Theme.of(context).primaryColor,
                ),
              ),
              Text(
                '${completionPercentage.round()}%',
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
            value: completionPercentage / 100,
            backgroundColor: Colors.grey[300],
            valueColor: AlwaysStoppedAnimation<Color>(
              completionPercentage >= 50 
                  ? Colors.green 
                  : completionPercentage >= 25 
                      ? Colors.orange 
                      : Colors.red,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            '${userProfile.allIssuesWithViews.length} of ${userProfile.allActiveIssues.length} issues completed',
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey[600],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCategoryContent(IssueCategory category) {
    // Get subcategories for this category
    final subcategories = ViewCategoriesService().getSubcategoriesForCategory(category.categoryId);
    
    if (subcategories.isEmpty) {
      return const Center(
        child: Text('No issues available in this category.'),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: subcategories.length,
      itemBuilder: (context, index) {
        final subcategory = subcategories[index];
        return _buildSubcategorySection(subcategory, category);
      },
    );
  }

  Widget _buildSubcategorySection(Subcategory subcategory, IssueCategory category) {
    final subcategoryKey = '${category.categoryId}_${subcategory.name}';
    final isExpanded = _expandedSubcategories[subcategoryKey] ?? false;

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      elevation: 2,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Collapsible subcategory header
          InkWell(
            onTap: () {
              setState(() {
                _expandedSubcategories[subcategoryKey] = !isExpanded;
              });
            },
            child: Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Theme.of(context).primaryColor.withOpacity(0.1),
                borderRadius: BorderRadius.only(
                  topLeft: const Radius.circular(12),
                  topRight: const Radius.circular(12),
                  bottomLeft: Radius.circular(isExpanded ? 0 : 12),
                  bottomRight: Radius.circular(isExpanded ? 0 : 12),
                ),
              ),
              child: Row(
                children: [
                  Expanded(
                    child: Text(
                      subcategory.displayName,
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: Theme.of(context).primaryColor,
                      ),
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: Theme.of(context).primaryColor,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      '${subcategory.issuesWithViews.length}/${subcategory.issues.length}',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Icon(
                    isExpanded ? Icons.expand_less : Icons.expand_more,
                    color: Theme.of(context).primaryColor,
                    size: 24,
                  ),
                ],
              ),
            ),
          ),
          
          // Expandable content
          if (isExpanded) ...[
            ...subcategory.issues.map((issue) => _buildIssueCard(issue, category)),
          ],
        ],
      ),
    );
  }

  Widget _buildIssueCard(IssueView issue, IssueCategory category) {
    final hasView = issue.stanceValue != null || 
                   issue.stanceLevel != null || 
                   issue.confidenceLevel != null || 
                   issue.interestLevel != null;

    return Container(
      decoration: BoxDecoration(
        border: Border(
          bottom: BorderSide(
            color: Colors.grey[200]!,
            width: 0.5,
          ),
        ),
      ),
      child: InkWell(
        onTap: () {
          _showIssueDetail(issue);
        },
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(
                      issue.issueName,
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                  if (hasView)
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 8,
                        vertical: 4,
                      ),
                      decoration: BoxDecoration(
                        color: Colors.green,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: const Text(
                        'VIEWED',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                ],
              ),
              const SizedBox(height: 8),
              
              // Show current view if exists
              if (hasView) ...[
                _buildCurrentViewSummary(issue),
                const SizedBox(height: 12),
              ],
              
              // Action buttons
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () {
                        _showIssueDetail(issue);
                      },
                      icon: Icon(hasView ? Icons.edit : Icons.add),
                      label: Text(hasView ? 'Edit View' : 'Add View'),
                      style: OutlinedButton.styleFrom(
                        foregroundColor: Theme.of(context).primaryColor,
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  if (hasView)
                    IconButton(
                      onPressed: () {
                        _clearIssueView(issue);
                      },
                      icon: const Icon(Icons.clear, color: Colors.red),
                      tooltip: 'Clear View',
                    ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildCurrentViewSummary(IssueView issue) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.grey[100],
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                _getStanceIcon(issue.stanceValue ?? 5.0),
                color: _getStanceColor(issue.stanceValue ?? 5.0),
                size: 16,
              ),
              const SizedBox(width: 8),
              Text(
                issue.getStanceLabel(),
                style: TextStyle(
                  fontWeight: FontWeight.w600,
                  color: _getStanceColor(issue.stanceValue ?? 5.0),
                ),
              ),
            ],
          ),
          if (issue.confidenceLevel != null) ...[
            const SizedBox(height: 4),
            Text(
              'Confidence: ${issue.getConfidenceLabel()}',
              style: const TextStyle(fontSize: 12, color: Colors.grey),
            ),
          ],
          if (issue.interestLevel != null) ...[
            const SizedBox(height: 4),
            Text(
              'Interest: ${issue.getInterestLabel()}',
              style: const TextStyle(fontSize: 12, color: Colors.grey),
            ),
          ],
        ],
      ),
    );
  }

  void _showIssueDetail(IssueView issue) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.9,
        minChildSize: 0.5,
        maxChildSize: 0.95,
        builder: (context, scrollController) => Container(
          decoration: const BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
          ),
          child: Column(
            children: [
              // Handle
              Container(
                margin: const EdgeInsets.only(top: 8),
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: Colors.grey[300],
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
              // Content
              Expanded(
                child: SingleChildScrollView(
                  controller: scrollController,
                  child: ViewExpressionWidget(
                    issue: issue,
                    onViewChanged: (updatedIssue) {
                      ref.read(userViewProfileProvider.notifier).updateIssueView(updatedIssue);
                      Navigator.pop(context);
                    },
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _clearIssueView(IssueView issue) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Clear View'),
        content: Text('Are you sure you want to clear your view on "${issue.issueName}"?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              ref.read(userViewProfileProvider.notifier).clearIssueView(issue.issueId);
              Navigator.pop(context);
            },
            child: const Text('Clear', style: TextStyle(color: Colors.red)),
          ),
        ],
      ),
    );
  }

  void _showSearchDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Search Issues'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              decoration: const InputDecoration(
                hintText: 'Search for issues...',
                prefixIcon: Icon(Icons.search),
              ),
              onChanged: (value) {
                setState(() {
                  _searchQuery = value;
                });
              },
            ),
            const SizedBox(height: 16),
            if (_searchQuery.isNotEmpty)
              SizedBox(
                height: 200,
                child: FutureBuilder<List<IssueView>>(
                  future: Future.value(ref.read(userViewProfileProvider.notifier).searchIssues(_searchQuery)),
                  builder: (context, snapshot) {
                    if (snapshot.hasData) {
                      final results = snapshot.data!;
                      if (results.isEmpty) {
                        return const Center(
                          child: Text('No issues found.'),
                        );
                      }
                      return ListView.builder(
                        itemCount: results.length,
                        itemBuilder: (context, index) {
                          final issue = results[index];
                          return ListTile(
                            title: Text(issue.issueName),
                            subtitle: Text(issue.categoryName),
                            onTap: () {
                              Navigator.pop(context);
                              _navigateToIssue(issue);
                            },
                          );
                        },
                      );
                    }
                    return const Center(child: CircularProgressIndicator());
                  },
                ),
              ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  void _navigateToIssue(IssueView issue) {
    final userProfile = ref.read(userViewProfileProvider);
    if (userProfile == null) return;

    // Find the category index and navigate to it
    for (int i = 0; i < userProfile.categories.length; i++) {
      final category = userProfile.categories[i];
      if (category.categoryId == issue.categoryId) {
        _tabController!.animateTo(i);
        // Show the issue detail after a short delay
        Future.delayed(const Duration(milliseconds: 300), () {
          _showIssueDetail(issue);
        });
        break;
      }
    }
  }

  void _showProfileSummary() {
    final userProfile = ref.read(userViewProfileProvider);
    if (userProfile == null) return;

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Profile Summary'),
        content: SizedBox(
          width: double.maxFinite,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              _buildCategorySummary(userProfile),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  Widget _buildCategorySummary(UserViewProfile userProfile) {
    return Column(
      children: userProfile.categories.map((category) {
        final completionPercentage = category.completionPercentage;
        return ListTile(
          leading: Text(category.icon, style: const TextStyle(fontSize: 20)),
          title: Text(category.categoryName),
          subtitle: Text('${category.issuesWithViews.length}/${category.activeIssues.length} issues'),
          trailing: Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: completionPercentage >= 50 
                  ? Colors.green 
                  : completionPercentage >= 25 
                      ? Colors.orange 
                      : Colors.red,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Text(
              '${completionPercentage.round()}%',
              style: const TextStyle(
                color: Colors.white,
                fontSize: 12,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        );
      }).toList(),
    );
  }

  Color _getStanceColor(double value) {
    if (value <= 2) return Colors.red;
    if (value <= 4) return Colors.orange;
    if (value <= 6) return Colors.grey;
    if (value <= 8) return Colors.lightGreen;
    return Colors.green;
  }

  IconData _getStanceIcon(double value) {
    if (value <= 2) return Icons.thumb_down;
    if (value <= 4) return Icons.thumb_down_outlined;
    if (value <= 6) return Icons.remove;
    if (value <= 8) return Icons.thumb_up_outlined;
    return Icons.thumb_up;
  }
} 