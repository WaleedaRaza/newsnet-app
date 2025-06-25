import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../core/constants.dart';
import '../providers/user_provider.dart';

class ChatScreen extends ConsumerStatefulWidget {
  final String storyId;

  const ChatScreen({super.key, required this.storyId});

  @override
  ConsumerState<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends ConsumerState<ChatScreen> {
  final _messageController = TextEditingController();
  final List<ChatMessage> _messages = [];
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _addWelcomeMessage();
  }

  @override
  void dispose() {
    _messageController.dispose();
    super.dispose();
  }

  void _addWelcomeMessage() {
    _messages.add(ChatMessage(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      content: "Hello! I'm NewsNet AI. Ask me anything about this story and I'll respond based on your bias settings.",
      isUser: false,
      timestamp: DateTime.now(),
    ));
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final biasValue = ref.watch(biasNotifierProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Chat with NewsNet AI'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              setState(() {
                _messages.clear();
                _addWelcomeMessage();
              });
            },
          ),
        ],
      ),
      body: Column(
        children: [
          // Bias indicator
          Container(
            padding: const EdgeInsets.all(AppConstants.defaultPadding),
            decoration: BoxDecoration(
              color: theme.colorScheme.surface,
              border: Border(
                bottom: BorderSide(
                  color: theme.colorScheme.outline.withOpacity(0.2),
                ),
              ),
            ),
            child: Row(
              children: [
                Icon(
                  Icons.psychology,
                  size: 16,
                  color: theme.colorScheme.primary,
                ),
                const SizedBox(width: 8),
                Text(
                  'AI responding with: ',
                  style: theme.textTheme.bodySmall,
                ),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: _getBiasColor(biasValue).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                      color: _getBiasColor(biasValue).withOpacity(0.3),
                    ),
                  ),
                  child: Text(
                    _getBiasLabel(biasValue),
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: _getBiasColor(biasValue),
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ],
            ),
          ),
          
          // Chat messages
          Expanded(
            child: ListView.builder(
              reverse: true,
              padding: const EdgeInsets.all(AppConstants.defaultPadding),
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                final message = _messages[_messages.length - 1 - index];
                return _ChatMessageWidget(message: message, theme: theme);
              },
            ),
          ),
          
          // Input area
          Container(
            padding: const EdgeInsets.all(AppConstants.defaultPadding),
            decoration: BoxDecoration(
              color: theme.colorScheme.surface,
              border: Border(
                top: BorderSide(
                  color: theme.colorScheme.outline.withOpacity(0.2),
                ),
              ),
            ),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _messageController,
                    decoration: const InputDecoration(
                      hintText: 'Ask me about this story...',
                      border: OutlineInputBorder(),
                    ),
                    onSubmitted: _handleSendMessage,
                  ),
                ),
                const SizedBox(width: 8),
                IconButton(
                  onPressed: _isLoading ? null : () => _handleSendMessage(_messageController.text),
                  icon: _isLoading 
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.send),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  void _handleSendMessage(String text) async {
    if (text.trim().isEmpty) return;

    final userMessage = ChatMessage(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      content: text,
      isUser: true,
      timestamp: DateTime.now(),
    );

    setState(() {
      _messages.add(userMessage);
      _isLoading = true;
    });

    _messageController.clear();

    // Simulate AI response
    await Future.delayed(const Duration(seconds: 1));
    
    final biasValue = ref.read(biasNotifierProvider);
    final aiResponse = _generateAIResponse(text, biasValue);
    
    final aiMessage = ChatMessage(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      content: aiResponse,
      isUser: false,
      timestamp: DateTime.now(),
    );

    setState(() {
      _messages.add(aiMessage);
      _isLoading = false;
    });
  }

  String _generateAIResponse(String userMessage, double biasValue) {
    // Simple response generation based on bias
    final responses = [
      "That's an interesting question! Based on the available information, I'd say...",
      "From what I can analyze, the situation appears to be...",
      "Looking at the facts, it seems that...",
      "Based on the evidence presented, I believe...",
    ];
    
    final biasResponses = [
      "I understand your perspective, but let me challenge that view...",
      "That's a valid point, though there might be another angle...",
      "I see where you're coming from, and I'd like to add...",
      "You raise a good question. Let me provide some additional context...",
    ];
    
    if (biasValue < 0.5) {
      return biasResponses[DateTime.now().millisecondsSinceEpoch % biasResponses.length];
    } else {
      return responses[DateTime.now().millisecondsSinceEpoch % responses.length];
    }
  }

  Color _getBiasColor(double bias) {
    if (bias <= 0.25) return Colors.red;
    if (bias <= 0.5) return Colors.orange;
    if (bias <= 0.75) return Colors.blue;
    return Colors.green;
  }

  String _getBiasLabel(double bias) {
    if (bias <= 0.25) return 'Challenge Me';
    if (bias <= 0.5) return 'Question';
    if (bias <= 0.75) return 'Support';
    return 'Prove Me Right';
  }
}

class ChatMessage {
  final String id;
  final String content;
  final bool isUser;
  final DateTime timestamp;

  ChatMessage({
    required this.id,
    required this.content,
    required this.isUser,
    required this.timestamp,
  });
}

class _ChatMessageWidget extends StatelessWidget {
  final ChatMessage message;
  final ThemeData theme;

  const _ChatMessageWidget({
    required this.message,
    required this.theme,
  });

  @override
  Widget build(BuildContext context) {
    final isUser = message.isUser;
    
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        children: [
          if (!isUser) ...[
            CircleAvatar(
              radius: 16,
              backgroundColor: theme.colorScheme.primary,
              child: Text(
                'AI',
                style: TextStyle(
                  color: theme.colorScheme.onPrimary,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            const SizedBox(width: 8),
          ],
          Flexible(
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              decoration: BoxDecoration(
                color: isUser 
                  ? theme.colorScheme.primary 
                  : theme.colorScheme.surface,
                borderRadius: BorderRadius.circular(20),
                border: !isUser ? Border.all(
                  color: theme.colorScheme.outline.withOpacity(0.2),
                ) : null,
              ),
              child: Text(
                message.content,
                style: TextStyle(
                  color: isUser 
                    ? theme.colorScheme.onPrimary 
                    : theme.colorScheme.onSurface,
                ),
              ),
            ),
          ),
          if (isUser) ...[
            const SizedBox(width: 8),
            CircleAvatar(
              radius: 16,
              backgroundColor: theme.colorScheme.secondary,
              child: Text(
                'You',
                style: TextStyle(
                  color: theme.colorScheme.onSecondary,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }
} 