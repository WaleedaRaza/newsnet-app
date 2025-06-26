import 'package:json_annotation/json_annotation.dart';

part 'category.g.dart';

@JsonSerializable()
class Category {
  final String categoryId;
  final String categoryName;
  final String description;
  final String icon;
  final List<Issue> issues;
  final List<String> subcategories;

  const Category({
    required this.categoryId,
    required this.categoryName,
    required this.description,
    required this.icon,
    required this.issues,
    required this.subcategories,
  });

  factory Category.fromJson(Map<String, dynamic> json) => _$CategoryFromJson(json);
  Map<String, dynamic> toJson() => _$CategoryToJson(this);
}

@JsonSerializable()
class Issue {
  final String issueId;
  final String issueName;
  final String categoryId;
  final String categoryName;
  final String? subcategory;
  final String? subcategoryDisplayName;

  const Issue({
    required this.issueId,
    required this.issueName,
    required this.categoryId,
    required this.categoryName,
    this.subcategory,
    this.subcategoryDisplayName,
  });

  factory Issue.fromJson(Map<String, dynamic> json) => _$IssueFromJson(json);
  Map<String, dynamic> toJson() => _$IssueToJson(this);
} 