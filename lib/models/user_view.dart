import 'package:json_annotation/json_annotation.dart';

part 'user_view.g.dart';

@JsonSerializable()
class UserView {
  final int? id;
  final int userId;
  final String issueId;
  final String categoryId;
  final String? subcategory;
  final double? stanceValue;
  final String? stanceChoice;
  final int? confidenceLevel;
  final int? interestLevel;
  final String expressionType;
  final bool isActive;
  final DateTime createdAt;
  final DateTime updatedAt;

  const UserView({
    this.id,
    required this.userId,
    required this.issueId,
    required this.categoryId,
    this.subcategory,
    this.stanceValue,
    this.stanceChoice,
    this.confidenceLevel,
    this.interestLevel,
    required this.expressionType,
    this.isActive = true,
    required this.createdAt,
    required this.updatedAt,
  });

  factory UserView.fromJson(Map<String, dynamic> json) => _$UserViewFromJson(json);
  Map<String, dynamic> toJson() => _$UserViewToJson(this);
}

@JsonSerializable()
class UserViewCreate {
  final String issueId;
  final String categoryId;
  final String? subcategory;
  final double? stanceValue;
  final String? stanceChoice;
  final int? confidenceLevel;
  final int? interestLevel;
  final String expressionType;

  const UserViewCreate({
    required this.issueId,
    required this.categoryId,
    this.subcategory,
    this.stanceValue,
    this.stanceChoice,
    this.confidenceLevel,
    this.interestLevel,
    required this.expressionType,
  });

  factory UserViewCreate.fromJson(Map<String, dynamic> json) => _$UserViewCreateFromJson(json);
  Map<String, dynamic> toJson() => _$UserViewCreateToJson(this);
}

@JsonSerializable()
class UserViewUpdate {
  final double? stanceValue;
  final String? stanceChoice;
  final int? confidenceLevel;
  final int? interestLevel;
  final String? expressionType;

  const UserViewUpdate({
    this.stanceValue,
    this.stanceChoice,
    this.confidenceLevel,
    this.interestLevel,
    this.expressionType,
  });

  factory UserViewUpdate.fromJson(Map<String, dynamic> json) => _$UserViewUpdateFromJson(json);
  Map<String, dynamic> toJson() => _$UserViewUpdateToJson(this);
}

@JsonSerializable()
class UserViewHistory {
  final int? id;
  final int userId;
  final int userViewId;
  final String issueId;
  final String categoryId;
  final String? subcategory;
  final double? stanceValue;
  final String? stanceChoice;
  final int? confidenceLevel;
  final int? interestLevel;
  final String expressionType;
  final String changeReason;
  final DateTime createdAt;

  const UserViewHistory({
    this.id,
    required this.userId,
    required this.userViewId,
    required this.issueId,
    required this.categoryId,
    this.subcategory,
    this.stanceValue,
    this.stanceChoice,
    this.confidenceLevel,
    this.interestLevel,
    required this.expressionType,
    required this.changeReason,
    required this.createdAt,
  });

  factory UserViewHistory.fromJson(Map<String, dynamic> json) => _$UserViewHistoryFromJson(json);
  Map<String, dynamic> toJson() => _$UserViewHistoryToJson(this);
}

@JsonSerializable()
class UserViewBulkUpdate {
  final List<UserViewCreate> views;

  const UserViewBulkUpdate({
    required this.views,
  });

  factory UserViewBulkUpdate.fromJson(Map<String, dynamic> json) => _$UserViewBulkUpdateFromJson(json);
  Map<String, dynamic> toJson() => _$UserViewBulkUpdateToJson(this);
}

@JsonSerializable()
class UserViewBulkResponse {
  final List<UserView> updatedViews;
  final List<String> errors;
  final int successCount;
  final int errorCount;

  const UserViewBulkResponse({
    required this.updatedViews,
    required this.errors,
    required this.successCount,
    required this.errorCount,
  });

  factory UserViewBulkResponse.fromJson(Map<String, dynamic> json) => _$UserViewBulkResponseFromJson(json);
  Map<String, dynamic> toJson() => _$UserViewBulkResponseToJson(this);
}

@JsonSerializable()
class UserProfileWithViews {
  final int id;
  final String email;
  final String? name;
  final List<String>? interests;
  final Map<String, dynamic>? beliefFingerprint;
  final double? biasSetting;
  final DateTime createdAt;
  final DateTime updatedAt;
  final List<UserView> userViews;
  final int viewCount;

  const UserProfileWithViews({
    required this.id,
    required this.email,
    this.name,
    this.interests,
    this.beliefFingerprint,
    this.biasSetting,
    required this.createdAt,
    required this.updatedAt,
    required this.userViews,
    required this.viewCount,
  });

  factory UserProfileWithViews.fromJson(Map<String, dynamic> json) => _$UserProfileWithViewsFromJson(json);
  Map<String, dynamic> toJson() => _$UserProfileWithViewsToJson(this);
}

@JsonSerializable()
class CategoryInfo {
  final String categoryId;
  final String categoryName;
  final String description;
  final String icon;
  final List<IssueInfo> issues;
  final List<String> subcategories;

  const CategoryInfo({
    required this.categoryId,
    required this.categoryName,
    required this.description,
    required this.icon,
    required this.issues,
    required this.subcategories,
  });

  factory CategoryInfo.fromJson(Map<String, dynamic> json) => _$CategoryInfoFromJson(json);
  Map<String, dynamic> toJson() => _$CategoryInfoToJson(this);
}

@JsonSerializable()
class IssueInfo {
  final String issueId;
  final String issueName;
  final String categoryId;
  final String categoryName;
  final String? subcategory;
  final String? subcategoryDisplayName;

  const IssueInfo({
    required this.issueId,
    required this.issueName,
    required this.categoryId,
    required this.categoryName,
    this.subcategory,
    this.subcategoryDisplayName,
  });

  factory IssueInfo.fromJson(Map<String, dynamic> json) => _$IssueInfoFromJson(json);
  Map<String, dynamic> toJson() => _$IssueInfoToJson(this);
} 