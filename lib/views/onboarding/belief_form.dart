import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/constants.dart';
import '../../core/utils.dart';
import '../../providers/user_provider.dart';
import '../../widgets/bias_slider.dart';

class BeliefForm extends ConsumerStatefulWidget {
  const BeliefForm({super.key});

  @override
  ConsumerState<BeliefForm> createState() => _BeliefFormState();
}

class _BeliefFormState extends ConsumerState<BeliefForm> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  
  final List<String> _selectedTopics = [];
  final Map<String, List<String>> _beliefs = {};
  double _biasSetting = AppConstants.defaultBiasSetting;
  
  bool _isLoading = false;
  bool _isSignUp = true;

  @override
  void dispose() {
    _nameController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('Set Up Your Profile'),
        leading: IconButton(
          icon: const Icon(Icons.close),
          onPressed: () => context.pop(),
        ),
      ),
      body: Form(
        key: _formKey,
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(AppConstants.defaultPadding),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Welcome section
              _buildWelcomeSection(theme),
              
              const SizedBox(height: 32),
              
              // Auth section
              _buildAuthSection(theme),
              
              const SizedBox(height: 32),
              
              // Topics section
              _buildTopicsSection(theme),
              
              const SizedBox(height: 32),
              
              // Bias setting
              _buildBiasSection(theme),
              
              const SizedBox(height: 32),
              
              // Beliefs section
              _buildBeliefsSection(theme),
              
              const SizedBox(height: 32),
              
              // Submit button
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _isLoading ? null : _submitForm,
                  child: _isLoading
                      ? const CircularProgressIndicator()
                      : Text(_isSignUp ? 'Create Account' : 'Sign In'),
                ),
              ),
              
              const SizedBox(height: 16),
              
              // Toggle sign up/sign in
              Center(
                child: TextButton(
                  onPressed: () {
                    setState(() {
                      _isSignUp = !_isSignUp;
                    });
                  },
                  child: Text(
                    _isSignUp
                        ? 'Already have an account? Sign In'
                        : 'Don\'t have an account? Sign Up',
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildWelcomeSection(ThemeData theme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(
          Icons.psychology,
          size: 48,
          color: theme.colorScheme.primary,
        ),
        const SizedBox(height: 16),
        Text(
          'Welcome to NewsNet',
          style: theme.textTheme.headlineSmall?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          'Help us understand your worldview so we can provide personalized news narratives that match your perspective.',
          style: theme.textTheme.bodyMedium?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
      ],
    );
  }

  Widget _buildAuthSection(ThemeData theme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Account Information',
          style: theme.textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 16),
        
        if (_isSignUp) ...[
          TextFormField(
            controller: _nameController,
            decoration: const InputDecoration(
              labelText: 'Full Name (Optional)',
              prefixIcon: Icon(Icons.person),
            ),
          ),
          const SizedBox(height: 16),
        ],
        
        TextFormField(
          controller: _emailController,
          decoration: const InputDecoration(
            labelText: 'Email',
            prefixIcon: Icon(Icons.email),
          ),
          keyboardType: TextInputType.emailAddress,
          validator: (value) {
            if (value == null || value.isEmpty) {
              return 'Please enter your email';
            }
            if (!AppUtils.isValidEmail(value)) {
              return 'Please enter a valid email';
            }
            return null;
          },
        ),
        const SizedBox(height: 16),
        
        TextFormField(
          controller: _passwordController,
          decoration: const InputDecoration(
            labelText: 'Password',
            prefixIcon: Icon(Icons.lock),
          ),
          obscureText: true,
          validator: (value) {
            if (value == null || value.isEmpty) {
              return 'Please enter your password';
            }
            if (value.length < 6) {
              return 'Password must be at least 6 characters';
            }
            return null;
          },
        ),
      ],
    );
  }

  Widget _buildTopicsSection(ThemeData theme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Topics of Interest',
          style: theme.textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          'Select topics you\'re most interested in following:',
          style: theme.textTheme.bodySmall?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
        const SizedBox(height: 16),
        
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: TopicCategories.available.map((topic) {
            final isSelected = _selectedTopics.contains(topic);
            return FilterChip(
              label: Text(AppUtils.capitalizeFirst(topic)),
              selected: isSelected,
              onSelected: (selected) {
                setState(() {
                  if (selected) {
                    _selectedTopics.add(topic);
                  } else {
                    _selectedTopics.remove(topic);
                  }
                });
              },
            );
          }).toList(),
        ),
      ],
    );
  }

  Widget _buildBiasSection(ThemeData theme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Default Bias Setting',
          style: theme.textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          'How would you like stories to be framed by default?',
          style: theme.textTheme.bodySmall?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
        const SizedBox(height: 16),
        
        BiasSliderCard(
          value: _biasSetting,
          onChanged: (value) {
            setState(() {
              _biasSetting = value;
            });
          },
          title: 'Narrative Bias',
          subtitle: 'Challenge me vs Prove me right',
        ),
      ],
    );
  }

  Widget _buildBeliefsSection(ThemeData theme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Your Beliefs & Convictions',
          style: theme.textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          'Share your key beliefs for each topic to help us personalize your news experience:',
          style: theme.textTheme.bodySmall?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
        const SizedBox(height: 16),
        
        ..._selectedTopics.map((topic) => _buildTopicBeliefs(topic, theme)),
      ],
    );
  }

  Widget _buildTopicBeliefs(String topic, ThemeData theme) {
    final beliefs = _beliefs[topic] ?? [];
    
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Padding(
        padding: const EdgeInsets.all(AppConstants.defaultPadding),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              AppUtils.capitalizeFirst(topic),
              style: theme.textTheme.titleSmall?.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 12),
            
            // Belief input
            Row(
              children: [
                Expanded(
                  child: TextFormField(
                    decoration: InputDecoration(
                      hintText: 'Add a belief about $topic...',
                      suffixIcon: IconButton(
                        icon: const Icon(Icons.add),
                        onPressed: () => _addBelief(topic),
                      ),
                    ),
                    onFieldSubmitted: (_) => _addBelief(topic),
                  ),
                ),
              ],
            ),
            
            // Existing beliefs
            if (beliefs.isNotEmpty) ...[
              const SizedBox(height: 12),
              Wrap(
                spacing: 8,
                runSpacing: 4,
                children: beliefs.map((belief) => Chip(
                  label: Text(belief),
                  deleteIcon: const Icon(Icons.close, size: 16),
                  onDeleted: () => _removeBelief(topic, belief),
                )).toList(),
              ),
            ],
          ],
        ),
      ),
    );
  }

  void _addBelief(String topic) {
    // This would get the belief from a text field
    // For now, adding a placeholder belief
    setState(() {
      if (!_beliefs.containsKey(topic)) {
        _beliefs[topic] = [];
      }
      _beliefs[topic]!.add('Sample belief about $topic');
    });
  }

  void _removeBelief(String topic, String belief) {
    setState(() {
      _beliefs[topic]?.remove(belief);
    });
  }

  Future<void> _submitForm() async {
    if (!_formKey.currentState!.validate()) return;
    if (_selectedTopics.isEmpty) {
      AppUtils.showSnackBar(
        context,
        'Please select at least one topic of interest',
        isError: true,
      );
      return;
    }

    setState(() {
      _isLoading = true;
    });

    try {
      if (_isSignUp) {
        await ref.read(userNotifierProvider.notifier).register(
          _emailController.text,
          _passwordController.text,
          name: _nameController.text.isNotEmpty ? _nameController.text : null,
        );
      } else {
        await ref.read(userNotifierProvider.notifier).login(
          _emailController.text,
          _passwordController.text,
        );
      }

      // Update user profile with beliefs and bias
      final user = ref.read(userNotifierProvider).value;
      if (user != null) {
        await ref.read(userNotifierProvider.notifier).updateProfile(
          user.copyWith(
            interests: _selectedTopics,
            beliefFingerprint: _beliefs,
            biasSetting: _biasSetting,
          ),
        );
      }

      // Update bias setting
      ref.read(biasNotifierProvider.notifier).setBias(_biasSetting);

      if (mounted) {
        context.pop();
        AppUtils.showSnackBar(
          context,
          'Profile set up successfully!',
        );
      }
    } catch (e) {
      if (mounted) {
        AppUtils.showSnackBar(
          context,
          e.toString(),
          isError: true,
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }
} 