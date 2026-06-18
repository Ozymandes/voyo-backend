import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../theme.dart';

/// Structured trip profile collected from the user before CLEO generates a
/// grounded itinerary. Mirrors the dimensions the backend recommendation
/// engine + Safarny-style planner consume: budget → `price_sensitivity`,
/// style → `interest_scores`/`travel_style`, pace → `itinerary_pace`,
/// companions → `typical_companions`. Kept backend-agnostic so it can POST
/// to /itinerary/plan, feed CLEO context, or seed a user_profiles row.
class TripProfile {
  final String? title;
  final DateTime? startDate;
  final DateTime? endDate;
  final int travelers;
  final String budgetTier; // 'budget' | 'moderate' | 'luxury'
  final String pace; // 'packed_schedule' | 'balanced' | 'slow_flexible'
  final String companions; // 'solo' | 'couple' | 'family' | 'friends'
  final Set<String> interests; // {'historical','natural',...}
  final String? notes;

  const TripProfile({
    this.title,
    this.startDate,
    this.endDate,
    this.travelers = 2,
    this.budgetTier = 'moderate',
    this.pace = 'balanced',
    this.companions = 'couple',
    this.interests = const {'historical', 'cultural'},
    this.notes,
  });

  int get dayCount {
    if (startDate == null || endDate == null) return 0;
    return endDate!.difference(startDate!).inDays + 1;
  }

  Map<String, dynamic> toJson() => {
    if (title != null && title!.trim().isNotEmpty) 'title': title!.trim(),
    if (startDate != null)
      'start_date':
          '${startDate!.year}-${startDate!.month.toString().padLeft(2, '0')}-${startDate!.day.toString().padLeft(2, '0')}',
    if (endDate != null)
      'end_date':
          '${endDate!.year}-${endDate!.month.toString().padLeft(2, '0')}-${endDate!.day.toString().padLeft(2, '0')}',
    'travelers': travelers,
    'budget_tier': budgetTier,
    'pace': pace,
    'companions': companions,
    'interests': interests.toList(),
    if (notes != null && notes!.trim().isNotEmpty) 'notes': notes!.trim(),
  };

  /// Maps to the user_profiles columns the recommendation engine reads, so a
  /// one-shot profile (no onboarding) still personalizes POI scoring.
  Map<String, dynamic> toProfilePrefs() => {
    'price_sensitivity': budgetTier,
    'itinerary_pace': pace,
    'interest_scores': {for (final i in interests) i: 9},
    'typical_companions': {'type': companions},
  };

  TripProfile copyWith({
    String? title,
    DateTime? startDate,
    DateTime? endDate,
    int? travelers,
    String? budgetTier,
    String? pace,
    String? companions,
    Set<String>? interests,
    String? notes,
  }) => TripProfile(
    title: title ?? this.title,
    startDate: startDate ?? this.startDate,
    endDate: endDate ?? this.endDate,
    travelers: travelers ?? this.travelers,
    budgetTier: budgetTier ?? this.budgetTier,
    pace: pace ?? this.pace,
    companions: companions ?? this.companions,
    interests: interests ?? this.interests,
    notes: notes ?? this.notes,
  );
}

/// Shows the trip-profile sheet. Returns the completed [TripProfile] when the
/// user taps "Generate itinerary", or null if cancelled. Used as the entry
/// point when CLEO detects an itinerary intent OR when the user taps a
/// "Plan a trip" action — collecting the structured inputs the grounded
/// planner needs before any LLM / VROOM work happens.
Future<TripProfile?> showTripProfileSheet(
  BuildContext context, {
  TripProfile? initial,
}) {
  return showModalBottomSheet<TripProfile>(
    context: context,
    isScrollControlled: true,
    backgroundColor: Colors.transparent,
    builder: (_) => _TripProfileSheet(initial: initial),
  );
}

class _TripProfileSheet extends StatefulWidget {
  final TripProfile? initial;
  const _TripProfileSheet({this.initial});

  @override
  State<_TripProfileSheet> createState() => _TripProfileSheetState();
}

class _TripProfileSheetState extends State<_TripProfileSheet> {
  late TripProfile _p;
  final _notesCtrl = TextEditingController();
  final _titleCtrl = TextEditingController();

  @override
  void initState() {
    super.initState();
    _p = widget.initial ?? const TripProfile();
    _notesCtrl.text = _p.notes ?? '';
    _titleCtrl.text = _p.title ?? '';
  }

  @override
  void dispose() {
    _notesCtrl.dispose();
    _titleCtrl.dispose();
    super.dispose();
  }

  Future<void> _pickDate(bool isStart) async {
    final initial =
        isStart
            ? (_p.startDate ?? DateTime.now().add(const Duration(days: 7)))
            : (_p.endDate ??
                (_p.startDate ?? DateTime.now()).add(const Duration(days: 5)));
    final first = isStart ? DateTime.now() : (_p.startDate ?? DateTime.now());
    final picked = await showDatePicker(
      context: context,
      initialDate: initial,
      firstDate: first,
      lastDate: DateTime.now().add(const Duration(days: 365 * 2)),
      builder:
          (ctx, child) => Theme(
            data: Theme.of(ctx).copyWith(
              colorScheme: const ColorScheme.light(
                primary: VoyoColors.expedition,
                onSurface: VoyoColors.ink,
              ),
            ),
            child: child!,
          ),
    );
    if (picked == null) return;
    setState(() {
      if (isStart) {
        _p = _p.copyWith(
          startDate: picked,
          endDate:
              (_p.endDate != null && _p.endDate!.isBefore(picked))
                  ? null
                  : _p.endDate,
        );
      } else {
        _p = _p.copyWith(endDate: picked);
      }
    });
  }

  void _submit() {
    // Dates are the only hard requirement — without a date range we can't
    // compute days or run VROOM. Everything else has sensible defaults.
    if (_p.startDate == null || _p.endDate == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please pick your travel dates to continue.'),
          behavior: SnackBarBehavior.floating,
        ),
      );
      return;
    }
    final profile = _p.copyWith(
      title: _titleCtrl.text.trim().isEmpty ? null : _titleCtrl.text.trim(),
      notes: _notesCtrl.text.trim().isEmpty ? null : _notesCtrl.text.trim(),
    );
    Navigator.pop(context, profile);
  }

  @override
  Widget build(BuildContext context) {
    final bottomInset = MediaQuery.of(context).viewInsets.bottom;
    return Container(
      height: MediaQuery.of(context).size.height * 0.92,
      padding: EdgeInsets.only(bottom: bottomInset),
      decoration: const BoxDecoration(
        color: VoyoColors.page,
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      child: Column(
        children: [
          // Handle + header
          Container(
            width: 40,
            height: 4,
            margin: const EdgeInsets.only(top: 10),
            decoration: BoxDecoration(
              color: VoyoColors.smoke,
              borderRadius: BorderRadius.circular(2),
            ),
          ),
          Padding(
            padding: const EdgeInsets.fromLTRB(20, 16, 20, 8),
            child: Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Plan your Egypt trip',
                        style: GoogleFonts.fraunces(
                          fontSize: 24,
                          fontStyle: FontStyle.italic,
                          color: VoyoColors.ink,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        'A few details and CLEO will craft a grounded, '
                        'route-optimized itinerary.',
                        style: GoogleFonts.instrumentSans(
                          fontSize: 12.5,
                          color: VoyoColors.stone,
                          height: 1.4,
                        ),
                      ),
                    ],
                  ),
                ),
                IconButton(
                  onPressed: () => Navigator.pop(context),
                  icon: const Icon(
                    Icons.close_rounded,
                    color: VoyoColors.stone,
                  ),
                ),
              ],
            ),
          ),
          const Divider(height: 1, color: VoyoColors.smoke),
          // Scrollable form
          Expanded(
            child: ListView(
              padding: const EdgeInsets.fromLTRB(20, 18, 20, 24),
              children: [
                _sectionLabel('Trip name (optional)'),
                _TextField(
                  controller: _titleCtrl,
                  hint: 'e.g. Cairo & Luxor Adventure',
                ),
                const SizedBox(height: 22),

                _sectionLabel('Travel dates'),
                Row(
                  children: [
                    Expanded(
                      child: _DateTile(
                        label: 'Start',
                        date: _p.startDate,
                        onTap: () => _pickDate(true),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: _DateTile(
                        label: 'End',
                        date: _p.endDate,
                        onTap: () => _pickDate(false),
                      ),
                    ),
                  ],
                ),
                if (_p.dayCount > 0)
                  Padding(
                    padding: const EdgeInsets.only(top: 8),
                    child: Text(
                      '${_p.dayCount} day${_p.dayCount == 1 ? '' : 's'} of travel',
                      style: GoogleFonts.instrumentSans(
                        fontSize: 11.5,
                        color: VoyoColors.expedition,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                const SizedBox(height: 22),

                _sectionLabel('Travellers'),
                _Stepper(
                  value: _p.travelers,
                  onChanged:
                      (v) => setState(() => _p = _p.copyWith(travelers: v)),
                ),
                const SizedBox(height: 22),

                _sectionLabel('Budget'),
                _ChipPicker(
                  options: const [
                    ('budget', 'Budget', Icons.savings_outlined),
                    (
                      'moderate',
                      'Moderate',
                      Icons.account_balance_wallet_outlined,
                    ),
                    ('luxury', 'Luxury', Icons.diamond_outlined),
                  ],
                  value: _p.budgetTier,
                  onChanged:
                      (v) => setState(() => _p = _p.copyWith(budgetTier: v)),
                ),
                const SizedBox(height: 22),

                _sectionLabel('Travel style'),
                _ChipPicker(
                  multi: true,
                  options: const [
                    ('historical', 'History', Icons.museum_outlined),
                    ('cultural', 'Culture', Icons.theater_comedy_outlined),
                    ('natural', 'Nature', Icons.terrain_outlined),
                    ('entertainment', 'Fun', Icons.celebration_outlined),
                    ('religious', 'Spiritual', Icons.church_outlined),
                  ],
                  values: _p.interests,
                  onChangedSet:
                      (set) => setState(() => _p = _p.copyWith(interests: set)),
                ),
                const SizedBox(height: 22),

                _sectionLabel('Pace'),
                _ChipPicker(
                  options: const [
                    ('packed_schedule', 'Packed', Icons.flash_on_outlined),
                    ('balanced', 'Balanced', Icons.balance_outlined),
                    ('slow_flexible', 'Relaxed', Icons.spa_outlined),
                  ],
                  value: _p.pace,
                  onChanged: (v) => setState(() => _p = _p.copyWith(pace: v)),
                ),
                const SizedBox(height: 22),

                _sectionLabel('Who\'s coming?'),
                _ChipPicker(
                  options: const [
                    ('solo', 'Solo', Icons.person_outline),
                    ('couple', 'Couple', Icons.favorite_outline),
                    ('family', 'Family', Icons.family_restroom_outlined),
                    ('friends', 'Friends', Icons.groups_outlined),
                  ],
                  value: _p.companions,
                  onChanged:
                      (v) => setState(() => _p = _p.copyWith(companions: v)),
                ),
                const SizedBox(height: 22),

                _sectionLabel('Anything else? (optional)'),
                _TextField(
                  controller: _notesCtrl,
                  hint: 'Dietary needs, mobility, must-sees, things to avoid…',
                  maxLines: 3,
                ),
                const SizedBox(height: 28),

                // Generate button
                SizedBox(
                  width: double.infinity,
                  height: 52,
                  child: FilledButton.icon(
                    onPressed: _submit,
                    style: FilledButton.styleFrom(
                      backgroundColor: VoyoColors.expedition,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(14),
                      ),
                    ),
                    icon: const Icon(
                      Icons.auto_awesome_rounded,
                      size: 20,
                      color: Colors.white,
                    ),
                    label: Text(
                      'Generate itinerary',
                      style: GoogleFonts.instrumentSans(
                        fontSize: 15,
                        fontWeight: FontWeight.w700,
                        color: Colors.white,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _sectionLabel(String text) => Padding(
    padding: const EdgeInsets.only(bottom: 10),
    child: Text(
      text,
      style: GoogleFonts.instrumentSans(
        fontSize: 13,
        fontWeight: FontWeight.w700,
        color: VoyoColors.ink,
        letterSpacing: 0.2,
      ),
    ),
  );
}

// ── Sub-widgets ──────────────────────────────────────────────────────

class _DateTile extends StatelessWidget {
  final String label;
  final DateTime? date;
  final VoidCallback onTap;
  const _DateTile({
    required this.label,
    required this.date,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
          decoration: BoxDecoration(
            color: VoyoColors.paper,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: VoyoColors.smoke),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: GoogleFonts.instrumentSans(
                  fontSize: 10.5,
                  color: VoyoColors.stone,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 3),
              Text(
                date == null
                    ? 'Select'
                    : '${date!.day} ${_monthName(date!.month)} ${date!.year}',
                style: GoogleFonts.instrumentSans(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  color: date == null ? VoyoColors.stone : VoyoColors.ink,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  static String _monthName(int m) =>
      const [
        '',
        'Jan',
        'Feb',
        'Mar',
        'Apr',
        'May',
        'Jun',
        'Jul',
        'Aug',
        'Sep',
        'Oct',
        'Nov',
        'Dec',
      ][m];
}

class _Stepper extends StatelessWidget {
  final int value;
  final ValueChanged<int> onChanged;
  const _Stepper({required this.value, required this.onChanged});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 4),
      decoration: BoxDecoration(
        color: VoyoColors.paper,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: VoyoColors.smoke),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          _stepBtn(Icons.remove_rounded, value > 1, () => onChanged(value - 1)),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Text(
              '$value ${value == 1 ? 'traveller' : 'travellers'}',
              style: GoogleFonts.instrumentSans(
                fontSize: 14,
                fontWeight: FontWeight.w600,
                color: VoyoColors.ink,
              ),
            ),
          ),
          _stepBtn(Icons.add_rounded, value < 12, () => onChanged(value + 1)),
        ],
      ),
    );
  }

  Widget _stepBtn(IconData icon, bool enabled, VoidCallback onTap) =>
      IconButton(
        onPressed: enabled ? onTap : null,
        icon: Icon(icon, size: 20),
        color: VoyoColors.expedition,
        disabledColor: VoyoColors.smoke,
        visualDensity: VisualDensity.compact,
      );
}

class _ChipPicker extends StatelessWidget {
  final List<(String, String, IconData)> options;
  final String? value;
  final Set<String>? values; // for multi
  final bool multi;
  final ValueChanged<String>? onChanged;
  final ValueChanged<Set<String>>? onChangedSet;
  const _ChipPicker({
    required this.options,
    this.value,
    this.values,
    this.multi = false,
    this.onChanged,
    this.onChangedSet,
  }) : assert(multi ? onChangedSet != null : onChanged != null);

  @override
  Widget build(BuildContext context) {
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: [
        for (final (id, label, icon) in options)
          _OptionChip(
            icon: icon,
            label: label,
            selected: multi ? (values?.contains(id) ?? false) : value == id,
            onTap: () {
              if (multi) {
                final next = Set<String>.from(values ?? const {});
                if (!next.add(id)) next.remove(id);
                // Keep at least one interest selected in multi mode.
                if (next.isEmpty && options.isNotEmpty) {
                  next.add(options.first.$1);
                }
                onChangedSet!(next);
              } else {
                onChanged!(id);
              }
            },
          ),
      ],
    );
  }
}

class _OptionChip extends StatelessWidget {
  final IconData icon;
  final String label;
  final bool selected;
  final VoidCallback onTap;
  const _OptionChip({
    required this.icon,
    required this.label,
    required this.selected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final accent = VoyoColors.expedition;
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(20),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 150),
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 9),
          decoration: BoxDecoration(
            color: selected ? accent.withValues(alpha: 0.12) : VoyoColors.paper,
            borderRadius: BorderRadius.circular(20),
            border: Border.all(
              color: selected ? accent : VoyoColors.smoke,
              width: selected ? 1.5 : 1,
            ),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(icon, size: 15, color: selected ? accent : VoyoColors.stone),
              const SizedBox(width: 7),
              Text(
                label,
                style: GoogleFonts.instrumentSans(
                  fontSize: 12.5,
                  fontWeight: selected ? FontWeight.w700 : FontWeight.w500,
                  color: selected ? accent : VoyoColors.ink,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _TextField extends StatelessWidget {
  final TextEditingController controller;
  final String hint;
  final int maxLines;
  const _TextField({
    required this.controller,
    required this.hint,
    this.maxLines = 1,
  });

  @override
  Widget build(BuildContext context) {
    return TextField(
      controller: controller,
      maxLines: maxLines,
      style: GoogleFonts.instrumentSans(fontSize: 14, color: VoyoColors.ink),
      decoration: InputDecoration(
        hintText: hint,
        hintStyle: GoogleFonts.instrumentSans(
          fontSize: 14,
          color: VoyoColors.stone,
        ),
        filled: true,
        fillColor: VoyoColors.paper,
        contentPadding: const EdgeInsets.symmetric(
          horizontal: 14,
          vertical: 13,
        ),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: VoyoColors.smoke),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: VoyoColors.smoke),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: VoyoColors.expedition, width: 1.5),
        ),
      ),
    );
  }
}
