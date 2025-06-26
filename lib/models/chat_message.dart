import 'package:json_annotation/json_annotation.dart';

part 'chat_message.g.dart';

@JsonSerializable()
class ChatMessage {
  final String id;
  final String storyId;
  final String content;
  final bool isUser;
  final DateTime timestamp;
  final Map<String, dynamic>? sourceContext;

  ChatMessage({
    required this.id,
    required this.storyId,
    required this.content,
    required this.isUser,
    required this.timestamp,
    this.sourceContext,
  });

  factory ChatMessage.fromJson(Map<String, dynamic> json) => _$ChatMessageFromJson(json);
  Map<String, dynamic> toJson() => _$ChatMessageToJson(this);
} 