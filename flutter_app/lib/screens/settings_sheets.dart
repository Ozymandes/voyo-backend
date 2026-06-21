import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../theme.dart';

// ---------------------------------------------------------------------------
// Shared helpers
// ---------------------------------------------------------------------------

final _supabase = Supabase.instance.client;

Future<Map<String, dynamic>?> _fetchProfile() async {
  final uid = _supabase.auth.currentUser?.id;
  if (uid == null) return null;
  return await _supabase
      .from('user_profiles')
      .select()
      .eq('user_id', uid)
      .maybeSingle() as Map<String, dynamic>?;
}

Future<void> _saveProfile(Map<String, dynamic> data) async {
  final uid = _supabase.auth.currentUser?.id;
  if (uid == null) return;
  await _supabase
      .from('user_profiles')
      .update(data)
      .eq('user_id', uid);
}

Widget _sheetHandle() => Padding(
      padding: const EdgeInsets.only(top: 12, bottom: 4),
      child: Center(
        child: Container(
          width: 36,
          height: 4,
          decoration: BoxDecoration(
              color: VoyoColors.smoke,
              borderRadius: BorderRadius.circular(2)),
        ),
      ),
    );

Widget _sheetHeader(String title, BuildContext context) => Padding(
      padding: const EdgeInsets.fromLTRB(20, 8, 16, 12),
      child: Row(
        children: [
          Text(title,
              style: GoogleFonts.fraunces(
                  fontSize: 22,
                  fontStyle: FontStyle.italic,
                  color: VoyoColors.ink)),
          const Spacer(),
          GestureDetector(
            onTap: () => Navigator.pop(context),
            child:
                const Icon(Icons.close, size: 20, color: VoyoColors.stone),
          ),
        ],
      ),
    );

Widget _saveButton(
        {required bool saving,
        required VoidCallback onTap}) =>
    SizedBox(
      width: double.infinity,
      height: 52,
      child: FilledButton(
        onPressed: saving ? null : onTap,
        style: FilledButton.styleFrom(
          backgroundColor: VoyoColors.expedition,
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
        ),
        child: saving
            ? const SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(
                    strokeWidth: 2, color: Colors.white))
            : Text('Save Changes',
                style: GoogleFonts.instrumentSans(
                    fontSize: 15,
                    fontWeight: FontWeight.w600,
                    color: Colors.white)),
      ),
    );

// ---------------------------------------------------------------------------
// Personal Info Sheet
// ---------------------------------------------------------------------------

class PersonalInfoSheet extends StatefulWidget {
  final VoidCallback? onSaved;
  const PersonalInfoSheet({super.key, this.onSaved});

  @override
  State<PersonalInfoSheet> createState() => _PersonalInfoSheetState();
}

class _PersonalInfoSheetState extends State<PersonalInfoSheet> {
  final _nameCtrl = TextEditingController();
  bool _loading = true;
  bool _saving = false;
  String? _error;
  String? _email;

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void dispose() {
    _nameCtrl.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    final profile = await _fetchProfile();
    if (mounted) {
      _nameCtrl.text = profile?['full_name'] as String? ?? '';
      _email = _supabase.auth.currentUser?.email;
      setState(() => _loading = false);
    }
  }

  Future<void> _save() async {
    final name = _nameCtrl.text.trim();
    if (name.isEmpty) {
      setState(() => _error = 'Name cannot be empty.');
      return;
    }
    setState(() { _saving = true; _error = null; });
    try {
      await _saveProfile({'full_name': name});
      if (mounted) {
        widget.onSaved?.call();
        Navigator.pop(context);
      }
    } catch (e) {
      if (mounted) setState(() { _error = e.toString(); _saving = false; });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding:
          EdgeInsets.only(bottom: MediaQuery.of(context).viewInsets.bottom),
      child: Container(
        decoration: const BoxDecoration(
          color: VoyoColors.paper,
          borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _sheetHandle(),
            _sheetHeader('Personal Info', context),
            const Divider(color: VoyoColors.smoke, height: 1),
            if (_loading)
              const Padding(
                padding: EdgeInsets.all(40),
                child: Center(
                    child: CircularProgressIndicator(
                        color: VoyoColors.terra, strokeWidth: 2)),
              )
            else
              Padding(
                padding: const EdgeInsets.fromLTRB(20, 20, 20, 32),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _label('Full name'),
                    const SizedBox(height: 8),
                    TextField(
                      controller: _nameCtrl,
                      autofocus: true,
                      textInputAction: TextInputAction.done,
                      style: GoogleFonts.instrumentSans(color: VoyoColors.ink),
                      decoration: _inputDeco('e.g. Ahmed Hassan'),
                    ),
                    const SizedBox(height: 16),
                    _label('Email'),
                    const SizedBox(height: 8),
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.symmetric(
                          horizontal: 16, vertical: 14),
                      decoration: BoxDecoration(
                        color: VoyoColors.vellum,
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: VoyoColors.smoke),
                      ),
                      child: Text(
                        _email ?? '—',
                        style: GoogleFonts.instrumentSans(
                            fontSize: 14, color: VoyoColors.stone),
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text('Email is managed through your account.',
                        style: GoogleFonts.instrumentSans(
                            fontSize: 11, color: VoyoColors.stone)),
                    if (_error != null) ...[
                      const SizedBox(height: 10),
                      Text(_error!,
                          style: GoogleFonts.instrumentSans(
                              fontSize: 12,
                              color: VoyoColors.expedition)),
                    ],
                    const SizedBox(height: 24),
                    _saveButton(saving: _saving, onTap: _save),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Travel Preferences Sheet
// ---------------------------------------------------------------------------

class TravelPreferencesSheet extends StatefulWidget {
  const TravelPreferencesSheet({super.key});

  @override
  State<TravelPreferencesSheet> createState() =>
      _TravelPreferencesSheetState();
}

class _TravelPreferencesSheetState extends State<TravelPreferencesSheet> {
  bool _loading = true;
  bool _saving = false;
  String? _error;

  // Pace
  String _pace = 'balanced';
  // Budget
  String _budget = 'moderate';
  // Companions
  String _companions = 'solo';
  // Planning style
  String _planning = 'mix_of_planned_spontaneous';
  // Interests
  final _interests = <String>{};

  static const _interestOptions = [
    ('Historical & Ancient', 'historical_sites'),
    ('Outdoor & Nature', 'outdoor_nature'),
    ('Food & Culture', 'food_culture'),
    ('Adventure & Sports', 'adventure'),
    ('Religious & Spiritual', 'religious_spiritual'),
    ('Modern & Nightlife', 'modern_entertainment'),
  ];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final profile = await _fetchProfile();
    if (profile != null && mounted) {
      final style = profile['travel_style'] as Map<String, dynamic>?;
      _pace = profile['itinerary_pace'] as String? ?? 'balanced';
      _budget = profile['price_sensitivity'] as String? ?? 'moderate';
      _companions = style?['companions'] as String? ?? 'solo';
      _planning = profile['planning_style'] as String? ??
          'mix_of_planned_spontaneous';

      final scores =
          profile['interest_scores'] as Map<String, dynamic>? ?? {};
      for (final opt in _interestOptions) {
        if ((scores[opt.$2] as num? ?? 0) > 0.5) _interests.add(opt.$2);
      }
    }
    if (mounted) setState(() => _loading = false);
  }

  Future<void> _save() async {
    setState(() { _saving = true; _error = null; });
    try {
      final scores = {
        for (final opt in _interestOptions)
          opt.$2: _interests.contains(opt.$2) ? 0.9 : 0.1,
      };
      await _saveProfile({
        'itinerary_pace': _pace,
        'price_sensitivity': _budget,
        'planning_style': _planning,
        'interest_scores': scores,
        'travel_style': {
          'pace': _pace,
          'budget': _budget,
          'companions': _companions,
          'planning': _planning,
        },
        'typical_companions': _companions == 'family'
            ? {'type': 'family', 'has_children': true}
            : {'type': _companions},
      });
      if (mounted) Navigator.pop(context);
    } catch (e) {
      if (mounted) setState(() { _error = e.toString(); _saving = false; });
    }
  }

  @override
  Widget build(BuildContext context) {
    final screenH = MediaQuery.of(context).size.height;
    return Container(
      height: screenH * 0.88,
      decoration: const BoxDecoration(
        color: VoyoColors.page,
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      child: Column(
        children: [
          _sheetHandle(),
          _sheetHeader('Travel Preferences', context),
          const Divider(color: VoyoColors.smoke, height: 1),
          Expanded(
            child: _loading
                ? const Center(
                    child: CircularProgressIndicator(
                        color: VoyoColors.terra, strokeWidth: 2))
                : SingleChildScrollView(
                    padding: const EdgeInsets.fromLTRB(20, 20, 20, 32),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Pace
                        _label('Trip pace'),
                        const SizedBox(height: 10),
                        _choiceRow([
                          ('Relaxed', 'relaxed'),
                          ('Balanced', 'balanced'),
                          ('Packed', 'packed'),
                        ], _pace, (v) => setState(() => _pace = v)),
                        const SizedBox(height: 20),

                        // Budget
                        _label('Budget sensitivity'),
                        const SizedBox(height: 10),
                        _choiceRow([
                          ('Budget', 'budget'),
                          ('Moderate', 'moderate'),
                          ('Luxury', 'luxury'),
                        ], _budget, (v) => setState(() => _budget = v)),
                        const SizedBox(height: 20),

                        // Companions
                        _label('Who do you travel with?'),
                        const SizedBox(height: 10),
                        _choiceRow([
                          ('Solo', 'solo'),
                          ('Couple', 'couple'),
                          ('Family', 'family'),
                          ('Group', 'group'),
                        ], _companions,
                            (v) => setState(() => _companions = v)),
                        const SizedBox(height: 20),

                        // Planning style
                        _label('Planning style'),
                        const SizedBox(height: 10),
                        _choiceColumn([
                          ('Fully planned', 'fully_planned'),
                          ('Mix of planned & spontaneous',
                              'mix_of_planned_spontaneous'),
                          ('Mostly spontaneous', 'mostly_spontaneous'),
                        ], _planning,
                            (v) => setState(() => _planning = v)),
                        const SizedBox(height: 20),

                        // Interests
                        _label('Interests'),
                        const SizedBox(height: 4),
                        Text('Select all that apply',
                            style: GoogleFonts.instrumentSans(
                                fontSize: 11, color: VoyoColors.stone)),
                        const SizedBox(height: 10),
                        Wrap(
                          spacing: 8,
                          runSpacing: 8,
                          children: _interestOptions.map((opt) {
                            final on = _interests.contains(opt.$2);
                            return GestureDetector(
                              onTap: () => setState(() => on
                                  ? _interests.remove(opt.$2)
                                  : _interests.add(opt.$2)),
                              child: AnimatedContainer(
                                duration:
                                    const Duration(milliseconds: 150),
                                padding: const EdgeInsets.symmetric(
                                    horizontal: 14, vertical: 8),
                                decoration: BoxDecoration(
                                  color: on
                                      ? VoyoColors.expedition
                                      : VoyoColors.paper,
                                  borderRadius: BorderRadius.circular(20),
                                  border: Border.all(
                                      color: on
                                          ? VoyoColors.expedition
                                          : VoyoColors.smoke),
                                ),
                                child: Text(opt.$1,
                                    style: GoogleFonts.instrumentSans(
                                        fontSize: 13,
                                        fontWeight: FontWeight.w500,
                                        color: on
                                            ? Colors.white
                                            : VoyoColors.stone)),
                              ),
                            );
                          }).toList(),
                        ),

                        if (_error != null) ...[
                          const SizedBox(height: 12),
                          Text(_error!,
                              style: GoogleFonts.instrumentSans(
                                  fontSize: 12,
                                  color: VoyoColors.expedition)),
                        ],
                        const SizedBox(height: 24),
                        _saveButton(saving: _saving, onTap: _save),
                      ],
                    ),
                  ),
          ),
        ],
      ),
    );
  }

  Widget _choiceRow(List<(String, String)> options, String selected,
      ValueChanged<String> onSelect) {
    return Row(
      children: options
          .map((o) => Expanded(
                child: Padding(
                  padding: const EdgeInsets.only(right: 6),
                  child: _chip(o.$1, o.$2, selected, onSelect),
                ),
              ))
          .toList(),
    );
  }

  Widget _choiceColumn(List<(String, String)> options, String selected,
      ValueChanged<String> onSelect) {
    return Column(
      children: options
          .map((o) => Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: GestureDetector(
                  onTap: () => onSelect(o.$2),
                  child: AnimatedContainer(
                    duration: const Duration(milliseconds: 150),
                    width: double.infinity,
                    padding: const EdgeInsets.symmetric(
                        horizontal: 16, vertical: 12),
                    decoration: BoxDecoration(
                      color: selected == o.$2
                          ? const Color(0x1AD45028)
                          : VoyoColors.paper,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(
                          color: selected == o.$2
                              ? VoyoColors.expedition
                              : VoyoColors.smoke),
                    ),
                    child: Row(
                      children: [
                        Expanded(
                          child: Text(o.$1,
                              style: GoogleFonts.instrumentSans(
                                  fontSize: 13,
                                  fontWeight: FontWeight.w500,
                                  color: selected == o.$2
                                      ? VoyoColors.expedition
                                      : VoyoColors.ink)),
                        ),
                        if (selected == o.$2)
                          const Icon(Icons.check,
                              size: 16,
                              color: VoyoColors.expedition),
                      ],
                    ),
                  ),
                ),
              ))
          .toList(),
    );
  }

  Widget _chip(String label, String value, String selected,
      ValueChanged<String> onSelect) {
    final on = selected == value;
    return GestureDetector(
      onTap: () => onSelect(value),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 150),
        padding:
            const EdgeInsets.symmetric(horizontal: 10, vertical: 10),
        decoration: BoxDecoration(
          color: on ? VoyoColors.expedition : VoyoColors.paper,
          borderRadius: BorderRadius.circular(10),
          border: Border.all(
              color: on ? VoyoColors.expedition : VoyoColors.smoke),
        ),
        child: Center(
          child: Text(label,
              style: GoogleFonts.instrumentSans(
                  fontSize: 12,
                  fontWeight: FontWeight.w500,
                  color: on ? Colors.white : VoyoColors.stone)),
        ),
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Mobility & Accessibility Sheet
// ---------------------------------------------------------------------------

class MobilitySheet extends StatefulWidget {
  const MobilitySheet({super.key});

  @override
  State<MobilitySheet> createState() => _MobilitySheetState();
}

class _MobilitySheetState extends State<MobilitySheet> {
  bool _loading = true;
  bool _saving = false;
  String? _error;
  String _mobility = 'Full mobility';

  static const _options = [
    (
      Icons.directions_walk_outlined,
      'Full mobility',
      'No restrictions — all terrain and stairs are fine'
    ),
    (
      Icons.accessibility_outlined,
      'Some limitations',
      'Prefer to avoid long walks or excessive stairs'
    ),
    (
      Icons.wheelchair_pickup_outlined,
      'Wheelchair user',
      'Need fully accessible routes and venues'
    ),
    (
      Icons.elderly_outlined,
      'Elderly / reduced mobility',
      'Prefer flat, easy-access routes'
    ),
  ];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final profile = await _fetchProfile();
    if (profile != null && mounted) {
      _mobility =
          profile['mobility_preference'] as String? ?? 'Full mobility';
    }
    if (mounted) setState(() => _loading = false);
  }

  Future<void> _save() async {
    setState(() { _saving = true; _error = null; });
    try {
      await _saveProfile({'mobility_preference': _mobility});
      if (mounted) Navigator.pop(context);
    } catch (e) {
      if (mounted) setState(() { _error = e.toString(); _saving = false; });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: const BoxDecoration(
        color: VoyoColors.paper,
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          _sheetHandle(),
          _sheetHeader('Mobility & Accessibility', context),
          const Divider(color: VoyoColors.smoke, height: 1),
          if (_loading)
            const Padding(
              padding: EdgeInsets.all(40),
              child: Center(
                  child: CircularProgressIndicator(
                      color: VoyoColors.terra, strokeWidth: 2)),
            )
          else
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 16, 20, 32),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'CLEO uses this to suggest accessible routes and venues.',
                    style: GoogleFonts.instrumentSans(
                        fontSize: 13,
                        color: VoyoColors.stone,
                        height: 1.4),
                  ),
                  const SizedBox(height: 16),
                  ..._options.map((opt) {
                    final selected = _mobility == opt.$2;
                    return GestureDetector(
                      onTap: () =>
                          setState(() => _mobility = opt.$2),
                      child: AnimatedContainer(
                        duration: const Duration(milliseconds: 150),
                        margin: const EdgeInsets.only(bottom: 10),
                        padding: const EdgeInsets.all(14),
                        decoration: BoxDecoration(
                          color: selected
                              ? const Color(0x1AD45028)
                              : VoyoColors.vellum,
                          borderRadius: BorderRadius.circular(14),
                          border: Border.all(
                              color: selected
                                  ? VoyoColors.expedition
                                  : VoyoColors.smoke,
                              width: selected ? 1.5 : 1),
                        ),
                        child: Row(
                          children: [
                            Icon(opt.$1,
                                size: 22,
                                color: selected
                                    ? VoyoColors.expedition
                                    : VoyoColors.stone),
                            const SizedBox(width: 14),
                            Expanded(
                              child: Column(
                                crossAxisAlignment:
                                    CrossAxisAlignment.start,
                                children: [
                                  Text(opt.$2,
                                      style: GoogleFonts.instrumentSans(
                                          fontSize: 14,
                                          fontWeight: FontWeight.w600,
                                          color: selected
                                              ? VoyoColors.expedition
                                              : VoyoColors.ink)),
                                  Text(opt.$3,
                                      style: GoogleFonts.instrumentSans(
                                          fontSize: 11,
                                          color: VoyoColors.stone,
                                          height: 1.3)),
                                ],
                              ),
                            ),
                            if (selected)
                              const Icon(Icons.check_circle,
                                  size: 18,
                                  color: VoyoColors.expedition),
                          ],
                        ),
                      ),
                    );
                  }),
                  if (_error != null) ...[
                    const SizedBox(height: 10),
                    Text(_error!,
                        style: GoogleFonts.instrumentSans(
                            fontSize: 12,
                            color: VoyoColors.expedition)),
                  ],
                  const SizedBox(height: 8),
                  _saveButton(saving: _saving, onTap: _save),
                ],
              ),
            ),
        ],
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Shared input helpers
// ---------------------------------------------------------------------------

Widget _label(String text) => Text(
      text,
      style: GoogleFonts.instrumentSans(
          fontSize: 13,
          fontWeight: FontWeight.w600,
          color: VoyoColors.ink),
    );

InputDecoration _inputDeco(String hint) => InputDecoration(
      hintText: hint,
      hintStyle:
          GoogleFonts.instrumentSans(color: VoyoColors.stone, fontSize: 14),
      filled: true,
      fillColor: VoyoColors.vellum,
      contentPadding:
          const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide.none),
      enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide.none),
      focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide:
              const BorderSide(color: VoyoColors.expedition, width: 1.5)),
    );
