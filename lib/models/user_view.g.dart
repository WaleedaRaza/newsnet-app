// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'user_view.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

UserView _$UserViewFromJson(Map<String, dynamic> json) => UserView(
      id: (json['id'] as num?)?.toInt(),
      userId: (json['userId'] as num).toInt(),
      issueId: json['issueId'] as String,
      categoryId: json['categoryId'] as String,
      subcategory: json['subcategory'] as String?,
      stanceValue: (json['stanceValue'] as num?)?.toDouble(),
      stanceChoice: json['stanceChoice'] as String?,
      confidenceLevel: (json['confidenceLevel'] as num?)?.toInt(),
      interestLevel: (json['interestLevel'] as num?)?.toInt(),
      expressionType: json['expressionType'] as String,
      isActive: json['isActive'] as bool? ?? true,
      createdAt: DateTime.parse(json['createdAt'] as String),
      updatedAt: DateTime.parse(json['updatedAt'] as String),
    );

Map<String, dynamic> _$UserViewToJson(UserView instance) => <String, dynamic>{
      'id': instance.id,
      'userId': instance.userId,
      'issueId': instance.issueId,
      'categoryId': instance.categoryId,
      'subcategory': instance.subcategory,
      'stanceValue': instance.stanceValue,
      'stanceChoice': instance.stanceChoice,
      'confidenceLevel': instance.confidenceLevel,
      'interestLevel': instance.interestLevel,
      'expressionType': instance.expressionType,
      'isActive': instance.isActive,
      'createdAt': instance.createdAt.toIso8601String(),
      'updatedAt': instance.updatedAt.toIso8601String(),
    };

UserViewCreate _$UserViewCreateFromJson(Map<String, dynamic> json) =>
    UserViewCreate(
      issueId: json['issueId'] as String,
      categoryId: json['categoryId'] as String,
      subcategory: json['subcategory'] as String?,
      stanceValue: (json['stanceValue'] as num?)?.toDouble(),
      stanceChoice: json['stanceChoice'] as String?,
      confidenceLevel: (json['confidenceLevel'] as num?)?.toInt(),
      interestLevel: (json['interestLevel'] as num?)?.toInt(),
      expressionType: json['expressionType'] as String,
    );

Map<String, dynamic> _$UserViewCreateToJson(UserViewCreate instance) =>
    <String, dynamic>{
      'issueId': instance.issueId,
      'categoryId': instance.categoryId,
      'subcategory': instance.subcategory,
      'stanceValue': instance.stanceValue,
      'stanceChoice': instance.stanceChoice,
      'confidenceLevel': instance.confidenceLevel,
      'interestLevel': instance.interestLevel,
      'expressionType': instance.expressionType,
    };

UserViewUpdate _$UserViewUpdateFromJson(Map<String, dynamic> json) =>
    UserViewUpdate(
      stanceValue: (json['stanceValue'] as num?)?.toDouble(),
      stanceChoice: json['stanceChoice'] as String?,
      confidenceLevel: (json['confidenceLevel'] as num?)?.toInt(),
      interestLevel: (json['interestLevel'] as num?)?.toInt(),
      expressionType: json['expressionType'] as String?,
    );

Map<String, dynamic> _$UserViewUpdateToJson(UserViewUpdate instance) =>
    <String, dynamic>{
      'stanceValue': instance.stanceValue,
      'stanceChoice': instance.stanceChoice,
      'confidenceLevel': instance.confidenceLevel,
      'interestLevel': instance.interestLevel,
      'expressionType': instance.expressionType,
    };

UserViewHistory _$UserViewHistoryFromJson(Map<String, dynamic> json) =>
    UserViewHistory(
      id: (json['id'] as num?)?.toInt(),
      userId: (json['userId'] as num).toInt(),
      userViewId: (json['userViewId'] as num).toInt(),
      issueId: json['issueId'] as String,
      categoryId: json['categoryId'] as String,
      subcategory: json['subcategory'] as String?,
      stanceValue: (json['stanceValue'] as num?)?.toDouble(),
      stanceChoice: json['stanceChoice'] as String?,
      confidenceLevel: (json['confidenceLevel'] as num?)?.toInt(),
      interestLevel: (json['interestLevel'] as num?)?.toInt(),
      expressionType: json['expressionType'] as String,
      changeReason: json['changeReason'] as String,
      createdAt: DateTime.parse(json['createdAt'] as String),
    );

Map<String, dynamic> _$UserViewHistoryToJson(UserViewHistory instance) =>
    <String, dynamic>{
      'id': instance.id,
      'userId': instance.userId,
      'userViewId': instance.userViewId,
      'issueId': instance.issueId,
      'categoryId': instance.categoryId,
      'subcategory': instance.subcategory,
      'stanceValue': instance.stanceValue,
      'stanceChoice': instance.stanceChoice,
      'confidenceLevel': instance.confidenceLevel,
      'interestLevel': instance.interestLevel,
      'expressionType': instance.expressionType,
      'changeReason': instance.changeReason,
      'createdAt': instance.createdAt.toIso8601String(),
    };

UserViewBulkUpdate _$UserViewBulkUpdateFromJson(Map<String, dynamic> json) =>
    UserViewBulkUpdate(
      views: (json['views'] as List<dynamic>)
          .map((e) => UserViewCreate.fromJson(e as Map<String, dynamic>))
          .toList(),
    );

Map<String, dynamic> _$UserViewBulkUpdateToJson(UserViewBulkUpdate instance) =>
    <String, dynamic>{
      'views': instance.views,
    };

UserViewBulkResponse _$UserViewBulkResponseFromJson(
        Map<String, dynamic> json) =>
    UserViewBulkResponse(
      updatedViews: (json['updatedViews'] as List<dynamic>)
          .map((e) => UserView.fromJson(e as Map<String, dynamic>))
          .toList(),
      errors:
          (json['errors'] as List<dynamic>).map((e) => e as String).toList(),
      successCount: (json['successCount'] as num).toInt(),
      errorCount: (json['errorCount'] as num).toInt(),
    );

Map<String, dynamic> _$UserViewBulkResponseToJson(
        UserViewBulkResponse instance) =>
    <String, dynamic>{
      'updatedViews': instance.updatedViews,
      'errors': instance.errors,
      'successCount': instance.successCount,
      'errorCount': instance.errorCount,
    };

UserProfileWithViews _$UserProfileWithViewsFromJson(
        Map<String, dynamic> json) =>
    UserProfileWithViews(
      id: (json['id'] as num).toInt(),
      email: json['email'] as String,
      name: json['name'] as String?,
      interests: (json['interests'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList(),
      beliefFingerprint: json['beliefFingerprint'] as Map<String, dynamic>?,
      biasSetting: (json['biasSetting'] as num?)?.toDouble(),
      createdAt: DateTime.parse(json['createdAt'] as String),
      updatedAt: DateTime.parse(json['updatedAt'] as String),
      userViews: (json['userViews'] as List<dynamic>)
          .map((e) => UserView.fromJson(e as Map<String, dynamic>))
          .toList(),
      viewCount: (json['viewCount'] as num).toInt(),
    );

Map<String, dynamic> _$UserProfileWithViewsToJson(
        UserProfileWithViews instance) =>
    <String, dynamic>{
      'id': instance.id,
      'email': instance.email,
      'name': instance.name,
      'interests': instance.interests,
      'beliefFingerprint': instance.beliefFingerprint,
      'biasSetting': instance.biasSetting,
      'createdAt': instance.createdAt.toIso8601String(),
      'updatedAt': instance.updatedAt.toIso8601String(),
      'userViews': instance.userViews,
      'viewCount': instance.viewCount,
    };

CategoryInfo _$CategoryInfoFromJson(Map<String, dynamic> json) => CategoryInfo(
      categoryId: json['categoryId'] as String,
      categoryName: json['categoryName'] as String,
      description: json['description'] as String,
      icon: json['icon'] as String,
      issues: (json['issues'] as List<dynamic>)
          .map((e) => IssueInfo.fromJson(e as Map<String, dynamic>))
          .toList(),
      subcategories: (json['subcategories'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
    );

Map<String, dynamic> _$CategoryInfoToJson(CategoryInfo instance) =>
    <String, dynamic>{
      'categoryId': instance.categoryId,
      'categoryName': instance.categoryName,
      'description': instance.description,
      'icon': instance.icon,
      'issues': instance.issues,
      'subcategories': instance.subcategories,
    };

IssueInfo _$IssueInfoFromJson(Map<String, dynamic> json) => IssueInfo(
      issueId: json['issueId'] as String,
      issueName: json['issueName'] as String,
      categoryId: json['categoryId'] as String,
      categoryName: json['categoryName'] as String,
      subcategory: json['subcategory'] as String?,
      subcategoryDisplayName: json['subcategoryDisplayName'] as String?,
    );

Map<String, dynamic> _$IssueInfoToJson(IssueInfo instance) => <String, dynamic>{
      'issueId': instance.issueId,
      'issueName': instance.issueName,
      'categoryId': instance.categoryId,
      'categoryName': instance.categoryName,
      'subcategory': instance.subcategory,
      'subcategoryDisplayName': instance.subcategoryDisplayName,
    };
