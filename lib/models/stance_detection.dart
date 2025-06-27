import 'package:json_annotation/json_annotation.dart';

part 'stance_detection.g.dart';

@JsonSerializable()
class StanceDetectionRequest {
  final String belief;
  final String articleText;
  final String methodPreference;

  const StanceDetectionRequest({
    required this.belief,
    required this.articleText,
    this.methodPreference = 'auto',
  });

  factory StanceDetectionRequest.fromJson(Map<String, dynamic> json) =>
      _$StanceDetectionRequestFromJson(json);

  Map<String, dynamic> toJson() => _$StanceDetectionRequestToJson(this);
}

@JsonSerializable()
class StanceDetectionResponse {
  final String belief;
  final String articleText;
  final String stance;
  final double confidence;
  final String method;
  final List<String> evidence;
  final double processingTime;
  final Map<String, dynamic>? metadata;

  const StanceDetectionResponse({
    required this.belief,
    required this.articleText,
    required this.stance,
    required this.confidence,
    required this.method,
    required this.evidence,
    required this.processingTime,
    this.metadata,
  });

  factory StanceDetectionResponse.fromJson(Map<String, dynamic> json) =>
      _$StanceDetectionResponseFromJson(json);

  Map<String, dynamic> toJson() => _$StanceDetectionResponseToJson(this);

  // Helper getters
  bool get isSupport => stance.toLowerCase() == 'support';
  bool get isOppose => stance.toLowerCase() == 'oppose';
  bool get isNeutral => stance.toLowerCase() == 'neutral';
  
  String get stanceDisplay {
    switch (stance.toLowerCase()) {
      case 'support':
        return 'Supports';
      case 'oppose':
        return 'Opposes';
      case 'neutral':
        return 'Neutral';
      default:
        return stance;
    }
  }

  String get confidenceDisplay => '${(confidence * 100).toInt()}%';
}

@JsonSerializable()
class BeliefStatement {
  final String text;
  final String category;
  final double strength;
  final String source;
  final Map<String, dynamic>? metadata;

  const BeliefStatement({
    required this.text,
    required this.category,
    this.strength = 0.5,
    this.source = 'user_input',
    this.metadata,
  });

  factory BeliefStatement.fromJson(Map<String, dynamic> json) =>
      _$BeliefStatementFromJson(json);

  Map<String, dynamic> toJson() => _$BeliefStatementToJson(this);
}

@JsonSerializable()
class UserBeliefFingerprint {
  final String userId;
  final List<BeliefStatement> beliefs;
  final List<String> categories;
  final DateTime lastUpdated;

  const UserBeliefFingerprint({
    required this.userId,
    required this.beliefs,
    required this.categories,
    required this.lastUpdated,
  });

  factory UserBeliefFingerprint.fromJson(Map<String, dynamic> json) =>
      _$UserBeliefFingerprintFromJson(json);

  Map<String, dynamic> toJson() => _$UserBeliefFingerprintToJson(this);
}

@JsonSerializable()
class ContentScoringRequest {
  final String userId;
  final String contentText;
  final Map<String, dynamic>? contentMetadata;

  const ContentScoringRequest({
    required this.userId,
    required this.contentText,
    this.contentMetadata,
  });

  factory ContentScoringRequest.fromJson(Map<String, dynamic> json) =>
      _$ContentScoringRequestFromJson(json);

  Map<String, dynamic> toJson() => _$ContentScoringRequestToJson(this);
}

@JsonSerializable()
class ContentScoringResponse {
  final String contentId;
  final String contentType;
  final double proximityScore;
  final double stanceAlignment;
  final double overallScore;
  final List<String> evidence;
  final Map<String, dynamic>? metadata;

  const ContentScoringResponse({
    required this.contentId,
    required this.contentType,
    required this.proximityScore,
    required this.stanceAlignment,
    required this.overallScore,
    required this.evidence,
    this.metadata,
  });

  factory ContentScoringResponse.fromJson(Map<String, dynamic> json) =>
      _$ContentScoringResponseFromJson(json);

  Map<String, dynamic> toJson() => _$ContentScoringResponseToJson(this);
}

// Predefined belief categories for easy selection
class BeliefCategories {
  static const List<String> categories = [
    'politics',
    'economics',
    'social_issues',
    'environment',
    'health',
    'technology',
    'education',
    'foreign_policy',
    'domestic_policy',
    'civil_rights',
    'national_security',
    'immigration',
    'taxation',
    'healthcare',
    'climate_change',
    'gun_control',
    'abortion',
    'religion',
    'media',
    'science',
  ];

  static const Map<String, List<String>> categoryExamples = {
    'politics': [
      'Democracy is the best form of government',
      'Political parties are necessary for democracy',
      'Term limits should be implemented for politicians',
    ],
    'economics': [
      'Free market capitalism is the best economic system',
      'Government regulation is necessary for economic stability',
      'Universal basic income would improve society',
    ],
    'social_issues': [
      'Diversity and inclusion improve organizations',
      'Traditional family values are important',
      'Social media has a negative impact on society',
    ],
    'environment': [
      'Climate change is primarily caused by human activities',
      'Environmental regulations hurt economic growth',
      'Renewable energy is the future of power generation',
    ],
    'health': [
      'Universal healthcare would improve health outcomes',
      'Alternative medicine is as effective as conventional medicine',
      'Mental health should be treated like physical health',
    ],
    'technology': [
      'Artificial intelligence will improve human life',
      'Social media companies should be more regulated',
      'Technology is making us more isolated',
    ],
  };
} 