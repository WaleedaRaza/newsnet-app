import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_markdown/flutter_markdown.dart';

import '../core/constants.dart';
import '../core/utils.dart';
import '../models/story.dart';
import '../models/fusion_result.dart';
import '../providers/story_provider.dart';
import '../providers/user_provider.dart';
import '../widgets/bias_slider.dart';
import '../widgets/fused_summary_box.dart';

class StoryScreen extends ConsumerStatefulWidget {
  final String storyId;

  const StoryScreen({super.key, required this.storyId});

  @override
  ConsumerState<StoryScreen> createState() => _StoryScreenState();
}

class _StoryScreenState extends ConsumerState<StoryScreen>
    with TickerProviderStateMixin {
  late TabController _tabController;
  double _currentBias = 0.5;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final storyState = ref.watch(storyProvider(widget.storyId));
    final fusionState = ref.watch(fusionResultProvider(widget.storyId, _currentBias));
    final timelineState = ref.watch(timelineProvider(widget.storyId));

    return Scaffold(
      appBar: AppBar(
        title: const Text('Story Details'),
        actions: [
          IconButton(
            icon: const Icon(Icons.chat),
            onPressed: () => context.push('/chat/${widget.storyId}'),
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'Summary'),
            Tab(text: 'Timeline'),
            Tab(text: 'Sources'),
          ],
        ),
      ),
      body: storyState.when(
        data: (story) => Column(
          children: [
            // Bias slider
            BiasSliderCard(
              value: _currentBias,
              onChanged: (value) {
                setState(() {
                  _currentBias = value;
                });
              },
              title: 'Adjust Narrative Bias',
              subtitle: 'See how the story changes with different perspectives',
            ),
            
            // Content tabs
            Expanded(
              child: TabBarView(
                controller: _tabController,
                children: [
                  _buildSummaryTab(story, fusionState, theme),
                  _buildTimelineTab(timelineState, theme),
                  _buildSourcesTab(story, theme),
                ],
              ),
            ),
          ],
        ),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stack) => _buildErrorState(error, theme),
      ),
    );
  }

  Widget _buildSummaryTab(Story story, AsyncValue<FusionResult> fusionState, ThemeData theme) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppConstants.defaultPadding),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Story title
          Text(
            story.title,
            style: theme.textTheme.headlineSmall?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          
          const SizedBox(height: 8),
          
          // Story metadata
          Row(
            children: [
              Icon(
                Icons.schedule,
                size: 16,
                color: theme.colorScheme.onSurfaceVariant,
              ),
              const SizedBox(width: 4),
              Text(
                AppUtils.formatDateTime(story.publishedAt),
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
              const SizedBox(width: 16),
              Icon(
                Icons.source,
                size: 16,
                color: theme.colorScheme.onSurfaceVariant,
              ),
              const SizedBox(width: 4),
              Text(
                '${story.sources.length} sources',
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 24),
          
          // Fusion result
          fusionState.when(
            data: (fusionResult) => FusedSummaryBox(
              fusionResult: fusionResult,
              showContradictions: true,
            ),
            loading: () => const Center(
              child: Padding(
                padding: EdgeInsets.all(32),
                child: CircularProgressIndicator(),
              ),
            ),
            error: (error, stack) => Card(
              child: Padding(
                padding: const EdgeInsets.all(AppConstants.defaultPadding),
                child: Column(
                  children: [
                    Icon(
                      Icons.error_outline,
                      size: 48,
                      color: theme.colorScheme.error,
                    ),
                    const SizedBox(height: 16),
                    Text(
                      'Failed to load AI analysis',
                      style: theme.textTheme.titleMedium,
                    ),
                    const SizedBox(height: 8),
                    Text(
                      error.toString(),
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
          
          const SizedBox(height: 24),
          
          // Topics
          if (story.topics.isNotEmpty) ...[
            Text(
              'Topics',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 4,
              children: story.topics.map((topic) => Chip(
                label: Text(AppUtils.capitalizeFirst(topic)),
                backgroundColor: theme.colorScheme.primary.withOpacity(0.1),
              )).toList(),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildTimelineTab(AsyncValue<List<TimelineChunk>> timelineState, ThemeData theme) {
    return timelineState.when(
      data: (timelineChunks) => ListView.builder(
        padding: const EdgeInsets.all(AppConstants.defaultPadding),
        itemCount: timelineChunks.length,
        itemBuilder: (context, index) {
          final chunk = timelineChunks[index];
          return Card(
            margin: const EdgeInsets.only(bottom: 16),
            child: Padding(
              padding: const EdgeInsets.all(AppConstants.defaultPadding),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        width: 12,
                        height: 12,
                        decoration: BoxDecoration(
                          color: theme.colorScheme.primary,
                          shape: BoxShape.circle,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        AppUtils.formatDateTime(chunk.timestamp),
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: theme.colorScheme.onSurfaceVariant,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      const Spacer(),
                      if (chunk.hasContradictions)
                        Icon(
                          Icons.warning_amber,
                          size: 16,
                          color: theme.colorScheme.error,
                        ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Text(
                    chunk.content,
                    style: theme.textTheme.bodyMedium,
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Icon(
                        Icons.source,
                        size: 12,
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                      const SizedBox(width: 4),
                      Text(
                        '${chunk.sources.length} sources',
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: theme.colorScheme.onSurfaceVariant,
                        ),
                      ),
                      const Spacer(),
                      Text(
                        '${(chunk.confidence * 100).toInt()}% confidence',
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: chunk.confidence > 0.8 
                              ? Colors.green 
                              : theme.colorScheme.error,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          );
        },
      ),
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (error, stack) => _buildErrorState(error, theme),
    );
  }

  Widget _buildSourcesTab(Story story, ThemeData theme) {
    return ListView.builder(
      padding: const EdgeInsets.all(AppConstants.defaultPadding),
      itemCount: story.sources.length,
      itemBuilder: (context, index) {
        final source = story.sources[index];
        return Card(
          margin: const EdgeInsets.only(bottom: 8),
          child: ListTile(
            leading: CircleAvatar(
              child: Text(AppUtils.getSourceIcon(source)),
            ),
            title: Text(AppUtils.getSourceDisplayName(source)),
            subtitle: Text(source),
            trailing: Icon(
              Icons.open_in_new,
              color: theme.colorScheme.primary,
            ),
            onTap: () {
              // Open source URL
            },
          ),
        );
      },
    );
  }

  Widget _buildErrorState(Object error, ThemeData theme) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(AppConstants.defaultPadding),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.error_outline,
              size: 64,
              color: theme.colorScheme.error,
            ),
            const SizedBox(height: 16),
            Text(
              'Failed to load story',
              style: theme.textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            Text(
              error.toString(),
              textAlign: TextAlign.center,
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () => ref.invalidate(storyProvider(widget.storyId)),
              child: const Text('Try Again'),
            ),
          ],
        ),
      ),
    );
  }
} 