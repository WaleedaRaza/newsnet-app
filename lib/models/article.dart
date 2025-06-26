import 'package:json_annotation/json_annotation.dart';
import 'package:flutter/material.dart';

part 'article.g.dart';

@JsonSerializable()
class Article {
  final String title;
  final String description;
  final String url;
  final String? urlToImage;
  final String? publishedAt;
  final Source source;
  final BiasAnalysis? biasAnalysis;

  Article({
    required this.title,
    required this.description,
    required this.url,
    this.urlToImage,
    this.publishedAt,
    required this.source,
    this.biasAnalysis,
  });

  factory Article.fromJson(Map<String, dynamic> json) {
    return Article(
      title: json['title'] ?? '',
      description: json['description'] ?? '',
      url: json['url'] ?? '',
      urlToImage: json['urlToImage'],
      publishedAt: json['publishedAt'],
      source: Source.fromJson(json['source'] ?? {}),
      biasAnalysis: json['bias_analysis'] != null 
          ? BiasAnalysis.fromJson(json['bias_analysis']) 
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'title': title,
      'description': description,
      'url': url,
      'urlToImage': urlToImage,
      'publishedAt': publishedAt,
      'source': source.toJson(),
      'bias_analysis': biasAnalysis?.toJson(),
    };
  }
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

class Source {
  final String name;
  final String? domain;

  Source({required this.name, this.domain});

  factory Source.fromJson(Map<String, dynamic> json) {
    return Source(
      name: json['name'] ?? 'Unknown',
      domain: json['domain'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'domain': domain,
    };
  }
}

class BiasAnalysis {
  final String stance;
  final double stanceConfidence;
  final String stanceMethod;
  final List<String> stanceEvidence;
  final double biasMatch;
  final double userBiasPreference;
  final String userBelief;
  final String analysisMethod;
  final List<String> topicMentions;
  final double topicSentimentScore;
  final String topicSentiment;

  BiasAnalysis({
    required this.stance,
    required this.stanceConfidence,
    required this.stanceMethod,
    required this.stanceEvidence,
    required this.biasMatch,
    required this.userBiasPreference,
    required this.userBelief,
    required this.analysisMethod,
    this.topicMentions = const [],
    this.topicSentimentScore = 0.0,
    this.topicSentiment = 'neutral',
  });

  factory BiasAnalysis.fromJson(Map<String, dynamic> json) {
    return BiasAnalysis(
      stance: json['stance'] ?? 'neutral',
      stanceConfidence: (json['stance_confidence'] ?? 0.0).toDouble(),
      stanceMethod: json['stance_method'] ?? 'rule_based',
      stanceEvidence: List<String>.from(json['stance_evidence'] ?? []),
      biasMatch: (json['bias_match'] ?? 0.5).toDouble(),
      userBiasPreference: (json['user_bias_preference'] ?? 0.5).toDouble(),
      userBelief: json['user_belief'] ?? '',
      analysisMethod: json['analysis_method'] ?? 'stance_detection',
      topicMentions: List<String>.from(json['topic_mentions'] ?? []),
      topicSentimentScore: (json['topic_sentiment_score'] ?? 0.0).toDouble(),
      topicSentiment: json['topic_sentiment'] ?? 'neutral',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'stance': stance,
      'stance_confidence': stanceConfidence,
      'stance_method': stanceMethod,
      'stance_evidence': stanceEvidence,
      'bias_match': biasMatch,
      'user_bias_preference': userBiasPreference,
      'user_belief': userBelief,
      'analysis_method': analysisMethod,
      'topic_mentions': topicMentions,
      'topic_sentiment_score': topicSentimentScore,
      'topic_sentiment': topicSentiment,
    };
  }

  String get biasLabel {
    switch (stance) {
      case 'support':
        return 'Supports';
      case 'oppose':
        return 'Opposes';
      case 'neutral':
        return 'Neutral';
      default:
        return 'Neutral';
    }
  }

  String get confidenceLabel {
    if (stanceConfidence > 0.7) return 'High';
    if (stanceConfidence > 0.4) return 'Medium';
    return 'Low';
  }

  Color get sentimentColor {
    switch (stance) {
      case 'support':
        return Colors.green;
      case 'oppose':
        return Colors.red;
      case 'neutral':
        return Colors.grey;
      default:
        return Colors.grey;
    }
  }
} 