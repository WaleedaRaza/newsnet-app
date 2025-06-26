// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'fusion_result.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

FusionResult _$FusionResultFromJson(Map<String, dynamic> json) => FusionResult(
      id: json['id'] as String,
      storyId: json['storyId'] as String,
      fusedNarrative: json['fusedNarrative'] as String,
      modulatedNarrative: json['modulatedNarrative'] as String,
      biasLevel: (json['biasLevel'] as num).toDouble(),
      contradictions: (json['contradictions'] as List<dynamic>)
          .map((e) => Contradiction.fromJson(e as Map<String, dynamic>))
          .toList(),
      entities: (json['entities'] as List<dynamic>)
          .map((e) => Entity.fromJson(e as Map<String, dynamic>))
          .toList(),
      confidence: (json['confidence'] as num).toDouble(),
      createdAt: DateTime.parse(json['createdAt'] as String),
    );

Map<String, dynamic> _$FusionResultToJson(FusionResult instance) =>
    <String, dynamic>{
      'id': instance.id,
      'storyId': instance.storyId,
      'fusedNarrative': instance.fusedNarrative,
      'modulatedNarrative': instance.modulatedNarrative,
      'biasLevel': instance.biasLevel,
      'contradictions': instance.contradictions,
      'entities': instance.entities,
      'confidence': instance.confidence,
      'createdAt': instance.createdAt.toIso8601String(),
    };

Contradiction _$ContradictionFromJson(Map<String, dynamic> json) =>
    Contradiction(
      id: json['id'] as String,
      description: json['description'] as String,
      sources:
          (json['sources'] as List<dynamic>).map((e) => e as String).toList(),
      resolution: json['resolution'] as String,
      severity: (json['severity'] as num).toDouble(),
    );

Map<String, dynamic> _$ContradictionToJson(Contradiction instance) =>
    <String, dynamic>{
      'id': instance.id,
      'description': instance.description,
      'sources': instance.sources,
      'resolution': instance.resolution,
      'severity': instance.severity,
    };

Entity _$EntityFromJson(Map<String, dynamic> json) => Entity(
      id: json['id'] as String,
      name: json['name'] as String,
      type: json['type'] as String,
      confidence: (json['confidence'] as num).toDouble(),
      mentions:
          (json['mentions'] as List<dynamic>).map((e) => e as String).toList(),
    );

Map<String, dynamic> _$EntityToJson(Entity instance) => <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'type': instance.type,
      'confidence': instance.confidence,
      'mentions': instance.mentions,
    };
