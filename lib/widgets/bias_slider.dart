import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../core/constants.dart';
import '../core/utils.dart';

class BiasSlider extends ConsumerStatefulWidget {
  final double value;
  final ValueChanged<double> onChanged;
  final bool showLabels;
  final bool enabled;

  const BiasSlider({
    super.key,
    required this.value,
    required this.onChanged,
    this.showLabels = true,
    this.enabled = true,
  });

  @override
  ConsumerState<BiasSlider> createState() => _BiasSliderState();
}

class _BiasSliderState extends ConsumerState<BiasSlider>
    with TickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _scaleAnimation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: AppConstants.shortAnimation,
      vsync: this,
    );
    _scaleAnimation = Tween<double>(begin: 1.0, end: 1.1).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final biasLabel = AppUtils.getBiasLabel(widget.value);
    final biasColor = AppUtils.getBiasColor(widget.value);

    return Column(
      children: [
        if (widget.showLabels) ...[
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Challenge Me',
                style: theme.textTheme.bodySmall?.copyWith(
                  color: Colors.red.shade400,
                  fontWeight: FontWeight.w500,
                ),
              ),
              Text(
                'Prove Me Right',
                style: theme.textTheme.bodySmall?.copyWith(
                  color: Colors.green.shade400,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
        ],
        
        Container(
          height: AppConstants.sliderHeight,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(AppConstants.borderRadius),
            color: theme.colorScheme.surface,
            border: Border.all(
              color: theme.colorScheme.outline.withOpacity(0.2),
            ),
          ),
          child: Stack(
            children: [
              // Background gradient
              Container(
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(AppConstants.borderRadius),
                  gradient: LinearGradient(
                    colors: [
                      Colors.red.shade100,
                      Colors.orange.shade100,
                      Colors.blue.shade100,
                      Colors.green.shade100,
                    ],
                    stops: const [0.0, 0.25, 0.75, 1.0],
                  ),
                ),
              ),
              
              // Slider
              SliderTheme(
                data: SliderTheme.of(context).copyWith(
                  trackHeight: 4,
                  thumbShape: const RoundSliderThumbShape(enabledThumbRadius: 12),
                  overlayShape: const RoundSliderOverlayShape(overlayRadius: 24),
                  activeTrackColor: biasColor,
                  inactiveTrackColor: Colors.transparent,
                  thumbColor: biasColor,
                  overlayColor: biasColor.withOpacity(0.2),
                ),
                child: Slider(
                  value: widget.value,
                  min: 0.0,
                  max: 1.0,
                  divisions: 100,
                  onChanged: widget.enabled ? (value) {
                    widget.onChanged(value);
                    _animationController.forward().then((_) {
                      _animationController.reverse();
                    });
                  } : null,
                ),
              ),
            ],
          ),
        ),
        
        const SizedBox(height: 12),
        
        // Current bias indicator
        AnimatedBuilder(
          animation: _scaleAnimation,
          builder: (context, child) {
            return Transform.scale(
              scale: _scaleAnimation.value,
              child: Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 8,
                ),
                decoration: BoxDecoration(
                  color: biasColor.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(
                    color: biasColor.withOpacity(0.3),
                  ),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      _getBiasIcon(widget.value),
                      size: 16,
                      color: biasColor,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      biasLabel,
                      style: theme.textTheme.bodyMedium?.copyWith(
                        color: biasColor,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
              ),
            );
          },
        ),
      ],
    );
  }

  IconData _getBiasIcon(double value) {
    if (value <= 0.25) return Icons.help_outline;
    if (value <= 0.5) return Icons.question_mark;
    if (value <= 0.75) return Icons.thumb_up_outlined;
    return Icons.verified;
  }
}

class BiasSliderCard extends StatelessWidget {
  final double value;
  final ValueChanged<double> onChanged;
  final String title;
  final String? subtitle;

  const BiasSliderCard({
    super.key,
    required this.value,
    required this.onChanged,
    required this.title,
    this.subtitle,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(AppConstants.defaultPadding),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.tune,
                  color: theme.colorScheme.primary,
                  size: 20,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        title,
                        style: theme.textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      if (subtitle != null) ...[
                        const SizedBox(height: 2),
                        Text(
                          subtitle!,
                          style: theme.textTheme.bodySmall?.copyWith(
                            color: theme.colorScheme.onSurfaceVariant,
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            BiasSlider(
              value: value,
              onChanged: onChanged,
            ),
          ],
        ),
      ),
    );
  }
} 