import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

class AppUtils {
  // Date formatting
  static String formatDate(DateTime date) {
    return DateFormat('MMM dd, yyyy').format(date);
  }

  static String formatDateTime(DateTime date) {
    return DateFormat('MMM dd, yyyy • HH:mm').format(date);
  }

  static String formatRelativeTime(DateTime date) {
    final now = DateTime.now();
    final difference = now.difference(date);

    if (difference.inDays > 0) {
      return '${difference.inDays}d ago';
    } else if (difference.inHours > 0) {
      return '${difference.inHours}h ago';
    } else if (difference.inMinutes > 0) {
      return '${difference.inMinutes}m ago';
    } else {
      return 'Just now';
    }
  }

  // Text utilities
  static String truncateText(String text, int maxLength) {
    if (text.length <= maxLength) return text;
    return '${text.substring(0, maxLength)}...';
  }

  static String capitalizeFirst(String text) {
    if (text.isEmpty) return text;
    return text[0].toUpperCase() + text.substring(1);
  }

  // Color utilities
  static Color getBiasColor(double biasValue) {
    if (biasValue <= 0.25) {
      return Colors.red.shade400;
    } else if (biasValue <= 0.5) {
      return Colors.orange.shade400;
    } else if (biasValue <= 0.75) {
      return Colors.blue.shade400;
    } else {
      return Colors.green.shade400;
    }
  }

  static String getBiasLabel(double biasValue) {
    if (biasValue <= 0.25) {
      return 'Challenge Me';
    } else if (biasValue <= 0.5) {
      return 'Question';
    } else if (biasValue <= 0.75) {
      return 'Support';
    } else {
      return 'Prove Me Right';
    }
  }

  // Validation utilities
  static bool isValidEmail(String email) {
    return RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$').hasMatch(email);
  }

  static bool isValidUrl(String url) {
    try {
      Uri.parse(url);
      return true;
    } catch (e) {
      return false;
    }
  }

  // UI utilities
  static void showSnackBar(BuildContext context, String message, {bool isError = false}) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: isError ? Colors.red : Colors.green,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
      ),
    );
  }

  static void showLoadingDialog(BuildContext context, String message) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        content: Row(
          children: [
            const CircularProgressIndicator(),
            const SizedBox(width: 16),
            Text(message),
          ],
        ),
      ),
    );
  }

  // Source utilities
  static String getSourceDisplayName(String source) {
    final sourceMap = {
      'nytimes': 'The New York Times',
      'reuters': 'Reuters',
      'bbc': 'BBC News',
      'cnn': 'CNN',
      'foxnews': 'Fox News',
      'npr': 'NPR',
      'ap': 'Associated Press',
      'bloomberg': 'Bloomberg',
      'wsj': 'The Wall Street Journal',
      'washingtonpost': 'The Washington Post',
    };

    return sourceMap[source.toLowerCase()] ?? source;
  }

  static String getSourceIcon(String source) {
    final sourceIcons = {
      'nytimes': '📰',
      'reuters': '🌐',
      'bbc': '🇬🇧',
      'cnn': '📺',
      'foxnews': '🦊',
      'npr': '🎙️',
      'ap': '📡',
      'bloomberg': '💼',
      'wsj': '📊',
      'washingtonpost': '🏛️',
    };

    return sourceIcons[source.toLowerCase()] ?? '📄';
  }
} 