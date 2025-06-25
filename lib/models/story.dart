import 'package:json_annotation/json_annotation.dart';

part 'story.g.dart';

@JsonSerializable()
class Story {
  @JsonKey(name: 'id')
  final String id;
  
  @JsonKey(name: 'event_key')
  final String eventKey;
  
  @JsonKey(name: 'title')
  final String title;
  
  @JsonKey(name: 'summary_neutral')
  final String summaryNeutral;
  
  @JsonKey(name: 'summary_modulated')
  final String summaryModulated;
  
  @JsonKey(name: 'sources')
  final List<String> sources;
  
  @JsonKey(name: 'timeline_chunks')
  final List<TimelineChunk> timelineChunks;
  
  @JsonKey(name: 'embedding_id')
  final String? embeddingId;
  
  @JsonKey(name: 'published_at')
  final DateTime publishedAt;
  
  @JsonKey(name: 'updated_at')
  final DateTime updatedAt;
  
  @JsonKey(name: 'topics')
  final List<String> topics;
  
  @JsonKey(name: 'confidence')
  final double confidence;

  @JsonKey(name: 'url')
  final String? url;

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
    this.url,
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
    String? url,
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
      url: url ?? this.url,
    );
  }
}

@JsonSerializable()
class TimelineChunk {
  @JsonKey(name: 'id')
  final String id;
  
  @JsonKey(name: 'timestamp')
  final DateTime timestamp;
  
  @JsonKey(name: 'content')
  final String content;
  
  @JsonKey(name: 'sources')
  final List<String> sources;
  
  @JsonKey(name: 'confidence')
  final double confidence;
  
  @JsonKey(name: 'has_contradictions')
  final bool hasContradictions;
  
  @JsonKey(name: 'contradictions')
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