import 'package:flutter/material.dart';
import 'dart:async';

class NewsSearchBar extends StatefulWidget {
  final TextEditingController controller;
  final Function(String) onSearch;

  const NewsSearchBar({
    super.key,
    required this.controller,
    required this.onSearch,
  });

  @override
  State<NewsSearchBar> createState() => _NewsSearchBarState();
}

class _NewsSearchBarState extends State<NewsSearchBar> {
  Timer? _debounceTimer;

  @override
  void dispose() {
    _debounceTimer?.cancel();
    super.dispose();
  }

  void _onSearchChanged(String value) {
    // Cancel previous timer
    _debounceTimer?.cancel();
    
    // Only search if there's actual text
    if (value.trim().isNotEmpty) {
      // Set a timer to search after user stops typing for 1 second
      _debounceTimer = Timer(const Duration(milliseconds: 1000), () {
        widget.onSearch(value.trim());
      });
    }
  }

  void _onSubmitted(String value) {
    // Cancel any pending timer
    _debounceTimer?.cancel();
    
    // Search immediately on submit
    if (value.trim().isNotEmpty) {
      widget.onSearch(value.trim());
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return Container(
      decoration: BoxDecoration(
        color: theme.colorScheme.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: theme.colorScheme.outline.withOpacity(0.3),
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: TextField(
        controller: widget.controller,
        decoration: InputDecoration(
          hintText: 'Search news...',
          hintStyle: TextStyle(
            color: theme.colorScheme.onSurfaceVariant.withOpacity(0.7),
          ),
          prefixIcon: Icon(
            Icons.search,
            color: theme.colorScheme.onSurfaceVariant,
          ),
          suffixIcon: widget.controller.text.isNotEmpty
              ? IconButton(
                  icon: Icon(
                    Icons.clear,
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                  onPressed: () {
                    widget.controller.clear();
                    _debounceTimer?.cancel();
                    setState(() {});
                  },
                )
              : null,
          border: InputBorder.none,
          contentPadding: const EdgeInsets.symmetric(
            horizontal: 16,
            vertical: 12,
          ),
        ),
        onChanged: _onSearchChanged,
        onSubmitted: _onSubmitted,
        textInputAction: TextInputAction.search,
      ),
    );
  }
} 