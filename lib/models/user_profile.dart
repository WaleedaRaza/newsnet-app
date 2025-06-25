import 'package:json_annotation/json_annotation.dart';

part 'user_profile.g.dart';

@JsonSerializable()
class UserProfile {
  final String id;
  final String email;
  final String? name;
  final List<String> interests;
  final Map<String, List<String>> beliefFingerprint;
  final double biasSetting;
  final DateTime createdAt;
  final DateTime updatedAt;

  const UserProfile({
    required this.id,
    required this.email,
    this.name,
    required this.interests,
    required this.beliefFingerprint,
    required this.biasSetting,
    required this.createdAt,
    required this.updatedAt,
  });

  factory UserProfile.fromJson(Map<String, dynamic> json) =>
      _$UserProfileFromJson(json);

  Map<String, dynamic> toJson() => _$UserProfileToJson(this);

  UserProfile copyWith({
    String? id,
    String? email,
    String? name,
    List<String>? interests,
    Map<String, List<String>>? beliefFingerprint,
    double? biasSetting,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return UserProfile(
      id: id ?? this.id,
      email: email ?? this.email,
      name: name ?? this.name,
      interests: interests ?? this.interests,
      beliefFingerprint: beliefFingerprint ?? this.beliefFingerprint,
      biasSetting: biasSetting ?? this.biasSetting,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  List<String> getBeliefsForTopic(String topic) {
    return beliefFingerprint[topic] ?? [];
  }

  void addBelief(String topic, String belief) {
    final currentBeliefs = beliefFingerprint[topic] ?? [];
    if (!currentBeliefs.contains(belief)) {
      beliefFingerprint[topic] = [...currentBeliefs, belief];
    }
  }

  void removeBelief(String topic, String belief) {
    final currentBeliefs = beliefFingerprint[topic] ?? [];
    beliefFingerprint[topic] = currentBeliefs.where((b) => b != belief).toList();
  }
} 