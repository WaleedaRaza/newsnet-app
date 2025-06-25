// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'story.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Story _$StoryFromJson(Map<String, dynamic> json) => Story(
      id: json['id'] as String,
      eventKey: json['event_key'] as String,
      title: json['title'] as String,
      summaryNeutral: json['summary_neutral'] as String,
      summaryModulated: json['summary_modulated'] as String,
      sources:
          (json['sources'] as List<dynamic>).map((e) => e as String).toList(),
      timelineChunks: (json['timeline_chunks'] as List<dynamic>)
          .map((e) => TimelineChunk.fromJson(e as Map<String, dynamic>))
          .toList(),
      embeddingId: json['embedding_id'] as String?,
      publishedAt: DateTime.parse(json['published_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
      topics:
          (json['topics'] as List<dynamic>).map((e) => e as String).toList(),
      confidence: (json['confidence'] as num).toDouble(),
      url: json['url'] as String?,
    );

Map<String, dynamic> _$StoryToJson(Story instance) => <String, dynamic>{
      'id': instance.id,
      'event_key': instance.eventKey,
      'title': instance.title,
      'summary_neutral': instance.summaryNeutral,
      'summary_modulated': instance.summaryModulated,
      'sources': instance.sources,
      'timeline_chunks': instance.timelineChunks,
      'embedding_id': instance.embeddingId,
      'published_at': instance.publishedAt.toIso8601String(),
      'updated_at': instance.updatedAt.toIso8601String(),
      'topics': instance.topics,
      'confidence': instance.confidence,
      'url': instance.url,
    };

TimelineChunk _$TimelineChunkFromJson(Map<String, dynamic> json) =>
    TimelineChunk(
      id: json['id'] as String,
      timestamp: DateTime.parse(json['timestamp'] as String),
      content: json['content'] as String,
      sources:
          (json['sources'] as List<dynamic>).map((e) => e as String).toList(),
      confidence: (json['confidence'] as num).toDouble(),
      hasContradictions: json['has_contradictions'] as bool,
      contradictions: (json['contradictions'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
    );

Map<String, dynamic> _$TimelineChunkToJson(TimelineChunk instance) =>
    <String, dynamic>{
      'id': instance.id,
      'timestamp': instance.timestamp.toIso8601String(),
      'content': instance.content,
      'sources': instance.sources,
      'confidence': instance.confidence,
      'has_contradictions': instance.hasContradictions,
      'contradictions': instance.contradictions,
    };

Source _$SourceFromJson(Map<String, dynamic> json) => Source(
      id: json['id'] as String,
      name: json['name'] as String,
      url: json['url'] as String,
      icon: json['icon'] as String?,
      reliability: (json['reliability'] as num).toDouble(),
      bias: json['bias'] as String?,
    );

Map<String, dynamic> _$SourceToJson(Source instance) => <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'url': instance.url,
      'icon': instance.icon,
      'reliability': instance.reliability,
      'bias': instance.bias,
    };
