// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'article.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Article _$ArticleFromJson(Map<String, dynamic> json) => Article(
      title: json['title'] as String,
      description: json['description'] as String,
      url: json['url'] as String,
      urlToImage: json['urlToImage'] as String?,
      publishedAt: json['publishedAt'] as String?,
      source: Source.fromJson(json['source'] as Map<String, dynamic>),
      biasAnalysis: json['biasAnalysis'] == null
          ? null
          : BiasAnalysis.fromJson(json['biasAnalysis'] as Map<String, dynamic>),
      stance: json['stance'] as String?,
      stanceConfidence: (json['stanceConfidence'] as num?)?.toDouble(),
      relevanceScore: (json['relevanceScore'] as num?)?.toDouble(),
    );

Map<String, dynamic> _$ArticleToJson(Article instance) => <String, dynamic>{
      'title': instance.title,
      'description': instance.description,
      'url': instance.url,
      'urlToImage': instance.urlToImage,
      'publishedAt': instance.publishedAt,
      'source': instance.source,
      'biasAnalysis': instance.biasAnalysis,
      'stance': instance.stance,
      'stanceConfidence': instance.stanceConfidence,
      'relevanceScore': instance.relevanceScore,
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
