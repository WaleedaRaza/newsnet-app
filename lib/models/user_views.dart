import 'package:flutter/foundation.dart';

// Enum for view expression methods
enum ViewExpressionMethod {
  stanceSlider,    // 1-10 scale
  multipleChoice,  // Strongly Support/Support/Neutral/Oppose/Strongly Oppose
  confidenceLevel, // How certain are you?
  interestLevel,   // How much do you care?
}

// Enum for stance levels
enum StanceLevel {
  stronglyOppose,
  oppose,
  neutral,
  support,
  stronglySupport,
}

// Enum for confidence levels
enum ConfidenceLevel {
  veryUncertain,
  uncertain,
  somewhatCertain,
  certain,
  veryCertain,
}

// Enum for interest levels
enum InterestLevel {
  notInterested,
  somewhatInterested,
  interested,
  veryInterested,
  extremelyInterested,
}

// Model for a specific issue view
class IssueView {
  final String issueId;
  final String issueName;
  final String categoryId;
  final String categoryName;
  final String? subcategory;
  
  // View data
  double? stanceValue; // 1-10 scale
  StanceLevel? stanceLevel;
  ConfidenceLevel? confidenceLevel;
  InterestLevel? interestLevel;
  String? userStatement;
  
  // Metadata
  DateTime? lastUpdated;
  DateTime? createdAt;
  bool isActive;

  IssueView({
    required this.issueId,
    required this.issueName,
    required this.categoryId,
    required this.categoryName,
    this.subcategory,
    this.stanceValue,
    this.stanceLevel,
    this.confidenceLevel,
    this.interestLevel,
    this.userStatement,
    this.lastUpdated,
    this.createdAt,
    this.isActive = true,
  });

  // Convert stance value (1-10) to stance level
  StanceLevel getStanceLevelFromValue() {
    if (stanceValue == null) return StanceLevel.neutral;
    if (stanceValue! <= 2) return StanceLevel.stronglyOppose;
    if (stanceValue! <= 4) return StanceLevel.oppose;
    if (stanceValue! <= 6) return StanceLevel.neutral;
    if (stanceValue! <= 8) return StanceLevel.support;
    return StanceLevel.stronglySupport;
  }

  // Convert stance level to value (1-10)
  double getStanceValueFromLevel() {
    switch (stanceLevel) {
      case StanceLevel.stronglyOppose:
        return 1.0;
      case StanceLevel.oppose:
        return 3.0;
      case StanceLevel.neutral:
        return 5.0;
      case StanceLevel.support:
        return 7.0;
      case StanceLevel.stronglySupport:
        return 9.0;
      default:
        return 5.0;
    }
  }

  // Get stance label
  String getStanceLabel() {
    switch (stanceLevel ?? getStanceLevelFromValue()) {
      case StanceLevel.stronglyOppose:
        return 'Strongly Oppose';
      case StanceLevel.oppose:
        return 'Oppose';
      case StanceLevel.neutral:
        return 'Neutral';
      case StanceLevel.support:
        return 'Support';
      case StanceLevel.stronglySupport:
        return 'Strongly Support';
      default:
        return 'Neutral';
    }
  }

  // Get confidence label
  String getConfidenceLabel() {
    switch (confidenceLevel) {
      case ConfidenceLevel.veryUncertain:
        return 'Very Uncertain';
      case ConfidenceLevel.uncertain:
        return 'Uncertain';
      case ConfidenceLevel.somewhatCertain:
        return 'Somewhat Certain';
      case ConfidenceLevel.certain:
        return 'Certain';
      case ConfidenceLevel.veryCertain:
        return 'Very Certain';
      default:
        return 'Uncertain';
    }
  }

  // Get interest label
  String getInterestLabel() {
    switch (interestLevel) {
      case InterestLevel.notInterested:
        return 'Not Interested';
      case InterestLevel.somewhatInterested:
        return 'Somewhat Interested';
      case InterestLevel.interested:
        return 'Interested';
      case InterestLevel.veryInterested:
        return 'Very Interested';
      case InterestLevel.extremelyInterested:
        return 'Extremely Interested';
      default:
        return 'Somewhat Interested';
    }
  }

  // Create copy with updated values
  IssueView copyWith({
    String? issueId,
    String? issueName,
    String? categoryId,
    String? categoryName,
    String? subcategory,
    double? stanceValue,
    StanceLevel? stanceLevel,
    ConfidenceLevel? confidenceLevel,
    InterestLevel? interestLevel,
    String? userStatement,
    DateTime? lastUpdated,
    DateTime? createdAt,
    bool? isActive,
  }) {
    return IssueView(
      issueId: issueId ?? this.issueId,
      issueName: issueName ?? this.issueName,
      categoryId: categoryId ?? this.categoryId,
      categoryName: categoryName ?? this.categoryName,
      subcategory: subcategory ?? this.subcategory,
      stanceValue: stanceValue ?? this.stanceValue,
      stanceLevel: stanceLevel ?? this.stanceLevel,
      confidenceLevel: confidenceLevel ?? this.confidenceLevel,
      interestLevel: interestLevel ?? this.interestLevel,
      userStatement: userStatement ?? this.userStatement,
      lastUpdated: lastUpdated ?? this.lastUpdated,
      createdAt: createdAt ?? this.createdAt,
      isActive: isActive ?? this.isActive,
    );
  }

  // Convert to JSON
  Map<String, dynamic> toJson() {
    return {
      'issueId': issueId,
      'issueName': issueName,
      'categoryId': categoryId,
      'categoryName': categoryName,
      'subcategory': subcategory,
      'stanceValue': stanceValue,
      'stanceLevel': stanceLevel?.name,
      'confidenceLevel': confidenceLevel?.name,
      'interestLevel': interestLevel?.name,
      'userStatement': userStatement,
      'lastUpdated': lastUpdated?.toIso8601String(),
      'createdAt': createdAt?.toIso8601String(),
      'isActive': isActive,
    };
  }

  // Create from JSON
  factory IssueView.fromJson(Map<String, dynamic> json) {
    return IssueView(
      issueId: json['issueId'],
      issueName: json['issueName'],
      categoryId: json['categoryId'],
      categoryName: json['categoryName'],
      subcategory: json['subcategory'],
      stanceValue: json['stanceValue']?.toDouble(),
      stanceLevel: json['stanceLevel'] != null 
          ? StanceLevel.values.firstWhere((e) => e.name == json['stanceLevel'])
          : null,
      confidenceLevel: json['confidenceLevel'] != null 
          ? ConfidenceLevel.values.firstWhere((e) => e.name == json['confidenceLevel'])
          : null,
      interestLevel: json['interestLevel'] != null 
          ? InterestLevel.values.firstWhere((e) => e.name == json['interestLevel'])
          : null,
      userStatement: json['userStatement'],
      lastUpdated: json['lastUpdated'] != null 
          ? DateTime.parse(json['lastUpdated']) 
          : null,
      createdAt: json['createdAt'] != null 
          ? DateTime.parse(json['createdAt']) 
          : null,
      isActive: json['isActive'] ?? true,
    );
  }
}

// Model for a category of issues
class IssueCategory {
  final String categoryId;
  final String categoryName;
  final String description;
  final String icon;
  final List<IssueView> issues;
  final bool isActive;

  IssueCategory({
    required this.categoryId,
    required this.categoryName,
    required this.description,
    required this.icon,
    required this.issues,
    this.isActive = true,
  });

  // Get active issues
  List<IssueView> get activeIssues => issues.where((issue) => issue.isActive).toList();

  // Get issues with views
  List<IssueView> get issuesWithViews => issues.where((issue) => 
    issue.stanceValue != null || 
    issue.stanceLevel != null || 
    issue.confidenceLevel != null || 
    issue.interestLevel != null
  ).toList();

  // Get completion percentage
  double get completionPercentage {
    if (activeIssues.isEmpty) return 0.0;
    final issuesWithViews = this.issuesWithViews.length;
    return (issuesWithViews / activeIssues.length) * 100;
  }

  // Create copy with updated values
  IssueCategory copyWith({
    String? categoryId,
    String? categoryName,
    String? description,
    String? icon,
    List<IssueView>? issues,
    bool? isActive,
  }) {
    return IssueCategory(
      categoryId: categoryId ?? this.categoryId,
      categoryName: categoryName ?? this.categoryName,
      description: description ?? this.description,
      icon: icon ?? this.icon,
      issues: issues ?? this.issues,
      isActive: isActive ?? this.isActive,
    );
  }
}

// Model for user's complete view profile
class UserViewProfile {
  final String userId;
  final List<IssueCategory> categories;
  final DateTime? lastUpdated;
  final DateTime? createdAt;

  UserViewProfile({
    required this.userId,
    required this.categories,
    this.lastUpdated,
    this.createdAt,
  });

  // Get all active issues
  List<IssueView> get allActiveIssues {
    return categories
        .where((category) => category.isActive)
        .expand((category) => category.activeIssues)
        .toList();
  }

  // Get all issues with views
  List<IssueView> get allIssuesWithViews {
    return categories
        .expand((category) => category.issuesWithViews)
        .toList();
  }

  // Get overall completion percentage
  double get overallCompletionPercentage {
    final totalActiveIssues = allActiveIssues.length;
    if (totalActiveIssues == 0) return 0.0;
    
    final issuesWithViews = allIssuesWithViews.length;
    return (issuesWithViews / totalActiveIssues) * 100;
  }

  // Get category by ID
  IssueCategory? getCategoryById(String categoryId) {
    try {
      return categories.firstWhere((category) => category.categoryId == categoryId);
    } catch (e) {
      return null;
    }
  }

  // Get issue by ID
  IssueView? getIssueById(String issueId) {
    try {
      return allActiveIssues.firstWhere((issue) => issue.issueId == issueId);
    } catch (e) {
      return null;
    }
  }

  // Create copy with updated values
  UserViewProfile copyWith({
    String? userId,
    List<IssueCategory>? categories,
    DateTime? lastUpdated,
    DateTime? createdAt,
  }) {
    return UserViewProfile(
      userId: userId ?? this.userId,
      categories: categories ?? this.categories,
      lastUpdated: lastUpdated ?? this.lastUpdated,
      createdAt: createdAt ?? this.createdAt,
    );
  }

  // Convert to JSON
  Map<String, dynamic> toJson() {
    return {
      'userId': userId,
      'categories': categories.map((category) => {
        'categoryId': category.categoryId,
        'categoryName': category.categoryName,
        'description': category.description,
        'icon': category.icon,
        'isActive': category.isActive,
        'issues': category.issues.map((issue) => issue.toJson()).toList(),
      }).toList(),
      'lastUpdated': lastUpdated?.toIso8601String(),
      'createdAt': createdAt?.toIso8601String(),
    };
  }

  // Create from JSON
  factory UserViewProfile.fromJson(Map<String, dynamic> json) {
    return UserViewProfile(
      userId: json['userId'],
      categories: (json['categories'] as List)
          .map((categoryJson) => IssueCategory(
                categoryId: categoryJson['categoryId'],
                categoryName: categoryJson['categoryName'],
                description: categoryJson['description'],
                icon: categoryJson['icon'],
                isActive: categoryJson['isActive'] ?? true,
                issues: (categoryJson['issues'] as List)
                    .map((issueJson) => IssueView.fromJson(issueJson))
                    .toList(),
              ))
          .toList(),
      lastUpdated: json['lastUpdated'] != null 
          ? DateTime.parse(json['lastUpdated']) 
          : null,
      createdAt: json['createdAt'] != null 
          ? DateTime.parse(json['createdAt']) 
          : null,
    );
  }
}

// Add a new model for subcategories
class Subcategory {
  final String name;
  final String displayName;
  final List<IssueView> issues;

  Subcategory({
    required this.name,
    required this.displayName,
    required this.issues,
  });

  // Get issues that have views
  List<IssueView> get issuesWithViews {
    return issues.where((issue) => 
      issue.stanceValue != null || 
      issue.stanceLevel != null || 
      issue.confidenceLevel != null || 
      issue.interestLevel != null
    ).toList();
  }

  // Get completion percentage for this subcategory
  double get completionPercentage {
    if (issues.isEmpty) return 0.0;
    return (issuesWithViews.length / issues.length) * 100;
  }
} 