import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

class OnboardingScreen extends StatefulWidget {
  const OnboardingScreen({super.key});

  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen> {
  final _supabase = Supabase.instance.client;
  final _nameController = TextEditingController();
  bool _saving = false;

  // Q1 — interests (multi-select)
  final _selectedInterests = <String>{};
  static const _interestOptions = [
    ('Historical & Ancient', 'historical_sites'),
    ('Outdoor & Nature', 'outdoor_nature'),
    ('Food & Culture', 'food_culture'),
    ('Adventure & Sports', 'adventure'),
    ('Religious & Spiritual', 'religious_spiritual'),
    ('Modern & Nightlife', 'modern_entertainment'),
  ];

  // Q2 — pace
  String _pace = 'balanced';

  // Q3 — budget
  String _budgetSensitivity = 'moderate';
  double _budgetAmount = 150.0;

  // Q4 — companions
  String _companions = 'solo';

  // Q5 — mobility
  String _mobility = 'Full mobility';

  @override
  void dispose() {
    _nameController.dispose();
    super.dispose();
  }

  Map<String, double> _buildInterestScores() {
    return {
      for (final opt in _interestOptions)
        opt.$2: _selectedInterests.contains(opt.$2) ? 0.9 : 0.1,
    };
  }

  Map<String, dynamic> _buildCompanions() {
    return switch (_companions) {
      'family' => {'type': 'family', 'has_children': true},
      _ => {'type': _companions},
    };
  }

  Future<void> _save() async {
    final name = _nameController.text.trim();
    if (name.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter your name')),
      );
      return;
    }

    setState(() => _saving = true);
    try {
      final userId = _supabase.auth.currentUser!.id;
      await _supabase.from('user_profiles').update({
        'full_name': name,
        'interest_scores': _buildInterestScores(),
        'itinerary_pace': _pace,
        'price_sensitivity': _budgetSensitivity,
        'trip_budget_estimate': _budgetAmount,
        'typical_companions': _buildCompanions(),
        'mobility_preference': _mobility,
      }).eq('user_id', userId);
      // StreamBuilder in main.dart will now route to MainShell
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Could not save preferences: $e'),
            backgroundColor: Colors.red,
          ),
        );
        setState(() => _saving = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Let\'s get to know you'),
        backgroundColor: Colors.deepOrange,
        foregroundColor: Colors.white,
        automaticallyImplyLeading: false,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Tell us about your travel style so CLEO can personalise everything for you.',
                style: TextStyle(color: Colors.grey, fontSize: 14),
              ),
              const SizedBox(height: 28),

              // Name
              _SectionHeader(label: 'What should we call you?'),
              const SizedBox(height: 10),
              TextField(
                controller: _nameController,
                textInputAction: TextInputAction.done,
                decoration: const InputDecoration(
                  hintText: 'Your name',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.person_outline),
                ),
              ),

              const SizedBox(height: 28),

              // Q1 — Interests
              _SectionHeader(label: 'What draws you most? (pick all that apply)'),
              const SizedBox(height: 10),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: _interestOptions.map((opt) {
                  final selected = _selectedInterests.contains(opt.$2);
                  return FilterChip(
                    label: Text(opt.$1),
                    selected: selected,
                    selectedColor: Colors.deepOrange.withOpacity(0.2),
                    checkmarkColor: Colors.deepOrange,
                    onSelected: (v) => setState(() {
                      if (v) {
                        _selectedInterests.add(opt.$2);
                      } else {
                        _selectedInterests.remove(opt.$2);
                      }
                    }),
                  );
                }).toList(),
              ),

              const SizedBox(height: 28),

              // Q2 — Pace
              _SectionHeader(label: 'Travel pace?'),
              const SizedBox(height: 10),
              _OptionRow(
                options: const [
                  ('Relaxed', 'slow_flexible'),
                  ('Balanced', 'balanced'),
                  ('Packed', 'packed_schedule'),
                ],
                selected: _pace,
                onSelect: (v) => setState(() => _pace = v),
              ),

              const SizedBox(height: 28),

              // Q3 — Budget
              _SectionHeader(label: 'Budget level?'),
              const SizedBox(height: 10),
              _OptionRow(
                options: const [
                  ('Budget', 'budget'),
                  ('Moderate', 'moderate'),
                  ('Luxury', 'luxury'),
                ],
                selected: _budgetSensitivity,
                onSelect: (v) => setState(() {
                  _budgetSensitivity = v;
                  _budgetAmount = switch (v) {
                    'budget' => 50.0,
                    'luxury' => 400.0,
                    _ => 150.0,
                  };
                }),
              ),

              const SizedBox(height: 28),

              // Q4 — Companions
              _SectionHeader(label: 'Who do you travel with?'),
              const SizedBox(height: 10),
              _OptionRow(
                options: const [
                  ('Solo', 'solo'),
                  ('Couple', 'couple'),
                  ('Family', 'family'),
                  ('Group', 'group'),
                ],
                selected: _companions,
                onSelect: (v) => setState(() => _companions = v),
              ),

              const SizedBox(height: 28),

              // Q5 — Mobility
              _SectionHeader(label: 'Any mobility needs?'),
              const SizedBox(height: 10),
              _OptionRow(
                options: const [
                  ('None', 'Full mobility'),
                  ('Limited walking', 'Limited walking'),
                  ('Wheelchair', 'Wheelchair accessible only'),
                ],
                selected: _mobility,
                onSelect: (v) => setState(() => _mobility = v),
              ),

              const SizedBox(height: 36),

              SizedBox(
                width: double.infinity,
                height: 52,
                child: FilledButton(
                  onPressed: _saving ? null : _save,
                  style: FilledButton.styleFrom(
                    backgroundColor: Colors.deepOrange,
                  ),
                  child: _saving
                      ? const SizedBox(
                          width: 22,
                          height: 22,
                          child: CircularProgressIndicator(
                              strokeWidth: 2, color: Colors.white),
                        )
                      : const Text('Done — let\'s explore Egypt!',
                          style: TextStyle(fontSize: 16)),
                ),
              ),
              const SizedBox(height: 16),
            ],
          ),
        ),
      ),
    );
  }
}

class _SectionHeader extends StatelessWidget {
  final String label;
  const _SectionHeader({required this.label});

  @override
  Widget build(BuildContext context) {
    return Text(
      label,
      style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 15),
    );
  }
}

class _OptionRow extends StatelessWidget {
  final List<(String, String)> options;
  final String selected;
  final ValueChanged<String> onSelect;

  const _OptionRow({
    required this.options,
    required this.selected,
    required this.onSelect,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: options.map((opt) {
        final isSelected = selected == opt.$2;
        return Expanded(
          child: Padding(
            padding: const EdgeInsets.only(right: 6),
            child: OutlinedButton(
              onPressed: () => onSelect(opt.$2),
              style: OutlinedButton.styleFrom(
                backgroundColor:
                    isSelected ? Colors.deepOrange.withOpacity(0.1) : null,
                side: BorderSide(
                  color: isSelected ? Colors.deepOrange : Colors.grey.shade300,
                  width: isSelected ? 2 : 1,
                ),
                padding: const EdgeInsets.symmetric(vertical: 10),
              ),
              child: Text(
                opt.$1,
                style: TextStyle(
                  fontSize: 13,
                  color: isSelected ? Colors.deepOrange : Colors.black87,
                  fontWeight:
                      isSelected ? FontWeight.w600 : FontWeight.normal,
                ),
                textAlign: TextAlign.center,
              ),
            ),
          ),
        );
      }).toList(),
    );
  }
}
