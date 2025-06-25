import 'package:json_annotation/json_annotation.dart';

part 'story.g.dart';

@JsonSerializable()
class Story {
  final String id;
  final String eventKey;
  final String title;
  final String summaryNeutral;
  final String summaryModulated;
  final List<String> sources;
  final List<TimelineChunk> timelineChunks;
  final String? embeddingId;
  final DateTime publishedAt;
  final DateTime updatedAt;
  final List<String> topics;
  final double confidence;

  const Story({
    required this.id,
    required this.eventKey,
    required this.title,
    required this.summaryNeutral,
    required this.summaryModulated,
    required this.sources,
    required this.timelineChunks,
    this.embeddingId,
    required this.publishedAt,
    required this.updatedAt,
    required this.topics,
    required this.confidence,
  });

  factory Story.fromJson(Map<String, dynamic> json) => _$StoryFromJson(json);

  Map<String, dynamic> toJson() => _$StoryToJson(this);

  Story copyWith({
    String? id,
    String? eventKey,
    String? title,
    String? summaryNeutral,
    String? summaryModulated,
    List<String>? sources,
    List<TimelineChunk>? timelineChunks,
    String? embeddingId,
    DateTime? publishedAt,
    DateTime? updatedAt,
    List<String>? topics,
    double? confidence,
  }) {
    return Story(
      id: id ?? this.id,
      eventKey: eventKey ?? this.eventKey,
      title: title ?? this.title,
      summaryNeutral: summaryNeutral ?? this.summaryNeutral,
      summaryModulated: summaryModulated ?? this.summaryModulated,
      sources: sources ?? this.sources,
      timelineChunks: timelineChunks ?? this.timelineChunks,
      embeddingId: embeddingId ?? this.embeddingId,
      publishedAt: publishedAt ?? this.publishedAt,
      updatedAt: updatedAt ?? this.updatedAt,
      topics: topics ?? this.topics,
      confidence: confidence ?? this.confidence,
    );
  }
}

@JsonSerializable()
class TimelineChunk {
  final String id;
  final DateTime timestamp;
  final String content;
  final List<String> sources;
  final double confidence;
  final bool hasContradictions;
  final List<String> contradictions;

  const TimelineChunk({
    required this.id,
    required this.timestamp,
    required this.content,
    required this.sources,
    required this.confidence,
    required this.hasContradictions,
    required this.contradictions,
  });

  factory TimelineChunk.fromJson(Map<String, dynamic> json) =>
      _$TimelineChunkFromJson(json);

  Map<String, dynamic> toJson() => _$TimelineChunkToJson(this);
}

@JsonSerializable()
class Source {
  final String id;
  final String name;
  final String url;
  final String? icon;
  final double reliability;
  final String? bias;

  const Source({
    required this.id,
    required this.name,
    required this.url,
    this.icon,
    required this.reliability,
    this.bias,
  });

  factory Source.fromJson(Map<String, dynamic> json) => _$SourceFromJson(json);

  Map<String, dynamic> toJson() => _$SourceToJson(this);
} 