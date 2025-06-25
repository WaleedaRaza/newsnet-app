import 'package:json_annotation/json_annotation.dart';

part 'article.g.dart';

@JsonSerializable()
class Article {
  final String id;
  final String title;
  final String content;
  final String url;
  final String sourceName;
  final String sourceDomain;
  final String? sourceBias;
  final double sourceReliability;
  final List<String> topics;
  final DateTime publishedAt;
  
  // Scoring fields
  final double topicalScore;
  final double beliefAlignmentScore;
  final double ideologicalScore;
  final double finalScore;
  
  final DateTime createdAt;

  Article({
    required this.id,
    required this.title,
    required this.content,
    required this.url,
    required this.sourceName,
    required this.sourceDomain,
    this.sourceBias,
    required this.sourceReliability,
    required this.topics,
    required this.publishedAt,
    required this.topicalScore,
    required this.beliefAlignmentScore,
    required this.ideologicalScore,
    required this.finalScore,
    required this.createdAt,
  });

  factory Article.fromJson(Map<String, dynamic> json) => _$ArticleFromJson(json);
  Map<String, dynamic> toJson() => _$ArticleToJson(this);
}

@JsonSerializable()
class ArticleAggregationRequest {
  final List<String> topics;
  final Map<String, List<String>> beliefs;
  final double bias;
  final int limitPerTopic;

  ArticleAggregationRequest({
    required this.topics,
    required this.beliefs,
    required this.bias,
    this.limitPerTopic = 10,
  });

  factory ArticleAggregationRequest.fromJson(Map<String, dynamic> json) => 
      _$ArticleAggregationRequestFromJson(json);
  Map<String, dynamic> toJson() => _$ArticleAggregationRequestToJson(this);
}

@JsonSerializable()
class ArticleAggregationResponse {
  final List<Article> articles;
  final int totalArticles;
  final List<String> topicsCovered;
  final double aggregationTime;

  ArticleAggregationResponse({
    required this.articles,
    required this.totalArticles,
    required this.topicsCovered,
    required this.aggregationTime,
  });

  factory ArticleAggregationResponse.fromJson(Map<String, dynamic> json) => 
      _$ArticleAggregationResponseFromJson(json);
  Map<String, dynamic> toJson() => _$ArticleAggregationResponseToJson(this);
} 