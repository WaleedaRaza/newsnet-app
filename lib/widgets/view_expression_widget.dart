import 'package:flutter/material.dart';
import '../models/user_views.dart';

class ViewExpressionWidget extends StatefulWidget {
  final IssueView issue;
  final Function(IssueView) onViewChanged;
  final bool showConfidence;
  final bool showInterest;

  const ViewExpressionWidget({
    super.key,
    required this.issue,
    required this.onViewChanged,
    this.showConfidence = true,
    this.showInterest = true,
  });

  @override
  State<ViewExpressionWidget> createState() => _ViewExpressionWidgetState();
}

class _ViewExpressionWidgetState extends State<ViewExpressionWidget> {
  late IssueView _currentIssue;
  ViewExpressionMethod _selectedMethod = ViewExpressionMethod.stanceSlider;

  @override
  void initState() {
    super.initState();
    _currentIssue = widget.issue;
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 8, horizontal: 16),
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Issue Header
            _buildIssueHeader(),
            const SizedBox(height: 16),
            
            // Expression Method Selector
            _buildMethodSelector(),
            const SizedBox(height: 16),
            
            // Expression Widget based on selected method
            _buildExpressionWidget(),
            const SizedBox(height: 16),

            // User Statement Text Field
            Text(
              'In your own words, how do you feel about this issue?',
              style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 8),
            TextField(
              minLines: 2,
              maxLines: 4,
              decoration: InputDecoration(
                hintText: 'Type your thoughts or beliefs here... (optional)',
                border: OutlineInputBorder(),
                contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 12),
              ),
              controller: TextEditingController(text: _currentIssue.userStatement ?? ""),
              onChanged: (value) {
                setState(() {
                  _currentIssue = _currentIssue.copyWith(
                    userStatement: value,
                    lastUpdated: DateTime.now(),
                  );
                });
              },
            ),
            const SizedBox(height: 16),
            
            // Confidence Level (if enabled)
            if (widget.showConfidence) ...[
              _buildConfidenceSelector(),
              const SizedBox(height: 16),
            ],
            
            // Interest Level (if enabled)
            if (widget.showInterest) ...[
              _buildInterestSelector(),
              const SizedBox(height: 16),
            ],
            
            // Save Button
            _buildSaveButton(),
          ],
        ),
      ),
    );
  }

  Widget _buildIssueHeader() {
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: Theme.of(context).primaryColor.withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Text(
            _currentIssue.categoryName,
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: Theme.of(context).primaryColor,
            ),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Text(
            _currentIssue.issueName,
            style: const TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildMethodSelector() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'How would you like to express your view?',
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 8),
        Wrap(
          spacing: 8,
          children: ViewExpressionMethod.values.map((method) {
            final isSelected = _selectedMethod == method;
            return ChoiceChip(
              label: Text(_getMethodLabel(method)),
              selected: isSelected,
              onSelected: (selected) {
                if (selected) {
                  setState(() {
                    _selectedMethod = method;
                  });
                }
              },
            );
          }).toList(),
        ),
      ],
    );
  }

  Widget _buildExpressionWidget() {
    switch (_selectedMethod) {
      case ViewExpressionMethod.stanceSlider:
        return _buildStanceSlider();
      case ViewExpressionMethod.multipleChoice:
        return _buildMultipleChoice();
      case ViewExpressionMethod.confidenceLevel:
        return _buildConfidenceSlider();
      case ViewExpressionMethod.interestLevel:
        return _buildInterestSlider();
    }
  }

  Widget _buildStanceSlider() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Your stance on this issue:',
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 8),
        SliderTheme(
          data: SliderTheme.of(context).copyWith(
            activeTrackColor: Theme.of(context).primaryColor,
            inactiveTrackColor: Colors.grey[300],
            thumbColor: Theme.of(context).primaryColor,
            overlayColor: Theme.of(context).primaryColor.withOpacity(0.2),
            valueIndicatorColor: Theme.of(context).primaryColor,
            valueIndicatorTextStyle: const TextStyle(
              color: Colors.white,
              fontSize: 14,
              fontWeight: FontWeight.bold,
            ),
          ),
          child: Slider(
            value: _currentIssue.stanceValue ?? 5.0,
            min: 1.0,
            max: 10.0,
            divisions: 9,
            label: _getStanceLabel(_currentIssue.stanceValue ?? 5.0),
            onChanged: (value) {
              setState(() {
                _currentIssue = _currentIssue.copyWith(
                  stanceValue: value,
                  stanceLevel: _getStanceLevelFromValue(value),
                  lastUpdated: DateTime.now(),
                );
              });
            },
          ),
        ),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text('Strongly Oppose', style: TextStyle(fontSize: 12)),
            const Text('Neutral', style: TextStyle(fontSize: 12)),
            const Text('Strongly Support', style: TextStyle(fontSize: 12)),
          ],
        ),
        const SizedBox(height: 8),
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: _getStanceColor(_currentIssue.stanceValue ?? 5.0).withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(
              color: _getStanceColor(_currentIssue.stanceValue ?? 5.0),
              width: 1,
            ),
          ),
          child: Row(
            children: [
              Icon(
                _getStanceIcon(_currentIssue.stanceValue ?? 5.0),
                color: _getStanceColor(_currentIssue.stanceValue ?? 5.0),
                size: 20,
              ),
              const SizedBox(width: 8),
              Text(
                _getStanceLabel(_currentIssue.stanceValue ?? 5.0),
                style: TextStyle(
                  fontWeight: FontWeight.w600,
                  color: _getStanceColor(_currentIssue.stanceValue ?? 5.0),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildMultipleChoice() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Select your stance:',
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 8),
        ...StanceLevel.values.map((stance) {
          return RadioListTile<StanceLevel>(
            title: Text(_getStanceLevelLabel(stance)),
            value: stance,
            groupValue: _currentIssue.stanceLevel,
            onChanged: (value) {
              setState(() {
                _currentIssue = _currentIssue.copyWith(
                  stanceLevel: value,
                  stanceValue: _getStanceValueFromLevel(value!),
                  lastUpdated: DateTime.now(),
                );
              });
            },
            activeColor: Theme.of(context).primaryColor,
          );
        }).toList(),
      ],
    );
  }

  Widget _buildConfidenceSlider() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'How certain are you about your view?',
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 8),
        SliderTheme(
          data: SliderTheme.of(context).copyWith(
            activeTrackColor: Colors.orange,
            inactiveTrackColor: Colors.grey[300],
            thumbColor: Colors.orange,
            overlayColor: Colors.orange.withOpacity(0.2),
          ),
          child: Slider(
            value: (_currentIssue.confidenceLevel?.index ?? 2).toDouble(),
            min: 0.0,
            max: 4.0,
            divisions: 4,
            label: _getConfidenceLabel(_currentIssue.confidenceLevel ?? ConfidenceLevel.somewhatCertain),
            onChanged: (value) {
              setState(() {
                _currentIssue = _currentIssue.copyWith(
                  confidenceLevel: ConfidenceLevel.values[value.round()],
                  lastUpdated: DateTime.now(),
                );
              });
            },
          ),
        ),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text('Very Uncertain', style: TextStyle(fontSize: 12)),
            const Text('Very Certain', style: TextStyle(fontSize: 12)),
          ],
        ),
      ],
    );
  }

  Widget _buildInterestSlider() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'How much do you care about this issue?',
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 8),
        SliderTheme(
          data: SliderTheme.of(context).copyWith(
            activeTrackColor: Colors.green,
            inactiveTrackColor: Colors.grey[300],
            thumbColor: Colors.green,
            overlayColor: Colors.green.withOpacity(0.2),
          ),
          child: Slider(
            value: (_currentIssue.interestLevel?.index ?? 2).toDouble(),
            min: 0.0,
            max: 4.0,
            divisions: 4,
            label: _getInterestLabel(_currentIssue.interestLevel ?? InterestLevel.interested),
            onChanged: (value) {
              setState(() {
                _currentIssue = _currentIssue.copyWith(
                  interestLevel: InterestLevel.values[value.round()],
                  lastUpdated: DateTime.now(),
                );
              });
            },
          ),
        ),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text('Not Interested', style: TextStyle(fontSize: 12)),
            const Text('Extremely Interested', style: TextStyle(fontSize: 12)),
          ],
        ),
      ],
    );
  }

  Widget _buildConfidenceSelector() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'How certain are you about your view?',
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 8),
        Wrap(
          spacing: 8,
          children: ConfidenceLevel.values.map((level) {
            final isSelected = _currentIssue.confidenceLevel == level;
            return ChoiceChip(
              label: Text(_getConfidenceLabel(level)),
              selected: isSelected,
              onSelected: (selected) {
                if (selected) {
                  setState(() {
                    _currentIssue = _currentIssue.copyWith(
                      confidenceLevel: level,
                      lastUpdated: DateTime.now(),
                    );
                  });
                }
              },
            );
          }).toList(),
        ),
      ],
    );
  }

  Widget _buildInterestSelector() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'How much do you care about this issue?',
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 8),
        Wrap(
          spacing: 8,
          children: InterestLevel.values.map((level) {
            final isSelected = _currentIssue.interestLevel == level;
            return ChoiceChip(
              label: Text(_getInterestLabel(level)),
              selected: isSelected,
              onSelected: (selected) {
                if (selected) {
                  setState(() {
                    _currentIssue = _currentIssue.copyWith(
                      interestLevel: level,
                      lastUpdated: DateTime.now(),
                    );
                  });
                }
              },
            );
          }).toList(),
        ),
      ],
    );
  }

  Widget _buildSaveButton() {
    final hasChanges = _currentIssue.stanceValue != widget.issue.stanceValue ||
        _currentIssue.stanceLevel != widget.issue.stanceLevel ||
        _currentIssue.confidenceLevel != widget.issue.confidenceLevel ||
        _currentIssue.interestLevel != widget.issue.interestLevel;

    return SizedBox(
      width: double.infinity,
      child: ElevatedButton(
        onPressed: hasChanges ? () {
          widget.onViewChanged(_currentIssue);
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('View saved successfully!'),
              backgroundColor: Colors.green,
            ),
          );
        } : null,
        style: ElevatedButton.styleFrom(
          padding: const EdgeInsets.symmetric(vertical: 12),
          backgroundColor: Theme.of(context).primaryColor,
          foregroundColor: Colors.white,
        ),
        child: const Text(
          'Save View',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
    );
  }

  // Helper methods
  String _getMethodLabel(ViewExpressionMethod method) {
    switch (method) {
      case ViewExpressionMethod.stanceSlider:
        return 'Slider';
      case ViewExpressionMethod.multipleChoice:
        return 'Multiple Choice';
      case ViewExpressionMethod.confidenceLevel:
        return 'Confidence';
      case ViewExpressionMethod.interestLevel:
        return 'Interest';
    }
  }

  String _getStanceLabel(double value) {
    if (value <= 2) return 'Strongly Oppose';
    if (value <= 4) return 'Oppose';
    if (value <= 6) return 'Neutral';
    if (value <= 8) return 'Support';
    return 'Strongly Support';
  }

  StanceLevel _getStanceLevelFromValue(double value) {
    if (value <= 2) return StanceLevel.stronglyOppose;
    if (value <= 4) return StanceLevel.oppose;
    if (value <= 6) return StanceLevel.neutral;
    if (value <= 8) return StanceLevel.support;
    return StanceLevel.stronglySupport;
  }

  double _getStanceValueFromLevel(StanceLevel level) {
    switch (level) {
      case StanceLevel.stronglyOppose:
        return 1.0;
      case StanceLevel.oppose:
        return 3.0;
      case StanceLevel.neutral:
        return 5.0;
      case StanceLevel.support:
        return 7.0;
      case StanceLevel.stronglySupport:
        return 9.0;
    }
  }

  String _getStanceLevelLabel(StanceLevel level) {
    switch (level) {
      case StanceLevel.stronglyOppose:
        return 'Strongly Oppose';
      case StanceLevel.oppose:
        return 'Oppose';
      case StanceLevel.neutral:
        return 'Neutral';
      case StanceLevel.support:
        return 'Support';
      case StanceLevel.stronglySupport:
        return 'Strongly Support';
    }
  }

  String _getConfidenceLabel(ConfidenceLevel level) {
    switch (level) {
      case ConfidenceLevel.veryUncertain:
        return 'Very Uncertain';
      case ConfidenceLevel.uncertain:
        return 'Uncertain';
      case ConfidenceLevel.somewhatCertain:
        return 'Somewhat Certain';
      case ConfidenceLevel.certain:
        return 'Certain';
      case ConfidenceLevel.veryCertain:
        return 'Very Certain';
    }
  }

  String _getInterestLabel(InterestLevel level) {
    switch (level) {
      case InterestLevel.notInterested:
        return 'Not Interested';
      case InterestLevel.somewhatInterested:
        return 'Somewhat Interested';
      case InterestLevel.interested:
        return 'Interested';
      case InterestLevel.veryInterested:
        return 'Very Interested';
      case InterestLevel.extremelyInterested:
        return 'Extremely Interested';
    }
  }

  Color _getStanceColor(double value) {
    if (value <= 2) return Colors.red;
    if (value <= 4) return Colors.orange;
    if (value <= 6) return Colors.grey;
    if (value <= 8) return Colors.lightGreen;
    return Colors.green;
  }

  IconData _getStanceIcon(double value) {
    if (value <= 2) return Icons.thumb_down;
    if (value <= 4) return Icons.thumb_down_outlined;
    if (value <= 6) return Icons.remove;
    if (value <= 8) return Icons.thumb_up_outlined;
    return Icons.thumb_up;
  }
} 