import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../../theme.dart';
import '../main_shell.dart';

class OnboardingScreen extends StatefulWidget {
  const OnboardingScreen({super.key});

  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen> {
  final _supabase = Supabase.instance.client;
  final _nameController = TextEditingController();
  bool _saving = false;

  // Q1 — interests
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

  // Q6 — planning style
  String _planningStyle = 'mix_of_planned_spontaneous';

  @override
  void dispose() {
    _nameController.dispose();
    super.dispose();
  }

  Map<String, dynamic> _buildTravelStyle() {
    return {
      'pace': _pace,
      'budget': _budgetSensitivity,
      'companions': _companions,
      'planning': _planningStyle,
    };
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
      await _supabase.from('user_profiles').upsert({
        'user_id': userId,
        'full_name': name,
        'interest_scores': _buildInterestScores(),
        'travel_style': _buildTravelStyle(),
        'itinerary_pace': _pace,
        'planning_style': _planningStyle,
        'price_sensitivity': _budgetSensitivity,
        'trip_budget_estimate': _budgetAmount,
        'typical_companions': _buildCompanions(),
        'mobility_preference': _mobility,
      }, onConflict: 'user_id');
      if (mounted) {
        Navigator.of(context).pushAndRemoveUntil(
          MaterialPageRoute(builder: (_) => const MainShell()),
          (_) => false,
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Could not save preferences: $e'),
            backgroundColor: VoyoColors.expedition,
          ),
        );
        setState(() => _saving = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: VoyoColors.page,
      appBar: AppBar(
        backgroundColor: VoyoColors.page,
        elevation: 0,
        automaticallyImplyLeading: false,
        title: Text(
          'Let\'s get to know you',
          style: GoogleFonts.fraunces(
            fontSize: 20,
            fontStyle: FontStyle.italic,
            color: VoyoColors.ink,
          ),
        ),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Tell us about your travel style so CLEO can personalise everything for you.',
                style: GoogleFonts.instrumentSans(
                  color: VoyoColors.stone,
                  fontSize: 14,
                  height: 1.5,
                ),
              ),
              const SizedBox(height: 28),

              // Name
              _header('What should we call you?'),
              const SizedBox(height: 10),
              TextField(
                controller: _nameController,
                textInputAction: TextInputAction.done,
                style: GoogleFonts.instrumentSans(color: VoyoColors.ink),
                decoration: const InputDecoration(
                  hintText: 'Your name',
                  prefixIcon: Icon(Icons.person_outline, color: VoyoColors.stone),
                ),
              ),

              const SizedBox(height: 28),

              // Q1 — Interests
              _header('What draws you most? (pick all that apply)'),
              const SizedBox(height: 10),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: _interestOptions.map((opt) {
                  final selected = _selectedInterests.contains(opt.$2);
                  return GestureDetector(
                    onTap: () => setState(() {
                      if (selected) {
                        _selectedInterests.remove(opt.$2);
                      } else {
                        _selectedInterests.add(opt.$2);
                      }
                    }),
                    child: AnimatedContainer(
                      duration: const Duration(milliseconds: 150),
                      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                      decoration: BoxDecoration(
                        color: selected ? const Color(0x1AD45028) : VoyoColors.paper,
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(
                          color: selected ? VoyoColors.expedition : VoyoColors.smoke,
                          width: selected ? 1.5 : 1,
                        ),
                      ),
                      child: Text(
                        opt.$1,
                        style: GoogleFonts.instrumentSans(
                          fontSize: 13,
                          fontWeight: selected ? FontWeight.w600 : FontWeight.w400,
                          color: selected ? VoyoColors.expedition : VoyoColors.stone,
                        ),
                      ),
                    ),
                  );
                }).toList(),
              ),

              const SizedBox(height: 28),

              // Q2 — Pace
              _header('Travel pace?'),
              const SizedBox(height: 10),
              _optionRow(
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
              _header('Budget level?'),
              const SizedBox(height: 10),
              _optionRow(
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
              _header('Who do you travel with?'),
              const SizedBox(height: 10),
              _optionRow(
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
              _header('Any mobility needs?'),
              const SizedBox(height: 10),
              _optionRow(
                options: const [
                  ('None', 'Full mobility'),
                  ('Limited', 'Limited walking'),
                  ('Wheelchair', 'Wheelchair accessible only'),
                ],
                selected: _mobility,
                onSelect: (v) => setState(() => _mobility = v),
              ),

              const SizedBox(height: 28),

              // Q6 — Planning style
              _header('How do you like to plan?'),
              const SizedBox(height: 10),
              _optionRow(
                options: const [
                  ('Pre-planned', 'everything_pre_planned'),
                  ('Mix', 'mix_of_planned_spontaneous'),
                  ('Spontaneous', 'mostly_spontaneous'),
                ],
                selected: _planningStyle,
                onSelect: (v) => setState(() => _planningStyle = v),
              ),

              const SizedBox(height: 36),

              SizedBox(
                width: double.infinity,
                height: 52,
                child: FilledButton(
                  onPressed: _saving ? null : _save,
                  style: FilledButton.styleFrom(
                    backgroundColor: VoyoColors.expedition,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(14),
                    ),
                  ),
                  child: _saving
                      ? const SizedBox(
                          width: 22,
                          height: 22,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            color: Colors.white,
                          ),
                        )
                      : Text(
                          'Done — let\'s explore Egypt!',
                          style: GoogleFonts.instrumentSans(
                            fontSize: 15,
                            fontWeight: FontWeight.w600,
                            color: Colors.white,
                          ),
                        ),
                ),
              ),
              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }

  Widget _header(String label) {
    return Text(
      label,
      style: GoogleFonts.instrumentSans(
        fontWeight: FontWeight.w600,
        fontSize: 15,
        color: VoyoColors.ink,
      ),
    );
  }

  Widget _optionRow({
    required List<(String, String)> options,
    required String selected,
    required ValueChanged<String> onSelect,
  }) {
    return Row(
      children: options.map((opt) {
        final isSelected = selected == opt.$2;
        return Expanded(
          child: Padding(
            padding: const EdgeInsets.only(right: 6),
            child: GestureDetector(
              onTap: () => onSelect(opt.$2),
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 150),
                padding: const EdgeInsets.symmetric(vertical: 10),
                decoration: BoxDecoration(
                  color: isSelected ? const Color(0x1AD45028) : VoyoColors.paper,
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(
                    color: isSelected ? VoyoColors.expedition : VoyoColors.smoke,
                    width: isSelected ? 1.5 : 1,
                  ),
                ),
                child: Text(
                  opt.$1,
                  textAlign: TextAlign.center,
                  style: GoogleFonts.instrumentSans(
                    fontSize: 13,
                    fontWeight: isSelected ? FontWeight.w600 : FontWeight.w400,
                    color: isSelected ? VoyoColors.expedition : VoyoColors.stone,
                  ),
                ),
              ),
            ),
          ),
        );
      }).toList(),
    );
  }
}
