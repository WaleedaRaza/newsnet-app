// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'stance_detection.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

StanceDetectionRequest _$StanceDetectionRequestFromJson(
        Map<String, dynamic> json) =>
    StanceDetectionRequest(
      belief: json['belief'] as String,
      articleText: json['articleText'] as String,
      methodPreference: json['methodPreference'] as String? ?? 'auto',
    );

Map<String, dynamic> _$StanceDetectionRequestToJson(
        StanceDetectionRequest instance) =>
    <String, dynamic>{
      'belief': instance.belief,
      'articleText': instance.articleText,
      'methodPreference': instance.methodPreference,
    };

StanceDetectionResponse _$StanceDetectionResponseFromJson(
        Map<String, dynamic> json) =>
    StanceDetectionResponse(
      belief: json['belief'] as String,
      articleText: json['articleText'] as String,
      stance: json['stance'] as String,
      confidence: (json['confidence'] as num).toDouble(),
      method: json['method'] as String,
      evidence:
          (json['evidence'] as List<dynamic>).map((e) => e as String).toList(),
      processingTime: (json['processingTime'] as num).toDouble(),
      metadata: json['metadata'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$StanceDetectionResponseToJson(
        StanceDetectionResponse instance) =>
    <String, dynamic>{
      'belief': instance.belief,
      'articleText': instance.articleText,
      'stance': instance.stance,
      'confidence': instance.confidence,
      'method': instance.method,
      'evidence': instance.evidence,
      'processingTime': instance.processingTime,
      'metadata': instance.metadata,
    };

BeliefStatement _$BeliefStatementFromJson(Map<String, dynamic> json) =>
    BeliefStatement(
      text: json['text'] as String,
      category: json['category'] as String,
      strength: (json['strength'] as num?)?.toDouble() ?? 0.5,
      source: json['source'] as String? ?? 'user_input',
      metadata: json['metadata'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$BeliefStatementToJson(BeliefStatement instance) =>
    <String, dynamic>{
      'text': instance.text,
      'category': instance.category,
      'strength': instance.strength,
      'source': instance.source,
      'metadata': instance.metadata,
    };

UserBeliefFingerprint _$UserBeliefFingerprintFromJson(
        Map<String, dynamic> json) =>
    UserBeliefFingerprint(
      userId: json['userId'] as String,
      beliefs: (json['beliefs'] as List<dynamic>)
          .map((e) => BeliefStatement.fromJson(e as Map<String, dynamic>))
          .toList(),
      categories: (json['categories'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
      lastUpdated: DateTime.parse(json['lastUpdated'] as String),
    );

Map<String, dynamic> _$UserBeliefFingerprintToJson(
        UserBeliefFingerprint instance) =>
    <String, dynamic>{
      'userId': instance.userId,
      'beliefs': instance.beliefs,
      'categories': instance.categories,
      'lastUpdated': instance.lastUpdated.toIso8601String(),
    };

ContentScoringRequest _$ContentScoringRequestFromJson(
        Map<String, dynamic> json) =>
    ContentScoringRequest(
      userId: json['userId'] as String,
      contentText: json['contentText'] as String,
      contentMetadata: json['contentMetadata'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$ContentScoringRequestToJson(
        ContentScoringRequest instance) =>
    <String, dynamic>{
      'userId': instance.userId,
      'contentText': instance.contentText,
      'contentMetadata': instance.contentMetadata,
    };

ContentScoringResponse _$ContentScoringResponseFromJson(
        Map<String, dynamic> json) =>
    ContentScoringResponse(
      contentId: json['contentId'] as String,
      contentType: json['contentType'] as String,
      proximityScore: (json['proximityScore'] as num).toDouble(),
      stanceAlignment: (json['stanceAlignment'] as num).toDouble(),
      overallScore: (json['overallScore'] as num).toDouble(),
      evidence:
          (json['evidence'] as List<dynamic>).map((e) => e as String).toList(),
      metadata: json['metadata'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$ContentScoringResponseToJson(
        ContentScoringResponse instance) =>
    <String, dynamic>{
      'contentId': instance.contentId,
      'contentType': instance.contentType,
      'proximityScore': instance.proximityScore,
      'stanceAlignment': instance.stanceAlignment,
      'overallScore': instance.overallScore,
      'evidence': instance.evidence,
      'metadata': instance.metadata,
    };
