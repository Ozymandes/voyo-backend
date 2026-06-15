import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../models/poi.dart';
import '../services/supabase_service.dart';
import '../theme.dart';

enum _ItinStep { trips, days, slot }

class AddToItineraryFlow extends StatefulWidget {
  final Poi poi;
  final SupabaseService service;
  final String userId;

  const AddToItineraryFlow({
    super.key,
    required this.poi,
    required this.service,
    required this.userId,
  });

  @override
  State<AddToItineraryFlow> createState() => _AddToItineraryFlowState();
}

class _AddToItineraryFlowState extends State<AddToItineraryFlow> {
  _ItinStep _step = _ItinStep.trips;
  bool _loading = true;
  bool _saving = false;

  List<Map<String, dynamic>> _trips = [];
  Map<String, dynamic>? _trip;
  List<Map<String, dynamic>> _items = [];
  int? _day;
  bool _geoWarning = false;

  static const _slots = [
    '08:00:00', '09:00:00', '10:00:00', '11:00:00',
    '12:00:00', '13:00:00', '14:00:00', '15:00:00',
    '16:00:00', '17:00:00', '18:00:00', '19:00:00',
  ];

  @override
  void initState() {
    super.initState();
    _loadTrips();
  }

  Future<void> _loadTrips() async {
    final trips = await widget.service.getAllItineraries(widget.userId);
    if (mounted) setState(() { _trips = trips; _loading = false; });
  }

  Future<void> _pickTrip(Map<String, dynamic>? trip) async {
    setState(() => _loading = true);
    if (trip == null) {
      final created = await widget.service.createItinerary(
          userId: widget.userId, title: 'My Trip');
      if (!mounted || created == null) return;
      setState(() {
        _trip = {'id': created.id, 'title': created.title, 'stop_count': 0, 'status': 'current'};
        _items = [];
        _loading = false;
        _step = _ItinStep.days;
      });
      return;
    }
    final items = await widget.service.getItineraryItemsWithPois(trip['id'] as int);
    if (!mounted) return;
    setState(() {
      _trip = trip;
      _items = items;
      _loading = false;
      _step = _ItinStep.days;
    });
  }

  List<int> get _days =>
      _items.map((i) => i['day_number'] as int).toSet().toList()..sort();

  List<Map<String, dynamic>> _dayItems(int day) =>
      (_items.where((i) => i['day_number'] == day).toList()
        ..sort((a, b) => (a['sequence_order'] as int).compareTo(b['sequence_order'] as int)));

  void _pickDay(int day) {
    final newCity = widget.poi.city;
    final dayCities = _dayItems(day)
        .map((i) => (i['pois'] as Map?)?['city'] as String?)
        .whereType<String>()
        .toSet();
    setState(() {
      _day = day;
      _geoWarning = newCity != null && dayCities.isNotEmpty && !dayCities.contains(newCity);
      _step = _ItinStep.slot;
    });
  }

  Map<String, dynamic>? _conflictAt(String slot) {
    final h = int.tryParse(slot.split(':')[0]);
    if (h == null) return null;
    for (final item in _dayItems(_day!)) {
      final t = item['start_time'] as String?;
      if (t == null) continue;
      if (int.tryParse(t.split(':')[0]) == h) return item;
    }
    return null;
  }

  Future<void> _pickSlot(String slot) async {
    final conflict = _conflictAt(slot);
    if (conflict != null) {
      final conflictName =
          (conflict['pois'] as Map?)?['name'] as String? ?? 'another stop';
      final replace = await showDialog<bool>(
        context: context,
        builder: (_) => AlertDialog(
          backgroundColor: VoyoColors.paper,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          title: Text('Scheduling conflict',
              style: GoogleFonts.fraunces(
                  fontSize: 18, fontStyle: FontStyle.italic, color: VoyoColors.ink)),
          content: Text(
            '"${widget.poi.name}" conflicts with "$conflictName" at this time and will replace it.\n\nWant to add it anyway?',
            style: GoogleFonts.instrumentSans(
                fontSize: 13, color: VoyoColors.stone, height: 1.5),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: Text('Cancel',
                  style: GoogleFonts.instrumentSans(color: VoyoColors.stone)),
            ),
            FilledButton(
              onPressed: () => Navigator.pop(context, true),
              style: FilledButton.styleFrom(
                  backgroundColor: VoyoColors.terra,
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(10))),
              child: Text('Replace',
                  style: GoogleFonts.instrumentSans(fontWeight: FontWeight.w600)),
            ),
          ],
        ),
      );
      if (replace != true || !mounted) return;
      await widget.service.deleteItineraryItem(conflict['id'] as int);
    }

    setState(() => _saving = true);
    try {
      await widget.service.addItineraryItem(
        itineraryId: _trip!['id'] as int,
        poiId: widget.poi.id,
        dayNumber: _day!,
        startTime: slot,
      );
      if (mounted) Navigator.pop(context, true);
    } catch (_) {
      if (mounted) {
        setState(() => _saving = false);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Could not add — please try again.')),
        );
      }
    }
  }

  static String _fmtSlot(String slot) {
    final h = int.tryParse(slot.split(':')[0]) ?? 9;
    if (h == 0) return '12:00 AM';
    if (h < 12) return '$h:00 AM';
    if (h == 12) return '12:00 PM';
    return '${h - 12}:00 PM';
  }

  @override
  Widget build(BuildContext context) {
    return DraggableScrollableSheet(
      initialChildSize: 0.55,
      minChildSize: 0.4,
      maxChildSize: 0.88,
      expand: false,
      builder: (_, controller) => Container(
        decoration: const BoxDecoration(
          color: VoyoColors.paper,
          borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
        ),
        child: _loading || _saving
            ? const Center(
                child: CircularProgressIndicator(
                    strokeWidth: 2, color: VoyoColors.expedition))
            : switch (_step) {
                _ItinStep.trips => _buildTrips(controller),
                _ItinStep.days  => _buildDays(controller),
                _ItinStep.slot  => _buildSlot(controller),
              },
      ),
    );
  }

  Widget _handle() => Center(
        child: Container(
          width: 36,
          height: 4,
          margin: const EdgeInsets.only(top: 12, bottom: 16),
          decoration: BoxDecoration(
              color: VoyoColors.smoke, borderRadius: BorderRadius.circular(2)),
        ),
      );

  Widget _backRow(String label, VoidCallback onTap) => GestureDetector(
        onTap: onTap,
        child: Row(mainAxisSize: MainAxisSize.min, children: [
          const Icon(Icons.arrow_back_ios_rounded, size: 14, color: VoyoColors.stone),
          const SizedBox(width: 4),
          Text(label,
              style: GoogleFonts.instrumentSans(fontSize: 13, color: VoyoColors.stone)),
        ]),
      );

  Widget _buildTrips(ScrollController ctrl) {
    return ListView(
      controller: ctrl,
      padding: const EdgeInsets.fromLTRB(20, 0, 20, 32),
      children: [
        _handle(),
        Text('Add to trip',
            style: GoogleFonts.fraunces(
                fontSize: 22, fontStyle: FontStyle.italic, color: VoyoColors.ink)),
        const SizedBox(height: 4),
        Text('Where should we save ${widget.poi.name}?',
            style: GoogleFonts.instrumentSans(fontSize: 13, color: VoyoColors.stone)),
        const SizedBox(height: 16),
        for (final trip in _trips) ...[
          _TripTile(
            title: trip['title'] as String,
            stopCount: (trip['stop_count'] as int?) ?? 0,
            isCurrent: trip['status'] == 'current',
            onTap: () => _pickTrip(trip),
          ),
          const SizedBox(height: 8),
        ],
        if (_trips.isNotEmpty) const Divider(color: VoyoColors.smoke, height: 24),
        _NewRowButton(label: 'Start a new trip', onTap: () => _pickTrip(null)),
      ],
    );
  }

  Widget _buildDays(ScrollController ctrl) {
    final days = _days;
    return ListView(
      controller: ctrl,
      padding: const EdgeInsets.fromLTRB(20, 0, 20, 32),
      children: [
        _handle(),
        _backRow(_trip!['title'] as String,
            () => setState(() => _step = _ItinStep.trips)),
        const SizedBox(height: 12),
        Text('Choose a day',
            style: GoogleFonts.fraunces(
                fontSize: 22, fontStyle: FontStyle.italic, color: VoyoColors.ink)),
        const SizedBox(height: 16),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: [
            for (final d in days)
              _ItinChip(label: 'Day $d', onTap: () => _pickDay(d)),
            _ItinChip(
              label: '+ New day',
              isAccent: true,
              onTap: () => _pickDay(days.isEmpty ? 1 : days.last + 1),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildSlot(ScrollController ctrl) {
    final items = _dayItems(_day!);
    return ListView(
      controller: ctrl,
      padding: const EdgeInsets.fromLTRB(20, 0, 20, 32),
      children: [
        _handle(),
        _backRow('Day $_day', () => setState(() => _step = _ItinStep.days)),
        const SizedBox(height: 12),
        Text('Pick a time slot',
            style: GoogleFonts.fraunces(
                fontSize: 22, fontStyle: FontStyle.italic, color: VoyoColors.ink)),
        if (_geoWarning) ...[
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: VoyoColors.caution.withValues(alpha: 0.08),
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: VoyoColors.caution.withValues(alpha: 0.35)),
            ),
            child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
              const Icon(Icons.fmd_bad_outlined, size: 16, color: VoyoColors.caution),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  '${widget.poi.name} is in ${widget.poi.city}, which differs from other stops on Day $_day. This may require significant travel.',
                  style: GoogleFonts.instrumentSans(
                      fontSize: 12, color: VoyoColors.ink, height: 1.4),
                ),
              ),
            ]),
          ),
        ],
        if (items.isNotEmpty) ...[
          const SizedBox(height: 16),
          Text('Current stops on Day $_day',
              style: GoogleFonts.instrumentSans(
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                  color: VoyoColors.stone,
                  letterSpacing: 0.4)),
          const SizedBox(height: 8),
          for (final item in items)
            Padding(
              padding: const EdgeInsets.only(bottom: 6),
              child: Row(children: [
                SizedBox(
                  width: 70,
                  child: Text(
                    _fmtSlot((item['start_time'] as String?) ?? '09:00:00'),
                    style: GoogleFonts.jetBrainsMono(fontSize: 11, color: VoyoColors.stone),
                  ),
                ),
                Container(
                    width: 6,
                    height: 6,
                    decoration: const BoxDecoration(
                        color: VoyoColors.expedition, shape: BoxShape.circle)),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    (item['pois'] as Map?)?['name'] as String? ?? 'Stop',
                    style: GoogleFonts.instrumentSans(fontSize: 13, color: VoyoColors.ink),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ]),
            ),
          const SizedBox(height: 8),
          const Divider(color: VoyoColors.smoke),
        ],
        const SizedBox(height: 12),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: [
            for (final slot in _slots)
              _SlotChip(
                label: _fmtSlot(slot),
                hasConflict: _conflictAt(slot) != null,
                onTap: () => _pickSlot(slot),
              ),
          ],
        ),
      ],
    );
  }
}

// ── Helper widgets ─────────────────────────────────────────────────────────────

class _TripTile extends StatelessWidget {
  final String title;
  final int stopCount;
  final bool isCurrent;
  final VoidCallback onTap;

  const _TripTile({
    required this.title,
    required this.stopCount,
    required this.isCurrent,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        decoration: BoxDecoration(
          color: VoyoColors.vellum,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
              color: isCurrent
                  ? VoyoColors.expedition.withValues(alpha: 0.5)
                  : VoyoColors.smoke),
        ),
        child: Row(children: [
          Expanded(
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text(title,
                  style: GoogleFonts.fraunces(
                      fontSize: 16, fontStyle: FontStyle.italic, color: VoyoColors.ink)),
              const SizedBox(height: 2),
              Text('$stopCount stop${stopCount == 1 ? '' : 's'}',
                  style: GoogleFonts.instrumentSans(fontSize: 12, color: VoyoColors.stone)),
            ]),
          ),
          if (isCurrent)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
              decoration: BoxDecoration(
                color: VoyoColors.expedition.withValues(alpha: 0.12),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text('Current',
                  style: GoogleFonts.instrumentSans(
                      fontSize: 10,
                      fontWeight: FontWeight.w600,
                      color: VoyoColors.expedition)),
            )
          else
            const Icon(Icons.chevron_right, color: VoyoColors.smoke, size: 18),
        ]),
      ),
    );
  }
}

class _ItinChip extends StatelessWidget {
  final String label;
  final bool isAccent;
  final VoidCallback onTap;

  const _ItinChip(
      {required this.label, required this.onTap, this.isAccent = false});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
        decoration: BoxDecoration(
          color: VoyoColors.vellum,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
              color: isAccent
                  ? VoyoColors.sky.withValues(alpha: 0.4)
                  : VoyoColors.smoke),
        ),
        child: Text(label,
            style: GoogleFonts.instrumentSans(
                fontSize: 14,
                fontWeight: FontWeight.w600,
                color: isAccent ? VoyoColors.sky : VoyoColors.ink)),
      ),
    );
  }
}

class _SlotChip extends StatelessWidget {
  final String label;
  final bool hasConflict;
  final VoidCallback onTap;

  const _SlotChip(
      {required this.label, required this.hasConflict, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        decoration: BoxDecoration(
          color: hasConflict
              ? VoyoColors.terra.withValues(alpha: 0.06)
              : VoyoColors.vellum,
          borderRadius: BorderRadius.circular(10),
          border: Border.all(
              color: hasConflict
                  ? VoyoColors.terra.withValues(alpha: 0.4)
                  : VoyoColors.smoke),
        ),
        child: Row(mainAxisSize: MainAxisSize.min, children: [
          if (hasConflict) ...[
            const Icon(Icons.warning_amber_rounded, size: 13, color: VoyoColors.terra),
            const SizedBox(width: 4),
          ],
          Text(label,
              style: GoogleFonts.instrumentSans(
                  fontSize: 13,
                  fontWeight: FontWeight.w500,
                  color: hasConflict ? VoyoColors.terra : VoyoColors.ink)),
        ]),
      ),
    );
  }
}

class _NewRowButton extends StatelessWidget {
  final String label;
  final VoidCallback onTap;
  const _NewRowButton({required this.label, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        decoration: BoxDecoration(
          color: VoyoColors.vellum,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: VoyoColors.sky.withValues(alpha: 0.4)),
        ),
        child: Row(children: [
          const Icon(Icons.add_rounded, color: VoyoColors.sky, size: 18),
          const SizedBox(width: 10),
          Text(label,
              style: GoogleFonts.instrumentSans(
                  fontSize: 14, fontWeight: FontWeight.w600, color: VoyoColors.sky)),
        ]),
      ),
    );
  }
}
