import 'package:json_annotation/json_annotation.dart';

part 'fusion_result.g.dart';

@JsonSerializable()
class FusionResult {
  final String id;
  final String storyId;
  final String fusedNarrative;
  final String modulatedNarrative;
  final double biasLevel;
  final List<Contradiction> contradictions;
  final List<Entity> entities;
  final double confidence;
  final DateTime createdAt;

  const FusionResult({
    required this.id,
    required this.storyId,
    required this.fusedNarrative,
    required this.modulatedNarrative,
    required this.biasLevel,
    required this.contradictions,
    required this.entities,
    required this.confidence,
    required this.createdAt,
  });

  factory FusionResult.fromJson(Map<String, dynamic> json) =>
      _$FusionResultFromJson(json);

  Map<String, dynamic> toJson() => _$FusionResultToJson(this);
}

@JsonSerializable()
class Contradiction {
  final String id;
  final String description;
  final List<String> sources;
  final String resolution;
  final double severity;

  const Contradiction({
    required this.id,
    required this.description,
    required this.sources,
    required this.resolution,
    required this.severity,
  });

  factory Contradiction.fromJson(Map<String, dynamic> json) =>
      _$ContradictionFromJson(json);

  Map<String, dynamic> toJson() => _$ContradictionToJson(this);
}

@JsonSerializable()
class Entity {
  final String id;
  final String name;
  final String type;
  final double confidence;
  final List<String> mentions;

  const Entity({
    required this.id,
    required this.name,
    required this.type,
    required this.confidence,
    required this.mentions,
  });

  factory Entity.fromJson(Map<String, dynamic> json) => _$EntityFromJson(json);

  Map<String, dynamic> toJson() => _$EntityToJson(this);
} 