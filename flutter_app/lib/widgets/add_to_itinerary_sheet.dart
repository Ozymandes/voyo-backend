import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../models/poi.dart';
import '../services/supabase_service.dart';
import '../theme.dart';

enum _ItinStep { trips, days, slot, blocked }

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

  // Add-POI feasibility verdict from VROOM (Tier 2 honest routing).
  // null = check pending/skipped (not signed in or backend down → the flow
  // falls back to the dumb insert). Loaded right after the user picks a day.
  FeasibilityVerdict? _verdict;
  bool _verdictLoading = false;
  // #22: a *failed* feasibility check is NOT a feasible result. When the
  // backend / matrix engine itself errored (HTTP 503, timeout, network), we
  // render the 'route verification unavailable' state instead of falling
  // through to the generic clock-slot picker — that picker would silently
  // let the user schedule an impossible trip whenever Valhalla errored,
  // which is exactly the failure mode the thesis argues VOYO prevents.
  bool _verdictUnavailable = false;

  // Geographic cluster hard-block state. When the candidate is far from the
  // day's existing cluster (> 150 km, e.g. Mount Sinai on a Luxor day), we
  // move to the `blocked` step instead of offering clock slots — those slots
  // would be 'free' on the clock but geographically impossible.
  String? _geoBlockReason;
  double? _geoBlockDistanceKm;

  // Path B: when true, the user explicitly chose to override CLEO's
  // VROOM-suggested time and is picking a clock slot manually. The
  // deterministic placement card stays the default; manual override is an
  // opt-in secondary action (spec #10/#12: manual + optimize modes both
  // available, never blurred).
  bool _manualTimeOverride = false;

  static const _slots = [
    '08:00:00',
    '09:00:00',
    '10:00:00',
    '11:00:00',
    '12:00:00',
    '13:00:00',
    '14:00:00',
    '15:00:00',
    '16:00:00',
    '17:00:00',
    '18:00:00',
    '19:00:00',
  ];

  @override
  void initState() {
    super.initState();
    _loadTrips();
  }

  Future<void> _loadTrips() async {
    final trips = await widget.service.getAllItineraries(widget.userId);
    if (mounted)
      setState(() {
        _trips = trips;
        _loading = false;
      });
  }

  Future<void> _pickTrip(Map<String, dynamic>? trip) async {
    setState(() => _loading = true);
    if (trip == null) {
      final created = await widget.service.createItinerary(
        userId: widget.userId,
        title: 'My Trip',
      );
      if (!mounted || created == null) return;
      setState(() {
        _trip = {
          'id': created.id,
          'title': created.title,
          'stop_count': 0,
          'status': 'current',
        };
        _items = [];
        _loading = false;
        _step = _ItinStep.days;
      });
      return;
    }
    final items = await widget.service.getItineraryItemsWithPois(
      trip['id'] as int,
    );
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
      (_items.where((i) => i['day_number'] == day).toList()..sort(
        (a, b) =>
            (a['sequence_order'] as int).compareTo(b['sequence_order'] as int),
      ));

  void _pickDay(int day) {
    final newCity = widget.poi.city;
    final dayItems = _dayItems(day);
    final dayCities =
        dayItems
            .map((i) => (i['pois'] as Map?)?['city'] as String?)
            .whereType<String>()
            .toSet();

    // ── Geographic cluster hard-block ──────────────────────────────────
    // A free clock slot is NOT a feasible itinerary slot. If the candidate
    // sits hundreds of km from the day's existing stops (e.g. Mount Sinai on
    // a Luxor day), same-day travel is impossible regardless of which clock
    // hour is empty. Block with alternatives rather than offer fake slots.
    //
    // Uses haversine (cheap, routing-independent) so the block is reliable
    // even when OSRM/Valhalla are down. VROOM provides a second opinion via
    // _verdict on the feasible path.
    //
    // NOTE: pass the *selected* `day` in (not the `_day` state field) — at
    // this point `_day` still holds the PREVIOUS selection (or null on the
    // first pick), so interpolating it into the reason string produced the
    // "Day null route" copy the partner saw in QA.
    final block = _geoClusterBlock(dayItems, selectedDay: day);
    if (block != null) {
      setState(() {
        _day = day;
        _geoBlockReason = block.reason;
        _geoBlockDistanceKm = block.distanceKm;
        _verdict = null;
        _verdictLoading = false;
        _step = _ItinStep.blocked;
      });
      return;
    }

    setState(() {
      _day = day;
      _geoWarning =
          newCity != null &&
          dayCities.isNotEmpty &&
          !dayCities.contains(newCity);
      _geoBlockReason = null;
      _verdict = null;
      _verdictLoading = false;
      _step = _ItinStep.slot;
    });
    // Fire the VROOM feasibility check now that we know the trip + day.
    // Best-effort: failures leave _verdict null and the flow behaves as before.
    _loadVerdict(day);
  }

  /// Returns a [_GeoBlock] if adding the candidate to [dayItems] is a
  /// same-day geographic impossibility, else null. Threshold is 150 km —
  /// cleanly separates Luxor↔Sinai (600 km), Cairo↔Aswan (700 km) from
  /// combinable pairs like Cairo↔Giza (15 km) or Cairo↔Saqqara (30 km).
  _GeoBlock? _geoClusterBlock(List<Map<String, dynamic>> dayItems,
      {required int selectedDay}) {
    final candLat = widget.poi.latitude;
    final candLng = widget.poi.longitude;
    if (dayItems.isEmpty) return null; // empty day → defines its own cluster

    // Collect coordinates of the day's existing stops.
    final cluster = <_LatLng>[];
    String? clusterCity;
    for (final item in dayItems) {
      final p = item['pois'] as Map?;
      final lat = (p?['latitude'] as num?)?.toDouble();
      final lng = (p?['longitude'] as num?)?.toDouble();
      if (lat != null && lng != null) cluster.add(_LatLng(lat, lng));
      final c = p?['city'] as String?;
      if (clusterCity == null && c != null && c.isNotEmpty) clusterCity = c;
    }
    if (cluster.isEmpty || candLat == 0 || candLng == 0) return null;

    // Nearest existing stop distance — the relevant test for 'can this be a
    // same-day stop'. If even the closest stop is > 150 km away, the day is
    // cross-region and infeasible.
    double nearestKm = double.infinity;
    for (final c in cluster) {
      final d = _haversineKm(candLat, candLng, c.lat, c.lng);
      if (d < nearestKm) nearestKm = d;
    }
    const threshold = 150.0; // km
    if (nearestKm > threshold) {
      final clusterName =
          clusterCity ?? (widget.poi.city ?? 'your existing stops');
      return _GeoBlock(
        distanceKm: nearestKm,
        clusterCity: clusterName,
        reason:
            '${widget.poi.name} is ${nearestKm.round()} km from your Day $selectedDay route — '
            'this day is built around $clusterName, while ${widget.poi.name} is in '
            '${widget.poi.city ?? 'a different region'}. A same-day visit would need '
            'major cross-region travel and isn\'t realistic.',
      );
    }
    return null;
  }

  Future<void> _loadVerdict(int day) async {
    final tripId = _trip?['id'] as int?;
    if (tripId == null) return;
    setState(() {
      _verdictLoading = true;
      _verdictUnavailable = false; // fresh day, fresh check
    });
    try {
      final v = await widget.service.previewAdd(
        itineraryId: tripId,
        candidatePoiId: widget.poi.id,
        preferredDay: day,
        days: _days.isEmpty ? 1 : _days.last,
      );
      if (mounted)
        setState(() {
          _verdict = v;
          _verdictLoading = false;
          _verdictUnavailable = false;
        });
    } on PreviewAddUnavailableException catch (e) {
      // Engine/down failure — surface honestly, do NOT fall through to slots.
      debugPrint('preview-add unavailable: $e');
      if (mounted)
        setState(() {
          _verdict = null;
          _verdictLoading = false;
          _verdictUnavailable = true;
        });
    }
  }

  /// Verdict fetch for a BRAND-NEW day ("Create a new Day N here"). Same as
  /// _loadVerdict but passes `days: day` so VROOM actually allocates a
  /// vehicle for the new day instead of the old max — without this the
  /// solver would reject the candidate as unassignable. Also guards against
  /// double-tap (partner QA noted lag): if a verdict is already loading,
  /// the second tap is a no-op.
  Future<void> _loadVerdictForNewDay(int day) async {
    if (_verdictLoading) return; // guard against double-tap
    final tripId = _trip?['id'] as int?;
    if (tripId == null) return;
    setState(() {
      _verdictLoading = true;
      _verdictUnavailable = false;
    });
    try {
      final v = await widget.service.previewAdd(
        itineraryId: tripId,
        candidatePoiId: widget.poi.id,
        preferredDay: day,
        days: day,
      );
      if (mounted)
        setState(() {
          _verdict = v;
          _verdictLoading = false;
          _verdictUnavailable = false;
        });
    } on PreviewAddUnavailableException catch (e) {
      debugPrint('preview-add unavailable (new day): $e');
      if (mounted)
        setState(() {
          _verdict = null;
          _verdictLoading = false;
          _verdictUnavailable = true;
        });
    }
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
    // VROOM hard-block: if the optimizer said this POI won't fit on ANY day,
    // don't let the user force it in — that's the whole point of honest
    // routing. (If the verdict is null the backend was unreachable; fall back
    // to the old behaviour rather than block the user.)
    if (_verdict != null && !_verdict!.feasible && !_verdict!.alreadyOnTrip) {
      await showDialog<void>(
        context: context,
        builder:
            (_) => AlertDialog(
              backgroundColor: VoyoColors.paper,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
              ),
              title: Text(
                "Can't fit this stop",
                style: GoogleFonts.fraunces(
                  fontSize: 18,
                  fontStyle: FontStyle.italic,
                  color: VoyoColors.ink,
                ),
              ),
              content: Text(
                _verdict!.reason,
                style: GoogleFonts.instrumentSans(
                  fontSize: 13,
                  color: VoyoColors.stone,
                  height: 1.5,
                ),
              ),
              actions: [
                FilledButton(
                  onPressed: () => Navigator.pop(context),
                  style: FilledButton.styleFrom(
                    backgroundColor: VoyoColors.ink,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(10),
                    ),
                  ),
                  child: Text(
                    'Got it',
                    style: GoogleFonts.instrumentSans(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ],
            ),
      );
      return;
    }
    final conflict = _conflictAt(slot);
    if (conflict != null) {
      final conflictName =
          (conflict['pois'] as Map?)?['name'] as String? ?? 'another stop';
      final replace = await showDialog<bool>(
        context: context,
        builder:
            (_) => AlertDialog(
              backgroundColor: VoyoColors.paper,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
              ),
              title: Text(
                'Scheduling conflict',
                style: GoogleFonts.fraunces(
                  fontSize: 18,
                  fontStyle: FontStyle.italic,
                  color: VoyoColors.ink,
                ),
              ),
              content: Text(
                '"${widget.poi.name}" conflicts with "$conflictName" at this time and will replace it.\n\nWant to add it anyway?',
                style: GoogleFonts.instrumentSans(
                  fontSize: 13,
                  color: VoyoColors.stone,
                  height: 1.5,
                ),
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(context, false),
                  child: Text(
                    'Cancel',
                    style: GoogleFonts.instrumentSans(color: VoyoColors.stone),
                  ),
                ),
                FilledButton(
                  onPressed: () => Navigator.pop(context, true),
                  style: FilledButton.styleFrom(
                    backgroundColor: VoyoColors.terra,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(10),
                    ),
                  ),
                  child: Text(
                    'Replace',
                    style: GoogleFonts.instrumentSans(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ],
            ),
      );
      if (replace != true || !mounted) return;
      await widget.service.deleteItineraryItem(conflict['id'] as int);
    }

    setState(() => _saving = true);
    try {
      // Debug trace (#5): confirms the selected slot is exactly what reaches
      // the DB. If a POI ever lands at the wrong time, these four lines show
      // whether the bug is in selection (slot != picked) or persistence
      // (DB mutated it). Inspect via `flutter run` console.
      debugPrint('═══ itinerary insert ═══');
      debugPrint('  selectedSlotBeforeConfirm: $slot');
      debugPrint('  poiId: ${widget.poi.id}  dayId: $_day');
      debugPrint(
        '  computedFeasibleSlot: ${_verdict?.recommendedDay != null ? "verdict driven" : "none"}',
      );
      debugPrint('  finalInsertedStartTime: $slot');
      await widget.service.addItineraryItem(
        itineraryId: _trip!['id'] as int,
        poiId: widget.poi.id,
        dayNumber: _day!,
        startTime: slot,
      );
      debugPrint(
        '  renderedTimelineStartTime: (visible after planner reload — sorted chronologically)',
      );
      debugPrint('══════════════════════════');
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

  // ── VROOM feasibility verdict banner ─────────────────────────────────
  // Renders the optimizer's honest take on adding this POI. Colour-coded so
  // the user gets the verdict at a glance; the `reason` string comes
  // straight from the backend (already VOYO-voiced).
  Widget _buildVerdictBanner() {
    if (_verdictLoading) {
      return Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: VoyoColors.vellum,
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: VoyoColors.smoke),
        ),
        child: Row(
          children: [
            const SizedBox(
              width: 14,
              height: 14,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                color: VoyoColors.stone,
              ),
            ),
            const SizedBox(width: 10),
            Text(
              'Checking if it fits…',
              style: GoogleFonts.instrumentSans(
                fontSize: 12,
                color: VoyoColors.stone,
                fontStyle: FontStyle.italic,
              ),
            ),
          ],
        ),
      );
    }
    final v = _verdict!;
    final tone = _verdictColor(v);
    final icon = _verdictIcon(v);
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: tone.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: tone.withValues(alpha: 0.4)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, size: 16, color: tone),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  v.reason,
                  style: GoogleFonts.instrumentSans(
                    fontSize: 12,
                    color: VoyoColors.ink,
                    height: 1.45,
                  ),
                ),
                if (_shouldOfferDaySwitch(v)) ...[
                  const SizedBox(height: 8),
                  _buildDaySwitchAction(v, tone),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }

  bool _shouldOfferDaySwitch(FeasibilityVerdict v) =>
      v.feasible &&
      !v.alreadyOnTrip &&
      v.recommendedDay != null &&
      v.recommendedDay != _day;

  Widget _buildDaySwitchAction(FeasibilityVerdict v, Color tone) {
    return GestureDetector(
      onTap: () {
        setState(() => _day = v.recommendedDay);
        _loadVerdict(v.recommendedDay!);
      },
      child: Text(
        'Add to Day ${v.recommendedDay} instead',
        style: GoogleFonts.instrumentSans(
          fontSize: 12,
          fontWeight: FontWeight.w700,
          color: tone,
          decoration: TextDecoration.underline,
        ),
      ),
    );
  }

  Color _verdictColor(FeasibilityVerdict v) {
    if (v.alreadyOnTrip) return VoyoColors.stone;
    if (!v.feasible) return VoyoColors.terra;
    if (v.displacedPois.isNotEmpty) return VoyoColors.caution;
    if (v.preferredDay != null && !v.preferredDayFeasible)
      return VoyoColors.caution;
    return VoyoColors.verified;
  }

  IconData _verdictIcon(FeasibilityVerdict v) {
    if (v.alreadyOnTrip) return Icons.check_circle_outline;
    if (!v.feasible) return Icons.block_rounded;
    if (v.displacedPois.isNotEmpty) return Icons.warning_amber_rounded;
    if (v.preferredDay != null && !v.preferredDayFeasible) {
      return Icons.swap_horiz_rounded;
    }
    return Icons.check_circle_rounded;
  }

  static String _fmtSlot(String slot) {
    final h = int.tryParse(slot.split(':')[0]) ?? 9;
    if (h == 0) return '12:00 AM';
    if (h < 12) return '$h:00 AM';
    if (h == 12) return '12:00 PM';
    return '${h - 12}:00 PM';
  }

  /// Honest time label for a stop. Null/empty start_time → "Unscheduled"
  /// (never a fake 9:00 AM). This matters because the feasibility engine
  /// can't be trusted if the visible schedule is full of placeholder times.
  static String _stopTimeLabel(String? start) {
    if (start == null || start.trim().isEmpty) return 'Unscheduled';
    return _fmtSlot(start);
  }

  /// Honest name label for a stop. Prefers the joined POI name; falls back
  /// to a clearly-marked placeholder so a "Stop" row is always
  /// debuggable ("POI #123") instead of an ambiguous "Stop".
  static String _stopNameLabel(Map<String, dynamic> item) {
    final p = item['pois'] as Map?;
    final name = p?['name'] as String?;
    if (name != null && name.trim().isNotEmpty) return name;
    // The POI join returned nothing usable. Mark it honestly rather than
    // render a bare "Stop" — this surfaces data gaps instead of hiding them.
    final poiId = item['poi_id'];
    return poiId != null ? 'POI #$poiId (loading…)' : 'Unscheduled stop';
  }

  @override
  Widget build(BuildContext context) {
    return DraggableScrollableSheet(
      initialChildSize: 0.55,
      minChildSize: 0.4,
      maxChildSize: 0.88,
      expand: false,
      builder:
          (_, controller) => Container(
            decoration: const BoxDecoration(
              color: VoyoColors.paper,
              borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
            ),
            child:
                _loading || _saving
                    ? const Center(
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: VoyoColors.expedition,
                      ),
                    )
                    : switch (_step) {
                      _ItinStep.trips => _buildTrips(controller),
                      _ItinStep.days => _buildDays(controller),
                      _ItinStep.slot => _buildSlot(controller),
                      _ItinStep.blocked => _buildBlocked(controller),
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
        color: VoyoColors.smoke,
        borderRadius: BorderRadius.circular(2),
      ),
    ),
  );

  Widget _backRow(String label, VoidCallback onTap) => GestureDetector(
    onTap: onTap,
    child: Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        const Icon(
          Icons.arrow_back_ios_rounded,
          size: 14,
          color: VoyoColors.stone,
        ),
        const SizedBox(width: 4),
        Text(
          label,
          style: GoogleFonts.instrumentSans(
            fontSize: 13,
            color: VoyoColors.stone,
          ),
        ),
      ],
    ),
  );

  Widget _buildTrips(ScrollController ctrl) {
    return ListView(
      controller: ctrl,
      padding: const EdgeInsets.fromLTRB(20, 0, 20, 32),
      children: [
        _handle(),
        Text(
          'Add to trip',
          style: GoogleFonts.fraunces(
            fontSize: 22,
            fontStyle: FontStyle.italic,
            color: VoyoColors.ink,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          'Where should we save ${widget.poi.name}?',
          style: GoogleFonts.instrumentSans(
            fontSize: 13,
            color: VoyoColors.stone,
          ),
        ),
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
        if (_trips.isNotEmpty)
          const Divider(color: VoyoColors.smoke, height: 24),
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
        _backRow(
          _trip!['title'] as String,
          () => setState(() => _step = _ItinStep.trips),
        ),
        const SizedBox(height: 12),
        Text(
          'Choose a day',
          style: GoogleFonts.fraunces(
            fontSize: 22,
            fontStyle: FontStyle.italic,
            color: VoyoColors.ink,
          ),
        ),
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

  /// Geographic-cluster hard-block step. Shown when the candidate is too
  /// far from the selected day's cluster for a realistic same-day visit.
  /// Offers concrete alternatives instead of fake free clock slots. An
  /// advanced 'Add anyway' is intentionally omitted from the primary path —
  /// per the spec, unrealistic overrides shouldn't reach the optimized plan.
  Widget _buildBlocked(ScrollController ctrl) {
    final reason =
        _geoBlockReason ??
        'This stop is too far from the selected day for a realistic same-day visit.';
    final dist = _geoBlockDistanceKm;
    final nextDay = (_days.isEmpty ? 0 : _days.last) + 1;
    return ListView(
      controller: ctrl,
      padding: const EdgeInsets.fromLTRB(20, 0, 20, 32),
      children: [
        _handle(),
        _backRow('Day $_day', () => setState(() => _step = _ItinStep.days)),
        const SizedBox(height: 16),
        Container(
          width: 52,
          height: 52,
          decoration: BoxDecoration(
            color: VoyoColors.terra.withValues(alpha: 0.12),
            shape: BoxShape.circle,
          ),
          child: const Icon(
            Icons.map_outlined,
            color: VoyoColors.terra,
            size: 26,
          ),
        ),
        const SizedBox(height: 14),
        Text(
          "Can't fit this on Day $_day",
          style: GoogleFonts.fraunces(
            fontSize: 22,
            fontStyle: FontStyle.italic,
            color: VoyoColors.ink,
          ),
        ),
        const SizedBox(height: 10),
        Text(
          reason,
          style: GoogleFonts.instrumentSans(
            fontSize: 13,
            color: VoyoColors.stone,
            height: 1.55,
          ),
        ),
        if (dist != null) ...[
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            decoration: BoxDecoration(
              color: VoyoColors.vellum,
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: VoyoColors.smoke),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(
                  Icons.straighten_rounded,
                  size: 15,
                  color: VoyoColors.stone,
                ),
                const SizedBox(width: 6),
                Text(
                  '${dist.round()} km from your Day $_day stops',
                  style: GoogleFonts.jetBrainsMono(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: VoyoColors.ink,
                  ),
                ),
              ],
            ),
          ),
        ],
        const SizedBox(height: 22),
        Text(
          'What you can do',
          style: GoogleFonts.instrumentSans(
            fontSize: 12,
            fontWeight: FontWeight.w600,
            color: VoyoColors.stone,
            letterSpacing: 0.4,
          ),
        ),
        const SizedBox(height: 10),
        // Create a new day centred on this POI's region.
        _BlockedAction(
          icon: Icons.add_circle_outline_rounded,
          title: 'Create a new Day $nextDay here',
          subtitle:
              'Start a fresh day built around ${widget.poi.city ?? 'this area'}.',
          onTap: () {
            // A brand-new empty day has no cluster to conflict with, so the
            // geographic block is moot and VROOM would just confirm it fits.
            // Skip straight to the slot step (no verdict round-trip — that's
            // what made this button feel laggy). The placement card renders
            // immediately with VROOM's first computed slot.
            setState(() {
              _day = nextDay;
              _geoBlockReason = null;
              _verdict = null;
              _verdictLoading = false;
              _step = _ItinStep.slot;
            });
            // VROOM verdict is still useful for the placement card, but we
            // pass the CORRECT day count (nextDay, not _days.last) so the
            // solver actually has a vehicle for the new day.
            _loadVerdictForNewDay(nextDay);
          },
        ),
        // Try a different existing day.
        if (_days.length > 1 || _days.isEmpty) ...[
          const SizedBox(height: 8),
          _BlockedAction(
            icon: Icons.swap_horiz_rounded,
            title: 'Choose a different day',
            subtitle: 'Pick another day whose stops are closer.',
            onTap: () => setState(() => _step = _ItinStep.days),
          ),
        ],
        const SizedBox(height: 8),
        _BlockedAction(
          icon: Icons.close_rounded,
          title: 'Cancel',
          subtitle: 'Don\'t add this stop right now.',
          onTap: () => Navigator.pop(context, false),
          destructive: false,
          muted: true,
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
        Text(
          'Pick a time slot',
          style: GoogleFonts.fraunces(
            fontSize: 22,
            fontStyle: FontStyle.italic,
            color: VoyoColors.ink,
          ),
        ),
        if (_geoWarning) ...[
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: VoyoColors.caution.withValues(alpha: 0.08),
              borderRadius: BorderRadius.circular(10),
              border: Border.all(
                color: VoyoColors.caution.withValues(alpha: 0.35),
              ),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(
                  Icons.fmd_bad_outlined,
                  size: 16,
                  color: VoyoColors.caution,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    '${widget.poi.name} is in ${widget.poi.city}, which differs from other stops on Day $_day. This may require significant travel.',
                    style: GoogleFonts.instrumentSans(
                      fontSize: 12,
                      color: VoyoColors.ink,
                      height: 1.4,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
        // ── VROOM feasibility verdict (Tier 2 honest routing) ──────────────
        // Shows what the real optimizer thinks of adding this POI: green
        // (fits), amber (fits on a different day / would displace a stop),
        // red (won't fit anywhere). While pending or if the backend is down,
        // we show nothing — the flow degrades to the original dumb insert.
        if (_verdictLoading || _verdict != null) ...[
          const SizedBox(height: 12),
          _buildVerdictBanner(),
        ],
        if (items.isNotEmpty) ...[
          const SizedBox(height: 16),
          Text(
            'Current stops on Day $_day',
            style: GoogleFonts.instrumentSans(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: VoyoColors.stone,
              letterSpacing: 0.4,
            ),
          ),
          const SizedBox(height: 8),
          for (final item in items)
            Padding(
              padding: const EdgeInsets.only(bottom: 6),
              child: Row(
                children: [
                  SizedBox(
                    width: 70,
                    child: Text(
                      _stopTimeLabel(item['start_time'] as String?),
                      style: GoogleFonts.jetBrainsMono(
                        fontSize: 11,
                        color: VoyoColors.stone,
                        fontStyle:
                            (item['start_time'] == null)
                                ? FontStyle.italic
                                : FontStyle.normal,
                      ),
                    ),
                  ),
                  Container(
                    width: 6,
                    height: 6,
                    decoration: const BoxDecoration(
                      color: VoyoColors.expedition,
                      shape: BoxShape.circle,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      _stopNameLabel(item),
                      style: GoogleFonts.instrumentSans(
                        fontSize: 13,
                        color: VoyoColors.ink,
                      ),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
            ),
          const SizedBox(height: 8),
          const Divider(color: VoyoColors.smoke),
        ],
        const SizedBox(height: 14),
        // ── Path B: deterministic placement vs manual override (#20/#22) ────
        // ORDER MATTERS HERE. A failed feasibility check (engine error /
        // 503 / network) must render the 'route verification unavailable'
        // state — it must NOT fall through to the clock-slot grid, which
        // would silently let the user schedule an impossible trip. The
        // generic picker is reachable ONLY after a successful verdict (or
        // an explicit manual override of a successful one).
        if (_verdictLoading)
          _buildComputingPlacement()
        else if (_verdictUnavailable)
          _buildRouteUnavailable()
        else if (_verdict?.candidatePlacement != null &&
            _verdict!.candidatePlacement!.arrivalTime != null &&
            !_manualTimeOverride)
          _buildPlacementCard()
        else if (_verdict != null && !_verdict!.feasible)
          _buildInfeasibleFromVerdict()
        else
          _buildManualSlots(),
      ],
    );
  }

  /// Shown while VROOM is computing the optimal slot for this candidate.
  Widget _buildComputingPlacement() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: VoyoColors.vellum,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: VoyoColors.smoke),
      ),
      child: Row(
        children: [
          const SizedBox(
            width: 18,
            height: 18,
            child: CircularProgressIndicator(
                strokeWidth: 2, color: VoyoColors.expedition),
          ),
          const SizedBox(width: 12),
          Text(
            'Finding the best time on Day $_day…',
            style: GoogleFonts.instrumentSans(
                fontSize: 13, color: VoyoColors.stone),
          ),
        ],
      ),
    );
  }

  /// Path B primary: the VROOM-determined placement card. Commits the POI at
  /// the optimizer's exact arrival time, with a one-line route rationale
  /// ("between X and Y") and an opt-in manual override.
  Widget _buildPlacementCard() {
    final p = _verdict!.candidatePlacement!;
    final time = _formatPlacementTime(p.arrivalTime!);
    // Build the "between X and Y" copy from VROOM's neighbours. When the POI
    // is first or last in the day, the copy adapts ("to start your day" /
    // "to finish your day").
    String rationale;
    if (p.previousName == null && p.nextName == null) {
      rationale = 'A focused day around ${widget.poi.name}.';
    } else if (p.previousName == null) {
      rationale = 'To start your day, before ${p.nextName}.';
    } else if (p.nextName == null) {
      rationale = 'After ${p.previousName}, to finish your day.';
    } else {
      rationale = 'Between ${p.previousName} and ${p.nextName}.';
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: VoyoColors.expedition.withValues(alpha: 0.05),
            borderRadius: BorderRadius.circular(14),
            border: Border.all(
                color: VoyoColors.expedition.withValues(alpha: 0.3)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(Icons.route_rounded,
                      size: 16, color: VoyoColors.expedition),
                  const SizedBox(width: 6),
                  Text(
                    'CLEO suggests $time',
                    style: GoogleFonts.fraunces(
                      fontSize: 18,
                      fontStyle: FontStyle.italic,
                      color: VoyoColors.ink,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Text(
                rationale,
                style: GoogleFonts.instrumentSans(
                    fontSize: 12.5, color: VoyoColors.stone, height: 1.45),
              ),
              const SizedBox(height: 6),
              Text(
                'This keeps your route efficient and avoids backtracking.',
                style: GoogleFonts.instrumentSans(
                  fontSize: 11.5,
                  color: VoyoColors.expedition,
                  fontStyle: FontStyle.italic,
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 12),
        // Primary: commit at the VROOM slot. Reuses _pickSlot so the same
        // conflict-aware save path applies.
        FilledButton.icon(
          onPressed: _saving
              ? null
              : () => _pickSlot(p.arrivalTime!),
          style: FilledButton.styleFrom(
            backgroundColor: VoyoColors.expedition,
            padding: const EdgeInsets.symmetric(vertical: 15),
            shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(14)),
          ),
          icon: _saving
              ? const SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(
                      strokeWidth: 2, color: Colors.white))
              : const Icon(Icons.check_rounded, color: Colors.white, size: 20),
          label: Text(
            'Add at $time',
            style: GoogleFonts.instrumentSans(
              fontSize: 15,
              fontWeight: FontWeight.w700,
              color: Colors.white,
            ),
          ),
        ),
        const SizedBox(height: 8),
        // Manual override: opt-in, secondary. Keeps manual mode available
        // per the spec without making it the default that stamps fake times.
        TextButton.icon(
          onPressed: () => setState(() => _manualTimeOverride = true),
          icon: const Icon(Icons.schedule_outlined,
              size: 16, color: VoyoColors.stone),
          label: Text(
            'Choose a different time',
            style: GoogleFonts.instrumentSans(
                fontSize: 12.5, color: VoyoColors.stone),
          ),
        ),
      ],
    );
  }

  /// The legacy clock-grid. Now the fallback: shown when the backend is
  /// unreachable (no verdict) OR the user explicitly chose manual override.
  Widget _buildManualSlots() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (_manualTimeOverride)
          Padding(
            padding: const EdgeInsets.only(bottom: 10),
            child: GestureDetector(
              onTap: () => setState(() => _manualTimeOverride = false),
              child: Row(
                children: [
                  const Icon(Icons.arrow_back_rounded,
                      size: 15, color: VoyoColors.expedition),
                  const SizedBox(width: 4),
                  Text(
                    'Use CLEO\'s suggested time',
                    style: GoogleFonts.instrumentSans(
                        fontSize: 12,
                        color: VoyoColors.expedition,
                        fontWeight: FontWeight.w600),
                  ),
                ],
              ),
            ),
          ),
        Text(
          _manualTimeOverride ? 'Pick a time' : 'Pick a time slot',
          style: GoogleFonts.instrumentSans(
            fontSize: 13,
            fontWeight: FontWeight.w600,
            color: VoyoColors.stone,
          ),
        ),
        const SizedBox(height: 10),
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

  /// "HH:MM:SS" → "2:00 PM" for the placement card.
  String _formatPlacementTime(String t) {
    final parts = t.split(':');
    if (parts.length < 2) return t;
    final h = int.tryParse(parts[0]) ?? 0;
    final m = int.tryParse(parts[1]) ?? 0;
    if (h == 0) return '12:${m.toString().padLeft(2, "0")} AM';
    if (h < 12) return '$h:${m.toString().padLeft(2, "0")} AM';
    if (h == 12) return '12:${m.toString().padLeft(2, "0")} PM';
    return '${h - 12}:${m.toString().padLeft(2, "0")} PM';
  }

  // ── #22 honesty states ───────────────────────────────────────────────
  // Two states below replace the old 'fall through to clock grid' behaviour
  // whenever the feasibility check itself fails or returns infeasible.
  // Neither offers the unverified clock grid: VOYO never pretends an
  // itinerary is feasible when it couldn't verify it.

  /// Shown when the route engine itself failed (503 / network / timeout).
  /// This is the state that closes the regression: previously this case
  /// silently rendered the generic 8 AM–7 PM clock grid, letting users
  /// schedule trips the engine never verified. Now it surfaces the failure
  /// honestly with concrete next actions.
  Widget _buildRouteUnavailable() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: VoyoColors.terra.withValues(alpha: 0.06),
            borderRadius: BorderRadius.circular(14),
            border:
                Border.all(color: VoyoColors.terra.withValues(alpha: 0.4)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(Icons.shield_outlined,
                      size: 16, color: VoyoColors.terra),
                  const SizedBox(width: 6),
                  Text(
                    'Couldn\'t verify this route',
                    style: GoogleFonts.fraunces(
                      fontSize: 17,
                      fontStyle: FontStyle.italic,
                      color: VoyoColors.ink,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Text(
                'VOYO needs route timing before adding this stop safely. '
                'Please try again, choose another day, or open the route externally.',
                style: GoogleFonts.instrumentSans(
                    fontSize: 12.5, color: VoyoColors.stone, height: 1.5),
              ),
            ],
          ),
        ),
        const SizedBox(height: 12),
        FilledButton.icon(
          onPressed: _saving
              ? null
              : () {
                  // Re-run the feasibility check for the current day.
                  if (_day != null) _loadVerdict(_day!);
                },
          style: FilledButton.styleFrom(
            backgroundColor: VoyoColors.expedition,
            padding: const EdgeInsets.symmetric(vertical: 14),
            shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(14)),
          ),
          icon: _saving
              ? const SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(
                      strokeWidth: 2, color: Colors.white))
              : const Icon(Icons.refresh_rounded, color: Colors.white, size: 18),
          label: Text(
            'Try again',
            style: GoogleFonts.instrumentSans(
                fontSize: 14, fontWeight: FontWeight.w700, color: Colors.white),
          ),
        ),
        const SizedBox(height: 8),
        OutlinedButton.icon(
          onPressed: () => setState(() => _step = _ItinStep.days),
          icon: const Icon(Icons.swap_horiz_rounded,
              size: 16, color: VoyoColors.ink),
          label: Text(
            'Choose a different day',
            style: GoogleFonts.instrumentSans(
                fontSize: 13, fontWeight: FontWeight.w600, color: VoyoColors.ink),
          ),
          style: OutlinedButton.styleFrom(
            side: BorderSide(color: VoyoColors.smoke),
            padding: const EdgeInsets.symmetric(vertical: 12),
            shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(14)),
          ),
        ),
        const SizedBox(height: 8),
        TextButton.icon(
          onPressed: () => Navigator.pop(context, false),
          icon: const Icon(Icons.close_rounded,
              size: 16, color: VoyoColors.stone),
          label: Text(
            'Cancel',
            style: GoogleFonts.instrumentSans(
                fontSize: 13, color: VoyoColors.stone),
          ),
        ),
      ],
    );
  }

  /// Shown when VROOM ran successfully and returned infeasible (the candidate
  /// lands in `unassigned`). Distinct from _buildRouteUnavailable: here we
  // *do* have a verified answer — the answer is 'no'.
  Widget _buildInfeasibleFromVerdict() {
    final reason = _verdict?.reason.isEmpty ?? true
        ? 'This stop won\'t fit on Day $_day given the current time budget and '
            'opening hours. Try another day or trim an existing stop.'
        : _verdict!.reason;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: VoyoColors.caution.withValues(alpha: 0.06),
            borderRadius: BorderRadius.circular(14),
            border: Border.all(color: VoyoColors.caution.withValues(alpha: 0.4)),
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(Icons.warning_amber_rounded,
                  size: 16, color: VoyoColors.caution),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  reason,
                  style: GoogleFonts.instrumentSans(
                      fontSize: 12.5, color: VoyoColors.ink, height: 1.5),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 12),
        OutlinedButton.icon(
          onPressed: () => setState(() => _step = _ItinStep.days),
          icon: const Icon(Icons.swap_horiz_rounded,
              size: 16, color: VoyoColors.ink),
          label: Text(
            'Choose a different day',
            style: GoogleFonts.instrumentSans(
                fontSize: 13, fontWeight: FontWeight.w600, color: VoyoColors.ink),
          ),
          style: OutlinedButton.styleFrom(
            side: BorderSide(color: VoyoColors.smoke),
            padding: const EdgeInsets.symmetric(vertical: 14),
            shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(14)),
          ),
        ),
        const SizedBox(height: 8),
        TextButton.icon(
          onPressed: () => Navigator.pop(context, false),
          icon: const Icon(Icons.close_rounded,
              size: 16, color: VoyoColors.stone),
          label: Text(
            'Cancel',
            style: GoogleFonts.instrumentSans(
                fontSize: 13, color: VoyoColors.stone),
          ),
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
            color:
                isCurrent
                    ? VoyoColors.expedition.withValues(alpha: 0.5)
                    : VoyoColors.smoke,
          ),
        ),
        child: Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: GoogleFonts.fraunces(
                      fontSize: 16,
                      fontStyle: FontStyle.italic,
                      color: VoyoColors.ink,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    '$stopCount stop${stopCount == 1 ? '' : 's'}',
                    style: GoogleFonts.instrumentSans(
                      fontSize: 12,
                      color: VoyoColors.stone,
                    ),
                  ),
                ],
              ),
            ),
            if (isCurrent)
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: VoyoColors.expedition.withValues(alpha: 0.12),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  'Current',
                  style: GoogleFonts.instrumentSans(
                    fontSize: 10,
                    fontWeight: FontWeight.w600,
                    color: VoyoColors.expedition,
                  ),
                ),
              )
            else
              const Icon(
                Icons.chevron_right,
                color: VoyoColors.smoke,
                size: 18,
              ),
          ],
        ),
      ),
    );
  }
}

class _ItinChip extends StatelessWidget {
  final String label;
  final bool isAccent;
  final VoidCallback onTap;

  const _ItinChip({
    required this.label,
    required this.onTap,
    this.isAccent = false,
  });

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
            color:
                isAccent
                    ? VoyoColors.sky.withValues(alpha: 0.4)
                    : VoyoColors.smoke,
          ),
        ),
        child: Text(
          label,
          style: GoogleFonts.instrumentSans(
            fontSize: 14,
            fontWeight: FontWeight.w600,
            color: isAccent ? VoyoColors.sky : VoyoColors.ink,
          ),
        ),
      ),
    );
  }
}

class _SlotChip extends StatelessWidget {
  final String label;
  final bool hasConflict;
  final VoidCallback onTap;

  const _SlotChip({
    required this.label,
    required this.hasConflict,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        decoration: BoxDecoration(
          color:
              hasConflict
                  ? VoyoColors.terra.withValues(alpha: 0.06)
                  : VoyoColors.vellum,
          borderRadius: BorderRadius.circular(10),
          border: Border.all(
            color:
                hasConflict
                    ? VoyoColors.terra.withValues(alpha: 0.4)
                    : VoyoColors.smoke,
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (hasConflict) ...[
              const Icon(
                Icons.warning_amber_rounded,
                size: 13,
                color: VoyoColors.terra,
              ),
              const SizedBox(width: 4),
            ],
            Text(
              label,
              style: GoogleFonts.instrumentSans(
                fontSize: 13,
                fontWeight: FontWeight.w500,
                color: hasConflict ? VoyoColors.terra : VoyoColors.ink,
              ),
            ),
          ],
        ),
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
        child: Row(
          children: [
            const Icon(Icons.add_rounded, color: VoyoColors.sky, size: 18),
            const SizedBox(width: 10),
            Text(
              label,
              style: GoogleFonts.instrumentSans(
                fontSize: 14,
                fontWeight: FontWeight.w600,
                color: VoyoColors.sky,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Geographic hard-block verdict from `_geoClusterBlock`.
class _GeoBlock {
  final double distanceKm;
  final String clusterCity;
  final String reason;
  const _GeoBlock({
    required this.distanceKm,
    required this.clusterCity,
    required this.reason,
  });
}

class _LatLng {
  final double lat;
  final double lng;
  const _LatLng(this.lat, this.lng);
}

/// Haversine great-circle distance in km. Used for the geographic cluster
/// hard-block (cheap + routing-independent, so the block is reliable even
/// when OSRM/Valhalla are down).
double _haversineKm(double lat1, double lng1, double lat2, double lng2) {
  const r = 6371.0;
  double toRad(double d) => d * math.pi / 180.0;
  final dLat = toRad(lat2 - lat1);
  final dLng = toRad(lng2 - lng1);
  final a =
      math.sin(dLat / 2) * math.sin(dLat / 2) +
      math.cos(toRad(lat1)) *
          math.cos(toRad(lat2)) *
          math.sin(dLng / 2) *
          math.sin(dLng / 2);
  return r * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a));
}

/// A single alternative action in the blocked-step list.
class _BlockedAction extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final VoidCallback onTap;
  final bool destructive;
  final bool muted;

  const _BlockedAction({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.onTap,
    this.destructive = false,
    this.muted = false,
  });

  @override
  Widget build(BuildContext context) {
    final accent =
        destructive
            ? VoyoColors.terra
            : (muted ? VoyoColors.stone : VoyoColors.expedition);
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
          decoration: BoxDecoration(
            color: accent.withValues(alpha: 0.06),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: accent.withValues(alpha: 0.2)),
          ),
          child: Row(
            children: [
              Icon(icon, size: 20, color: accent),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      title,
                      style: GoogleFonts.instrumentSans(
                        fontSize: 13.5,
                        fontWeight: FontWeight.w600,
                        color: VoyoColors.ink,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      subtitle,
                      style: GoogleFonts.instrumentSans(
                        fontSize: 11.5,
                        color: VoyoColors.stone,
                        height: 1.35,
                      ),
                    ),
                  ],
                ),
              ),
              Icon(
                Icons.chevron_right_rounded,
                size: 20,
                color: accent.withValues(alpha: 0.6),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
