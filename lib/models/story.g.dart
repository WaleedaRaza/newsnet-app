// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'story.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Story _$StoryFromJson(Map<String, dynamic> json) => Story(
      id: json['id'] as String,
      eventKey: json['eventKey'] as String,
      title: json['title'] as String,
      summaryNeutral: json['summaryNeutral'] as String,
      summaryModulated: json['summaryModulated'] as String,
      sources:
          (json['sources'] as List<dynamic>).map((e) => e as String).toList(),
      timelineChunks: (json['timelineChunks'] as List<dynamic>)
          .map((e) => TimelineChunk.fromJson(e as Map<String, dynamic>))
          .toList(),
      embeddingId: json['embeddingId'] as String?,
      publishedAt: DateTime.parse(json['publishedAt'] as String),
      updatedAt: DateTime.parse(json['updatedAt'] as String),
      topics:
          (json['topics'] as List<dynamic>).map((e) => e as String).toList(),
      confidence: (json['confidence'] as num).toDouble(),
    );

Map<String, dynamic> _$StoryToJson(Story instance) => <String, dynamic>{
      'id': instance.id,
      'eventKey': instance.eventKey,
      'title': instance.title,
      'summaryNeutral': instance.summaryNeutral,
      'summaryModulated': instance.summaryModulated,
      'sources': instance.sources,
      'timelineChunks': instance.timelineChunks,
      'embeddingId': instance.embeddingId,
      'publishedAt': instance.publishedAt.toIso8601String(),
      'updatedAt': instance.updatedAt.toIso8601String(),
      'topics': instance.topics,
      'confidence': instance.confidence,
    };

TimelineChunk _$TimelineChunkFromJson(Map<String, dynamic> json) =>
    TimelineChunk(
      id: json['id'] as String,
      timestamp: DateTime.parse(json['timestamp'] as String),
      content: json['content'] as String,
      sources:
          (json['sources'] as List<dynamic>).map((e) => e as String).toList(),
      confidence: (json['confidence'] as num).toDouble(),
      hasContradictions: json['hasContradictions'] as bool,
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
      'hasContradictions': instance.hasContradictions,
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
