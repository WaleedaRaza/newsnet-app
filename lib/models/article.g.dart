// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'article.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Article _$ArticleFromJson(Map<String, dynamic> json) => Article(
      id: json['id'] as String,
      title: json['title'] as String,
      content: json['content'] as String,
      url: json['url'] as String,
      sourceName: json['sourceName'] as String,
      sourceDomain: json['sourceDomain'] as String,
      sourceBias: json['sourceBias'] as String?,
      sourceReliability: (json['sourceReliability'] as num).toDouble(),
      topics:
          (json['topics'] as List<dynamic>).map((e) => e as String).toList(),
      publishedAt: DateTime.parse(json['publishedAt'] as String),
      topicalScore: (json['topicalScore'] as num).toDouble(),
      beliefAlignmentScore: (json['beliefAlignmentScore'] as num).toDouble(),
      ideologicalScore: (json['ideologicalScore'] as num).toDouble(),
      finalScore: (json['finalScore'] as num).toDouble(),
      createdAt: DateTime.parse(json['createdAt'] as String),
    );

Map<String, dynamic> _$ArticleToJson(Article instance) => <String, dynamic>{
      'id': instance.id,
      'title': instance.title,
      'content': instance.content,
      'url': instance.url,
      'sourceName': instance.sourceName,
      'sourceDomain': instance.sourceDomain,
      'sourceBias': instance.sourceBias,
      'sourceReliability': instance.sourceReliability,
      'topics': instance.topics,
      'publishedAt': instance.publishedAt.toIso8601String(),
      'topicalScore': instance.topicalScore,
      'beliefAlignmentScore': instance.beliefAlignmentScore,
      'ideologicalScore': instance.ideologicalScore,
      'finalScore': instance.finalScore,
      'createdAt': instance.createdAt.toIso8601String(),
    };

ArticleAggregationRequest _$ArticleAggregationRequestFromJson(
        Map<String, dynamic> json) =>
    ArticleAggregationRequest(
      topics:
          (json['topics'] as List<dynamic>).map((e) => e as String).toList(),
      beliefs: (json['beliefs'] as Map<String, dynamic>).map(
        (k, e) =>
            MapEntry(k, (e as List<dynamic>).map((e) => e as String).toList()),
      ),
      bias: (json['bias'] as num).toDouble(),
      limitPerTopic: (json['limitPerTopic'] as num?)?.toInt() ?? 10,
    );

Map<String, dynamic> _$ArticleAggregationRequestToJson(
        ArticleAggregationRequest instance) =>
    <String, dynamic>{
      'topics': instance.topics,
      'beliefs': instance.beliefs,
      'bias': instance.bias,
      'limitPerTopic': instance.limitPerTopic,
    };

ArticleAggregationResponse _$ArticleAggregationResponseFromJson(
        Map<String, dynamic> json) =>
    ArticleAggregationResponse(
      articles: (json['articles'] as List<dynamic>)
          .map((e) => Article.fromJson(e as Map<String, dynamic>))
          .toList(),
      totalArticles: (json['totalArticles'] as num).toInt(),
      topicsCovered: (json['topicsCovered'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
      aggregationTime: (json['aggregationTime'] as num).toDouble(),
    );

Map<String, dynamic> _$ArticleAggregationResponseToJson(
        ArticleAggregationResponse instance) =>
    <String, dynamic>{
      'articles': instance.articles,
      'totalArticles': instance.totalArticles,
      'topicsCovered': instance.topicsCovered,
      'aggregationTime': instance.aggregationTime,
    };
