import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/stance_detection.dart';
import '../providers/stance_detection_provider.dart';
import '../core/theme.dart';

class StanceDetectionScreen extends ConsumerStatefulWidget {
  const StanceDetectionScreen({super.key});

  @override
  ConsumerState<StanceDetectionScreen> createState() => _StanceDetectionScreenState();
}

class _StanceDetectionScreenState extends ConsumerState<StanceDetectionScreen> {
  final _beliefController = TextEditingController();
  final _articleController = TextEditingController();
  String _selectedMethod = 'auto';
  final List<BeliefStatement> _userBeliefs = [];

  @override
  void dispose() {
    _beliefController.dispose();
    _articleController.dispose();
    super.dispose();
  }

  Future<void> _detectStance() async {
    if (_beliefController.text.trim().isEmpty || _articleController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter both a belief and article text')),
      );
      return;
    }

    await ref.read(stanceDetectionResultsProvider.notifier).detectStance(
      belief: _beliefController.text.trim(),
      articleText: _articleController.text.trim(),
      methodPreference: _selectedMethod,
    );
  }

  void _addBelief() {
    if (_beliefController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter a belief statement')),
      );
      return;
    }

    final belief = BeliefStatement(
      text: _beliefController.text.trim(),
      category: 'politics', // Default category
      strength: 0.5,
    );

    setState(() {
      _userBeliefs.add(belief);
      _beliefController.clear();
    });
  }

  @override
  Widget build(BuildContext context) {
    final stanceResults = ref.watch(stanceDetectionResultsProvider);
    final isAvailable = ref.watch(stanceDetectionAvailableProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Stance Detection'),
        backgroundColor: AppTheme.primaryColor,
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Service Status
            isAvailable.when(
              data: (available) => Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: available ? Colors.green[50] : Colors.red[50],
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(
                    color: available ? Colors.green[300]! : Colors.red[300]!,
                  ),
                ),
                child: Row(
                  children: [
                    Icon(
                      available ? Icons.check_circle : Icons.error,
                      color: available ? Colors.green[700] : Colors.red[700],
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        available ? 'Stance detection service available' : 'Stance detection service unavailable',
                        style: TextStyle(
                          color: available ? Colors.green[700] : Colors.red[700],
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (_, __) => const SizedBox.shrink(),
            ),
            
            const SizedBox(height: 24),
            
            // Belief Input Section
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Enter Your Belief',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    TextField(
                      controller: _beliefController,
                      maxLines: 3,
                      decoration: const InputDecoration(
                        hintText: 'e.g., "Climate change is primarily caused by human activities"',
                        border: OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 16),
                    Text(
                      'Article Text to Analyze',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    TextField(
                      controller: _articleController,
                      maxLines: 5,
                      decoration: const InputDecoration(
                        hintText: 'Paste the article text you want to analyze...',
                        border: OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 16),
                    Row(
                      children: [
                        Text(
                          'Detection Method:',
                          style: Theme.of(context).textTheme.titleSmall,
                        ),
                        const SizedBox(width: 16),
                        DropdownButton<String>(
                          value: _selectedMethod,
                          items: const [
                            DropdownMenuItem(value: 'auto', child: Text('Auto')),
                            DropdownMenuItem(value: 'nli', child: Text('NLI Model')),
                            DropdownMenuItem(value: 'rules', child: Text('Rule-based')),
                            DropdownMenuItem(value: 'keywords', child: Text('Keywords')),
                          ],
                          onChanged: (value) {
                            setState(() {
                              _selectedMethod = value!;
                            });
                          },
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton.icon(
                        onPressed: stanceResults.isLoading ? null : _detectStance,
                        icon: stanceResults.isLoading 
                            ? const SizedBox(
                                width: 16,
                                height: 16,
                                child: CircularProgressIndicator(strokeWidth: 2),
                              )
                            : const Icon(Icons.psychology),
                        label: Text(stanceResults.isLoading ? 'Analyzing...' : 'Detect Stance'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: AppTheme.primaryColor,
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 12),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            
            const SizedBox(height: 24),
            
            // Results Section
            stanceResults.when(
              data: (results) {
                if (results.isEmpty) {
                  return const SizedBox.shrink();
                }
                
                final result = results.first;
                
                return Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Icon(
                              _getStanceIcon(result.stance),
                              color: _getStanceColor(result.stance),
                              size: 24,
                            ),
                            const SizedBox(width: 8),
                            Text(
                              'Stance Analysis Result',
                              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 16),
                        
                        // Stance and Confidence
                        Row(
                          children: [
                            Expanded(
                              child: _buildInfoCard(
                                'Stance',
                                result.stanceDisplay,
                                _getStanceColor(result.stance),
                              ),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: _buildInfoCard(
                                'Confidence',
                                result.confidenceDisplay,
                                _getConfidenceColor(result.confidence),
                              ),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: _buildInfoCard(
                                'Method',
                                result.method.toUpperCase(),
                                Colors.grey[600]!,
                              ),
                            ),
                          ],
                        ),
                        
                        const SizedBox(height: 16),
                        
                        // Evidence Section
                        if (result.evidence.isNotEmpty) ...[
                          Text(
                            'Supporting Evidence:',
                            style: Theme.of(context).textTheme.titleSmall?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 8),
                          ...result.evidence.map((evidence) => Padding(
                            padding: const EdgeInsets.only(bottom: 8.0),
                            child: Container(
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                color: Colors.grey[100],
                                borderRadius: BorderRadius.circular(8),
                                border: Border.all(color: Colors.grey[300]!),
                              ),
                              child: Text(
                                '"$evidence"',
                                style: Theme.of(context).textTheme.bodyMedium,
                              ),
                            ),
                          )),
                        ],
                        
                        const SizedBox(height: 16),
                        
                        // Processing Time
                        Text(
                          'Analysis completed in ${result.processingTime.toStringAsFixed(2)} seconds',
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: Colors.grey[600],
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              },
              loading: () => const Card(
                child: Padding(
                  padding: EdgeInsets.all(16.0),
                  child: Center(
                    child: Column(
                      children: [
                        CircularProgressIndicator(),
                        SizedBox(height: 16),
                        Text('Analyzing stance...'),
                      ],
                    ),
                  ),
                ),
              ),
              error: (error, stack) => Card(
                color: Colors.red[50],
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(Icons.error, color: Colors.red[700]),
                          const SizedBox(width: 8),
                          Text(
                            'Analysis Failed',
                            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                              color: Colors.red[700],
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Text(
                        error.toString(),
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: Colors.red[700],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoCard(String label, String value, Color color) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        children: [
          Text(
            label,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: color,
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            value,
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
              color: color,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  IconData _getStanceIcon(String stance) {
    switch (stance.toLowerCase()) {
      case 'support':
        return Icons.thumb_up;
      case 'oppose':
        return Icons.thumb_down;
      case 'neutral':
        return Icons.remove;
      default:
        return Icons.help;
    }
  }

  Color _getStanceColor(String stance) {
    switch (stance.toLowerCase()) {
      case 'support':
        return Colors.green[700]!;
      case 'oppose':
        return Colors.red[700]!;
      case 'neutral':
        return Colors.grey[600]!;
      default:
        return Colors.grey[600]!;
    }
  }

  Color _getConfidenceColor(double confidence) {
    if (confidence >= 0.8) {
      return Colors.green[700]!;
    } else if (confidence >= 0.6) {
      return Colors.orange[700]!;
    } else {
      return Colors.red[700]!;
    }
  }
} 