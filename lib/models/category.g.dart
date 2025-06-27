// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'category.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Category _$CategoryFromJson(Map<String, dynamic> json) => Category(
      categoryId: json['categoryId'] as String,
      categoryName: json['categoryName'] as String,
      description: json['description'] as String,
      icon: json['icon'] as String,
      issues: (json['issues'] as List<dynamic>)
          .map((e) => Issue.fromJson(e as Map<String, dynamic>))
          .toList(),
      subcategories: (json['subcategories'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
    );

Map<String, dynamic> _$CategoryToJson(Category instance) => <String, dynamic>{
      'categoryId': instance.categoryId,
      'categoryName': instance.categoryName,
      'description': instance.description,
      'icon': instance.icon,
      'issues': instance.issues,
      'subcategories': instance.subcategories,
    };

Issue _$IssueFromJson(Map<String, dynamic> json) => Issue(
      issueId: json['issueId'] as String,
      issueName: json['issueName'] as String,
      categoryId: json['categoryId'] as String,
      categoryName: json['categoryName'] as String,
      subcategory: json['subcategory'] as String?,
      subcategoryDisplayName: json['subcategoryDisplayName'] as String?,
    );

Map<String, dynamic> _$IssueToJson(Issue instance) => <String, dynamic>{
      'issueId': instance.issueId,
      'issueName': instance.issueName,
      'categoryId': instance.categoryId,
      'categoryName': instance.categoryName,
      'subcategory': instance.subcategory,
      'subcategoryDisplayName': instance.subcategoryDisplayName,
    };
