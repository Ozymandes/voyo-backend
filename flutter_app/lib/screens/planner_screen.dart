import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../models/itinerary.dart';
import '../services/supabase_service.dart';
import '../theme.dart';
import 'map_screen.dart';

class PlannerScreen extends StatefulWidget {
  const PlannerScreen({super.key});

  @override
  State<PlannerScreen> createState() => _PlannerScreenState();
}

class _PlannerScreenState extends State<PlannerScreen> {
  final _service = SupabaseService();
  final _supabase = Supabase.instance.client;

  Itinerary? _itinerary;
  List<Map<String, dynamic>> _items = [];
  bool _loading = true;
  String? _error;

  String? get _userId => _supabase.auth.currentUser?.id;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() { _loading = true; _error = null; });
    final uid = _userId;
    if (uid == null) {
      setState(() => _loading = false);
      return;
    }
    try {
      final itinerary = await _service.getCurrentItinerary(uid);
      List<Map<String, dynamic>> items = [];
      if (itinerary != null) {
        items = await _service.getItineraryItemsWithPois(itinerary.id);
      }
      if (mounted) setState(() { _itinerary = itinerary; _items = items; _loading = false; });
    } catch (e) {
      if (mounted) setState(() { _error = e.toString(); _loading = false; });
    }
  }

  // Groups items by day number
  Map<int, List<Map<String, dynamic>>> get _byDay {
    final map = <int, List<Map<String, dynamic>>>{};
    for (final item in _items) {
      final day = item['day_number'] as int;
      map.putIfAbsent(day, () => []).add(item);
    }
    return map;
  }

  int get _currentDayNumber {
    final start = _itinerary?.startDate;
    if (start == null) return 1;
    final diff = DateTime.now().difference(start).inDays + 1;
    return diff.clamp(1, 999);
  }

  bool _isVisited(Map<String, dynamic> item) {
    final day = item['day_number'] as int;
    final cur = _currentDayNumber;
    if (day < cur) return true;
    if (day > cur) return false;
    // Same day — check if time has passed
    final timeStr = item['start_time'] as String? ?? '23:59:00';
    final parts = timeStr.split(':');
    final stopTime = TimeOfDay(
      hour: int.parse(parts[0]),
      minute: int.parse(parts[1]),
    );
    final now = TimeOfDay.now();
    return now.hour > stopTime.hour ||
        (now.hour == stopTime.hour && now.minute > stopTime.minute);
  }

  bool _isCurrent(Map<String, dynamic> item) {
    final day = item['day_number'] as int;
    if (day != _currentDayNumber) return false;
    final dayItems = _byDay[day] ?? [];
    // Current = first non-visited stop of today
    for (final d in dayItems) {
      if (!_isVisited(d)) return d == item;
    }
    return false;
  }

  @override
  Widget build(BuildContext context) {
    final top = MediaQuery.of(context).padding.top;
    return Scaffold(
      backgroundColor: VoyoColors.page,
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: VoyoColors.terra, strokeWidth: 2))
          : _error != null
              ? _buildError()
              : _itinerary == null
                  ? _buildEmptyState(top)
                  : _buildPlanner(top),
    );
  }

  // ── Empty state ───────────────────────────────────────────────────────────

  Widget _buildEmptyState(double top) {
    return CustomScrollView(
      slivers: [
        SliverToBoxAdapter(child: _buildHeader(top, null)),
        SliverFillRemaining(
          child: Center(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 36),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Icon(Icons.calendar_today_outlined,
                      size: 56, color: VoyoColors.smoke),
                  const SizedBox(height: 20),
                  Text(
                    'Your itinerary is waiting.',
                    style: GoogleFonts.fraunces(
                        fontSize: 26,
                        fontStyle: FontStyle.italic,
                        color: VoyoColors.ink),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Create a trip and CLEO will help you fill it with the best Egypt has to offer.',
                    style: GoogleFonts.instrumentSans(
                        fontSize: 14, color: VoyoColors.stone, height: 1.5),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 28),
                  SizedBox(
                    width: double.infinity,
                    height: 52,
                    child: FilledButton(
                      onPressed: _showCreateSheet,
                      style: FilledButton.styleFrom(
                        backgroundColor: VoyoColors.expedition,
                        shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(14)),
                      ),
                      child: Text('+ Create Trip',
                          style: GoogleFonts.instrumentSans(
                              fontSize: 15,
                              fontWeight: FontWeight.w600,
                              color: Colors.white)),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }

  // ── Planner timeline ──────────────────────────────────────────────────────

  Widget _buildPlanner(double top) {
    final trip = _itinerary!;
    final byDay = _byDay;
    final days = byDay.keys.toList()..sort();

    return CustomScrollView(
      slivers: [
        SliverToBoxAdapter(child: _buildHeader(top, trip)),
        SliverToBoxAdapter(child: _buildTripCard(trip)),
        if (days.isEmpty)
          SliverFillRemaining(
            child: Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Icon(Icons.add_location_alt_outlined,
                      size: 48, color: VoyoColors.smoke),
                  const SizedBox(height: 12),
                  Text('No stops added yet.',
                      style: GoogleFonts.fraunces(
                          fontSize: 20,
                          fontStyle: FontStyle.italic,
                          color: VoyoColors.stone)),
                  const SizedBox(height: 6),
                  Text('Tap + to add your first stop.',
                      style: GoogleFonts.instrumentSans(
                          fontSize: 13, color: VoyoColors.stone)),
                  const SizedBox(height: 20),
                  FilledButton.icon(
                    onPressed: () => _showAddStopSheet(dayHint: 1),
                    style: FilledButton.styleFrom(
                      backgroundColor: VoyoColors.terra,
                      shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12)),
                    ),
                    icon: const Icon(Icons.add, size: 18, color: Colors.white),
                    label: Text('Add First Stop',
                        style: GoogleFonts.instrumentSans(
                            fontSize: 14,
                            fontWeight: FontWeight.w600,
                            color: Colors.white)),
                  ),
                ],
              ),
            ),
          )
        else ...[
          for (final day in days) ...[
            SliverToBoxAdapter(child: _buildDayHeader(day, trip)),
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(20, 0, 20, 0),
                child: Column(
                  children: [
                    for (int i = 0; i < byDay[day]!.length; i++) ...[
                      _buildStopCard(byDay[day]![i]),
                      if (i < byDay[day]!.length - 1)
                        _buildTravelPill(),
                    ],
                  ],
                ),
              ),
            ),
          ],
          SliverToBoxAdapter(child: _buildAddDayButton()),
        ],
        const SliverToBoxAdapter(child: SizedBox(height: 32)),
      ],
    );
  }

  // ── Header ────────────────────────────────────────────────────────────────

  Widget _buildHeader(double top, Itinerary? trip) {
    return Container(
      color: VoyoColors.paper,
      padding: EdgeInsets.fromLTRB(20, top + 14, 16, 14),
      child: Column(
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  trip?.title ?? 'Planner',
                  style: GoogleFonts.fraunces(
                      fontSize: 26,
                      fontStyle: FontStyle.italic,
                      color: VoyoColors.ink),
                ),
              ),
              GestureDetector(
                onTap: _showTripsSheet,
                child: Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                  decoration: BoxDecoration(
                    color: VoyoColors.vellum,
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(color: VoyoColors.smoke),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.history,
                          size: 13, color: VoyoColors.stone),
                      const SizedBox(width: 4),
                      Text('Trips',
                          style: GoogleFonts.instrumentSans(
                              fontSize: 12,
                              fontWeight: FontWeight.w600,
                              color: VoyoColors.stone)),
                    ],
                  ),
                ),
              ),
              const SizedBox(width: 6),
              GestureDetector(
                onTap: _showCreateSheet,
                child: Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: const Color(0x1AD45028),
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(
                        color: VoyoColors.expedition.withValues(alpha: 0.3)),
                  ),
                  child: Text('+ New',
                      style: GoogleFonts.instrumentSans(
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                          color: VoyoColors.expedition)),
                ),
              ),
            ],
          ),
          if (trip != null) ...[
            const SizedBox(height: 2),
            Align(
              alignment: Alignment.centerLeft,
              child: Text(
                _tripSubtitle(trip),
                style: GoogleFonts.instrumentSans(
                    fontSize: 13, color: VoyoColors.stone),
              ),
            ),
          ],
          const SizedBox(height: 8),
          Container(height: 1, color: VoyoColors.smoke),
        ],
      ),
    );
  }

  // ── Trip summary card ─────────────────────────────────────────────────────

  Widget _buildTripCard(Itinerary trip) {
    final totalDays = (trip.startDate != null && trip.endDate != null)
        ? trip.endDate!.difference(trip.startDate!).inDays + 1
        : null;
    final totalStops = _items.length;
    final byDay = _byDay;
    final daysWithStops = byDay.keys.length;

    return Container(
      margin: const EdgeInsets.fromLTRB(16, 14, 16, 0),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: VoyoColors.paper,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: VoyoColors.smoke),
        boxShadow: [
          BoxShadow(
              color: Colors.black.withValues(alpha: 0.04),
              blurRadius: 8,
              offset: const Offset(0, 2)),
        ],
      ),
      child: Column(
        children: [
          Row(
            children: [
              _statCell(
                  totalDays?.toString() ?? '—', 'days', VoyoColors.terra),
              _statDivider(),
              _statCell(totalStops.toString(), 'stops', VoyoColors.sky),
              _statDivider(),
              _statCell(
                  daysWithStops.toString(), 'planned', VoyoColors.verified),
            ],
          ),
          if (totalStops > 0) ...[
            const SizedBox(height: 12),
            Container(height: 1, color: VoyoColors.smoke),
            const SizedBox(height: 12),
            SizedBox(
              width: double.infinity,
              height: 40,
              child: OutlinedButton.icon(
                onPressed: () => Navigator.push(
                  context,
                  MaterialPageRoute(builder: (_) => const MapScreen()),
                ),
                style: OutlinedButton.styleFrom(
                  side: const BorderSide(color: VoyoColors.sky),
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(10)),
                ),
                icon: const Icon(Icons.route_outlined,
                    size: 16, color: VoyoColors.sky),
                label: Text(
                  'View Route on Map',
                  style: GoogleFonts.instrumentSans(
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                    color: VoyoColors.sky,
                  ),
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _statCell(String value, String label, Color color) {
    return Expanded(
      child: Column(
        children: [
          Text(value,
              style: GoogleFonts.jetBrainsMono(
                  fontSize: 22, fontWeight: FontWeight.w700, color: color)),
          Text(label,
              style: GoogleFonts.instrumentSans(
                  fontSize: 11, color: VoyoColors.stone)),
        ],
      ),
    );
  }

  Widget _statDivider() => Container(
      width: 1, height: 32, color: VoyoColors.smoke);

  // ── Day header ────────────────────────────────────────────────────────────

  Widget _buildDayHeader(int day, Itinerary trip) {
    final date = trip.startDate?.add(Duration(days: day - 1));
    final months = ['Jan','Feb','Mar','Apr','May','Jun',
                    'Jul','Aug','Sep','Oct','Nov','Dec'];
    final dateStr = date != null
        ? '${months[date.month - 1]} ${date.day}'
        : '';
    final isToday = day == _currentDayNumber;

    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 20, 20, 10),
      child: Row(
        children: [
          Container(
            width: 32,
            height: 32,
            decoration: BoxDecoration(
              color: isToday ? VoyoColors.terra : VoyoColors.vellum,
              shape: BoxShape.circle,
              border: Border.all(
                  color: isToday ? VoyoColors.terra : VoyoColors.smoke),
            ),
            child: Center(
              child: Text('$day',
                  style: GoogleFonts.instrumentSans(
                      fontSize: 13,
                      fontWeight: FontWeight.w700,
                      color: isToday ? Colors.white : VoyoColors.stone)),
            ),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Day $day${isToday ? ' · Today' : ''}',
                    style: GoogleFonts.instrumentSans(
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                        color: isToday ? VoyoColors.terra : VoyoColors.ink)),
                if (dateStr.isNotEmpty)
                  Text(dateStr,
                      style: GoogleFonts.instrumentSans(
                          fontSize: 11, color: VoyoColors.stone)),
              ],
            ),
          ),
          // + Add stop for this day
          GestureDetector(
            onTap: () => _showAddStopSheet(dayHint: day),
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
              decoration: BoxDecoration(
                color: const Color(0x14C4622A),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: const Color(0x20C4622A)),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Icon(Icons.add, size: 13, color: VoyoColors.terra),
                  const SizedBox(width: 3),
                  Text('Add stop',
                      style: GoogleFonts.instrumentSans(
                          fontSize: 11,
                          fontWeight: FontWeight.w600,
                          color: VoyoColors.terra)),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  // ── Delete stop ───────────────────────────────────────────────────────────

  Future<void> _deleteStop(Map<String, dynamic> item) async {
    final itemId = item['id'] as int;
    // Optimistic remove
    setState(() => _items.removeWhere((i) => i['id'] == itemId));
    try {
      await _service.deleteItineraryItem(itemId);
    } catch (_) {
      // Rollback on failure
      _load();
    }
  }

  // ── Stop card ─────────────────────────────────────────────────────────────

  Widget _buildStopCard(Map<String, dynamic> item) {
    final poi = item['pois'] as Map<String, dynamic>?;
    final name = item['custom_title'] as String? ??
        poi?['name'] as String? ??
        'Stop';
    final category = poi?['category'] as String?;
    final timeStr = item['start_time'] as String? ?? '';
    final isCurrent = _isCurrent(item);
    final isVisited = _isVisited(item);

    return Dismissible(
      key: ValueKey(item['id']),
      direction: DismissDirection.endToStart,
      background: Container(
        alignment: Alignment.centerRight,
        padding: const EdgeInsets.only(right: 20),
        margin: const EdgeInsets.only(bottom: 4),
        decoration: BoxDecoration(
          color: const Color(0xFFD94040),
          borderRadius: BorderRadius.circular(14),
        ),
        child: const Icon(Icons.delete_outline,
            color: Colors.white, size: 22),
      ),
      confirmDismiss: (_) async {
        return await showDialog<bool>(
          context: context,
          builder: (_) => AlertDialog(
            backgroundColor: VoyoColors.paper,
            shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16)),
            title: Text('Remove stop?',
                style: GoogleFonts.fraunces(
                    fontSize: 18,
                    fontStyle: FontStyle.italic,
                    color: VoyoColors.ink)),
            content: Text(
              'This stop will be removed from your itinerary.',
              style: GoogleFonts.instrumentSans(
                  fontSize: 13, color: VoyoColors.stone),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context, false),
                child: Text('Cancel',
                    style: GoogleFonts.instrumentSans(
                        color: VoyoColors.stone,
                        fontWeight: FontWeight.w600)),
              ),
              TextButton(
                onPressed: () => Navigator.pop(context, true),
                child: Text('Remove',
                    style: GoogleFonts.instrumentSans(
                        color: const Color(0xFFD94040),
                        fontWeight: FontWeight.w600)),
              ),
            ],
          ),
        ) ?? false;
      },
      onDismissed: (_) => _deleteStop(item),
      child: IntrinsicHeight(
      child: Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Timeline spine + dot — uses IntrinsicHeight so spine matches card
        Column(
          children: [
            Container(width: 2, height: 14, color: VoyoColors.smoke),
            Container(
              width: 13,
              height: 13,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: isVisited
                    ? VoyoColors.verified
                    : isCurrent
                        ? VoyoColors.terra
                        : VoyoColors.smoke,
                border: isCurrent
                    ? Border.all(
                        color: VoyoColors.terra.withValues(alpha: 0.3),
                        width: 4)
                    : null,
              ),
            ),
            Expanded(
              child: Container(width: 2, color: VoyoColors.smoke),
            ),
          ],
        ),
        const SizedBox(width: 12),
        // Card
        Expanded(
          child: Container(
            margin: const EdgeInsets.only(bottom: 4),
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: VoyoColors.paper,
              borderRadius: BorderRadius.circular(14),
              border: Border.all(
                color: isCurrent
                    ? VoyoColors.terra.withValues(alpha: 0.4)
                    : VoyoColors.smoke,
                width: isCurrent ? 1.5 : 1,
              ),
              boxShadow: isCurrent
                  ? [
                      BoxShadow(
                          color: VoyoColors.terra.withValues(alpha: 0.08),
                          blurRadius: 8,
                          offset: const Offset(0, 2))
                    ]
                  : null,
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      if (timeStr.isNotEmpty)
                        Text(
                          _formatTime(timeStr),
                          style: GoogleFonts.jetBrainsMono(
                              fontSize: 11,
                              color: isCurrent
                                  ? VoyoColors.terra
                                  : VoyoColors.stone),
                        ),
                      const SizedBox(height: 2),
                      Text(
                        name,
                        style: GoogleFonts.fraunces(
                          fontSize: 16,
                          color: isVisited ? VoyoColors.stone : VoyoColors.ink,
                          decoration: isVisited
                              ? TextDecoration.lineThrough
                              : null,
                          decorationColor: VoyoColors.stone,
                        ),
                      ),
                      if (category != null) ...[
                        const SizedBox(height: 2),
                        Text(
                          _categoryLabel(category),
                          style: GoogleFonts.instrumentSans(
                              fontSize: 11, color: VoyoColors.stone),
                        ),
                      ],
                    ],
                  ),
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    if (isCurrent)
                      Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 8, vertical: 3),
                        decoration: BoxDecoration(
                          color: VoyoColors.terra,
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Text('NOW',
                            style: GoogleFonts.instrumentSans(
                                fontSize: 9,
                                fontWeight: FontWeight.w700,
                                color: Colors.white,
                                letterSpacing: 0.5)),
                      )
                    else if (isVisited)
                      const Icon(Icons.check_circle_outline,
                          size: 16, color: VoyoColors.verified),
                    const SizedBox(height: 6),
                    GestureDetector(
                      onTap: () async {
                        final confirmed = await showDialog<bool>(
                          context: context,
                          builder: (_) => AlertDialog(
                            backgroundColor: VoyoColors.paper,
                            shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(16)),
                            title: Text('Remove stop?',
                                style: GoogleFonts.fraunces(
                                    fontSize: 18,
                                    fontStyle: FontStyle.italic,
                                    color: VoyoColors.ink)),
                            content: Text(
                              'This stop will be removed from your itinerary.',
                              style: GoogleFonts.instrumentSans(
                                  fontSize: 13, color: VoyoColors.stone),
                            ),
                            actions: [
                              TextButton(
                                onPressed: () =>
                                    Navigator.pop(context, false),
                                child: Text('Cancel',
                                    style: GoogleFonts.instrumentSans(
                                        color: VoyoColors.stone,
                                        fontWeight: FontWeight.w600)),
                              ),
                              TextButton(
                                onPressed: () =>
                                    Navigator.pop(context, true),
                                child: Text('Remove',
                                    style: GoogleFonts.instrumentSans(
                                        color: const Color(0xFFD94040),
                                        fontWeight: FontWeight.w600)),
                              ),
                            ],
                          ),
                        );
                        if (confirmed == true) _deleteStop(item);
                      },
                      child: const Icon(Icons.delete_outline,
                          size: 17, color: VoyoColors.stone),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ],
    ))); // closes Dismissible > IntrinsicHeight > Row
  }

  // ── Travel pill ───────────────────────────────────────────────────────────

  Widget _buildTravelPill() {
    return Row(
      children: [
        // Spine continuation
        const SizedBox(width: 5, height: 28),
        const SizedBox(width: 20),
        Container(
          padding:
              const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
          decoration: BoxDecoration(
            color: const Color(0x14C4622A),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: const Color(0x1EC4622A)),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.directions_car_outlined,
                  size: 11, color: VoyoColors.terra),
              const SizedBox(width: 4),
              Text('In transit',
                  style: GoogleFonts.instrumentSans(
                      fontSize: 11,
                      color: VoyoColors.terra,
                      fontWeight: FontWeight.w500)),
            ],
          ),
        ),
      ],
    );
  }

  // ── Add day button ────────────────────────────────────────────────────────

  Widget _buildAddDayButton() {
    final nextDay = (_byDay.keys.isEmpty ? 0 : _byDay.keys.reduce((a, b) => a > b ? a : b)) + 1;
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 16, 20, 0),
      child: GestureDetector(
        onTap: () => _showAddStopSheet(dayHint: nextDay),
        child: Container(
          width: double.infinity,
          padding: const EdgeInsets.symmetric(vertical: 14),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(14),
            border: Border.all(
                color: VoyoColors.smoke, width: 2,
                style: BorderStyle.solid),
          ),
          child: Text('+ Add Day',
              textAlign: TextAlign.center,
              style: GoogleFonts.instrumentSans(
                  fontSize: 13, color: VoyoColors.stone)),
        ),
      ),
    );
  }

  // ── Error ─────────────────────────────────────────────────────────────────

  Widget _buildError() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.error_outline,
                size: 48, color: VoyoColors.expedition),
            const SizedBox(height: 12),
            Text('Something went wrong.',
                style: GoogleFonts.fraunces(
                    fontSize: 20,
                    fontStyle: FontStyle.italic,
                    color: VoyoColors.ink)),
            const SizedBox(height: 6),
            Text(_error ?? '',
                style: GoogleFonts.instrumentSans(
                    fontSize: 12, color: VoyoColors.stone),
                textAlign: TextAlign.center),
            const SizedBox(height: 20),
            TextButton(
              onPressed: _load,
              child: Text('Try again',
                  style: GoogleFonts.instrumentSans(
                      color: VoyoColors.expedition,
                      fontWeight: FontWeight.w600)),
            ),
          ],
        ),
      ),
    );
  }

  // ── Trips history sheet ───────────────────────────────────────────────────

  void _showTripsSheet() {
    final uid = _userId;
    if (uid == null) return;
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => _TripsHistorySheet(
        service: _service,
        userId: uid,
        currentItineraryId: _itinerary?.id,
        onChanged: _load,
        onSelected: (id) async {
          await _service.setActiveItinerary(userId: uid, itineraryId: id);
          _load();
        },
      ),
    );
  }

  // ── Add stop sheet ────────────────────────────────────────────────────────

  void _showAddStopSheet({int dayHint = 1}) {
    final itinerary = _itinerary;
    if (itinerary == null) return;
    final existingDays = _byDay.keys.toList()..sort();
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => _AddStopSheet(
        service: _service,
        itineraryId: itinerary.id,
        dayHint: dayHint,
        existingDays: existingDays,
        onAdded: _load, // reload the whole timeline
      ),
    );
  }

  // ── Create trip sheet ─────────────────────────────────────────────────────

  void _showCreateSheet() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => _CreateTripSheet(
        onCreated: (itinerary) {
          setState(() { _itinerary = itinerary; _items = []; });
        },
        service: _service,
        userId: _userId ?? '',
      ),
    );
  }

  // ── Helpers ───────────────────────────────────────────────────────────────

  String _tripSubtitle(Itinerary trip) {
    final months = ['Jan','Feb','Mar','Apr','May','Jun',
                    'Jul','Aug','Sep','Oct','Nov','Dec'];
    if (trip.startDate != null && trip.endDate != null) {
      final days = trip.endDate!.difference(trip.startDate!).inDays + 1;
      final start =
          '${months[trip.startDate!.month - 1]} ${trip.startDate!.day}';
      final end =
          '${months[trip.endDate!.month - 1]} ${trip.endDate!.day}';
      return '$start – $end · $days days';
    }
    return 'Active trip';
  }

  String _formatTime(String timeStr) {
    final parts = timeStr.split(':');
    if (parts.length < 2) return timeStr;
    final hour = int.tryParse(parts[0]) ?? 0;
    final min = parts[1];
    final period = hour >= 12 ? 'PM' : 'AM';
    final h = hour > 12 ? hour - 12 : (hour == 0 ? 12 : hour);
    return '$h:$min $period';
  }

  String _categoryLabel(String cat) => switch (cat) {
        'historical' => 'Historical Site',
        'religious' => 'Religious Site',
        'natural' => 'Nature',
        'cultural' => 'Cultural',
        'entertainment' => 'Entertainment',
        'dining' => 'Dining',
        'shopping' => 'Shopping',
        _ => cat[0].toUpperCase() + cat.substring(1),
      };
}

// ---------------------------------------------------------------------------
// Trips History Bottom Sheet
// ---------------------------------------------------------------------------

class _TripsHistorySheet extends StatefulWidget {
  final SupabaseService service;
  final String userId;
  final int? currentItineraryId;
  final VoidCallback onChanged;
  final void Function(int itineraryId)? onSelected;

  const _TripsHistorySheet({
    required this.service,
    required this.userId,
    required this.currentItineraryId,
    required this.onChanged,
    this.onSelected,
  });

  @override
  State<_TripsHistorySheet> createState() => _TripsHistorySheetState();
}

class _TripsHistorySheetState extends State<_TripsHistorySheet> {
  List<Map<String, dynamic>> _trips = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final trips = await widget.service.getAllItineraries(widget.userId);
    if (mounted) setState(() { _trips = trips; _loading = false; });
  }

  Future<void> _delete(Map<String, dynamic> trip) async {
    final id = trip['id'] as int;
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        backgroundColor: VoyoColors.paper,
        shape:
            RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: Text('Delete trip?',
            style: GoogleFonts.fraunces(
                fontSize: 18,
                fontStyle: FontStyle.italic,
                color: VoyoColors.ink)),
        content: Text(
          '"${trip['title']}" and all its stops will be permanently deleted.',
          style: GoogleFonts.instrumentSans(
              fontSize: 13, color: VoyoColors.stone),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: Text('Cancel',
                style: GoogleFonts.instrumentSans(
                    color: VoyoColors.stone,
                    fontWeight: FontWeight.w600)),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: Text('Delete',
                style: GoogleFonts.instrumentSans(
                    color: const Color(0xFFD94040),
                    fontWeight: FontWeight.w600)),
          ),
        ],
      ),
    );
    if (confirmed != true) return;

    setState(() => _trips.removeWhere((t) => t['id'] == id));
    await widget.service.deleteItinerary(id);

    // If we deleted the active trip, notify the planner to reload
    if (id == widget.currentItineraryId) widget.onChanged();
  }

  @override
  Widget build(BuildContext context) {
    final screenH = MediaQuery.of(context).size.height;
    return Container(
      height: screenH * 0.75,
      decoration: const BoxDecoration(
        color: VoyoColors.page,
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      child: Column(
        children: [
          Padding(
            padding: const EdgeInsets.only(top: 12, bottom: 4),
            child: Container(
              width: 36, height: 4,
              decoration: BoxDecoration(
                  color: VoyoColors.smoke,
                  borderRadius: BorderRadius.circular(2)),
            ),
          ),
          Padding(
            padding: const EdgeInsets.fromLTRB(20, 8, 16, 12),
            child: Row(
              children: [
                Text('My Trips',
                    style: GoogleFonts.fraunces(
                        fontSize: 22,
                        fontStyle: FontStyle.italic,
                        color: VoyoColors.ink)),
                const Spacer(),
                GestureDetector(
                  onTap: () => Navigator.pop(context),
                  child: const Icon(Icons.close,
                      size: 20, color: VoyoColors.stone),
                ),
              ],
            ),
          ),
          Divider(color: VoyoColors.smoke, height: 1),
          Expanded(
            child: _loading
                ? const Center(
                    child: CircularProgressIndicator(
                        color: VoyoColors.terra, strokeWidth: 2))
                : _trips.isEmpty
                    ? Center(
                        child: Text('No trips yet.',
                            style: GoogleFonts.instrumentSans(
                                fontSize: 13, color: VoyoColors.stone)))
                    : ListView.separated(
                        padding: const EdgeInsets.symmetric(vertical: 8),
                        itemCount: _trips.length,
                        separatorBuilder: (_, _) =>
                            Divider(color: VoyoColors.smoke, height: 1),
                        itemBuilder: (_, i) => _tripTile(_trips[i]),
                      ),
          ),
        ],
      ),
    );
  }

  Widget _tripTile(Map<String, dynamic> trip) {
    final id = trip['id'] as int;
    final title = trip['title'] as String? ?? 'Untitled';
    final status = trip['status'] as String? ?? 'draft';
    final isCurrent = id == widget.currentItineraryId;
    final stopCount = trip['stop_count'] as int;
    final startDate = trip['start_date'] != null
        ? DateTime.tryParse(trip['start_date'] as String)
        : null;
    final endDate = trip['end_date'] != null
        ? DateTime.tryParse(trip['end_date'] as String)
        : null;

    final months = ['Jan','Feb','Mar','Apr','May','Jun',
                    'Jul','Aug','Sep','Oct','Nov','Dec'];
    String dateStr = 'No dates set';
    if (startDate != null && endDate != null) {
      dateStr = '${months[startDate.month - 1]} ${startDate.day}'
          ' – ${months[endDate.month - 1]} ${endDate.day}, ${endDate.year}';
    } else if (startDate != null) {
      dateStr = 'From ${months[startDate.month - 1]} ${startDate.day}';
    }

    return ListTile(
      contentPadding:
          const EdgeInsets.symmetric(horizontal: 20, vertical: 6),
      onTap: isCurrent
          ? null
          : () {
              Navigator.pop(context);
              widget.onSelected?.call(id);
            },
      title: Row(
        children: [
          Expanded(
            child: Text(title,
                style: GoogleFonts.fraunces(
                    fontSize: 16, color: VoyoColors.ink),
                maxLines: 1,
                overflow: TextOverflow.ellipsis),
          ),
          if (isCurrent)
            Container(
              padding:
                  const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
              decoration: BoxDecoration(
                color: VoyoColors.terra.withValues(alpha: 0.12),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text('Active',
                  style: GoogleFonts.instrumentSans(
                      fontSize: 10,
                      fontWeight: FontWeight.w700,
                      color: VoyoColors.terra)),
            )
          else if (status == 'completed')
            Container(
              padding:
                  const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
              decoration: BoxDecoration(
                color: VoyoColors.verified.withValues(alpha: 0.12),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text('Done',
                  style: GoogleFonts.instrumentSans(
                      fontSize: 10,
                      fontWeight: FontWeight.w700,
                      color: VoyoColors.verified)),
            ),
        ],
      ),
      subtitle: Padding(
        padding: const EdgeInsets.only(top: 3),
        child: Row(
          children: [
            Text(dateStr,
                style: GoogleFonts.instrumentSans(
                    fontSize: 11, color: VoyoColors.stone)),
            const SizedBox(width: 10),
            Text('$stopCount stop${stopCount == 1 ? '' : 's'}',
                style: GoogleFonts.jetBrainsMono(
                    fontSize: 11, color: VoyoColors.stone)),
          ],
        ),
      ),
      trailing: GestureDetector(
        onTap: () => _delete(trip),
        child: Container(
          padding: const EdgeInsets.all(6),
          decoration: BoxDecoration(
            color: const Color(0x0FD94040),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: const Color(0x20D94040)),
          ),
          child: const Icon(Icons.delete_outline,
              size: 16, color: Color(0xFFD94040)),
        ),
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Add Stop Bottom Sheet
// ---------------------------------------------------------------------------

class _AddStopSheet extends StatefulWidget {
  final SupabaseService service;
  final int itineraryId;
  final int dayHint;
  final List<int> existingDays;
  final VoidCallback onAdded;

  const _AddStopSheet({
    required this.service,
    required this.itineraryId,
    required this.dayHint,
    required this.existingDays,
    required this.onAdded,
  });

  @override
  State<_AddStopSheet> createState() => _AddStopSheetState();
}

class _AddStopSheetState extends State<_AddStopSheet> {
  final _searchCtrl = TextEditingController();

  // Step 1: search
  List<dynamic> _results = []; // List<Poi>
  bool _searching = false;

  // Step 2: confirm
  dynamic _selectedPoi; // Poi or null
  late int _selectedDay;
  TimeOfDay _selectedTime = const TimeOfDay(hour: 9, minute: 0);
  bool _saving = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _selectedDay = widget.dayHint;
    // Defer search until after the first frame — calling setState from
    // initState during a pointer event triggers _debugDuringDeviceUpdate.
    WidgetsBinding.instance.addPostFrameCallback((_) => _search(''));
  }

  @override
  void dispose() {
    _searchCtrl.dispose();
    super.dispose();
  }

  Future<void> _search(String q) async {
    setState(() => _searching = true);
    try {
      final results = q.trim().isEmpty
          ? await widget.service.getFeaturedPois(limit: 15)
          : await widget.service.searchPois(q.trim());
      if (mounted) setState(() { _results = results; _searching = false; });
    } catch (_) {
      if (mounted) setState(() => _searching = false);
    }
  }

  Future<void> _pickTime() async {
    final picked = await showTimePicker(
      context: context,
      initialTime: _selectedTime,
      builder: (ctx, child) => Theme(
        data: Theme.of(ctx).copyWith(
          colorScheme: const ColorScheme.light(
            primary: VoyoColors.terra,
            onSurface: VoyoColors.ink,
          ),
        ),
        child: child!,
      ),
    );
    if (picked != null) setState(() => _selectedTime = picked);
  }

  Future<void> _save() async {
    if (_selectedPoi == null) return;
    setState(() { _saving = true; _error = null; });
    try {
      final h = _selectedTime.hour.toString().padLeft(2, '0');
      final m = _selectedTime.minute.toString().padLeft(2, '0');
      await widget.service.addItineraryItem(
        itineraryId: widget.itineraryId,
        poiId: _selectedPoi.id as int,
        dayNumber: _selectedDay,
        startTime: '$h:$m:00',
      );
      if (mounted) {
        Navigator.pop(context);
        widget.onAdded();
      }
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
          // Handle
          Padding(
            padding: const EdgeInsets.only(top: 12, bottom: 4),
            child: Container(
              width: 36, height: 4,
              decoration: BoxDecoration(
                  color: VoyoColors.smoke,
                  borderRadius: BorderRadius.circular(2)),
            ),
          ),
          // Header
          Padding(
            padding: const EdgeInsets.fromLTRB(20, 8, 16, 12),
            child: Row(
              children: [
                if (_selectedPoi != null)
                  GestureDetector(
                    onTap: () => setState(() => _selectedPoi = null),
                    child: const Padding(
                      padding: EdgeInsets.only(right: 10),
                      child: Icon(Icons.arrow_back,
                          size: 20, color: VoyoColors.stone),
                    ),
                  ),
                Text(
                  _selectedPoi == null ? 'Add a Stop' : 'Set Details',
                  style: GoogleFonts.fraunces(
                      fontSize: 22,
                      fontStyle: FontStyle.italic,
                      color: VoyoColors.ink),
                ),
                const Spacer(),
                GestureDetector(
                  onTap: () => Navigator.pop(context),
                  child: const Icon(Icons.close,
                      size: 20, color: VoyoColors.stone),
                ),
              ],
            ),
          ),
          Divider(color: VoyoColors.smoke, height: 1),
          // Body — each step has its own independent scroll
          Expanded(
            child: _selectedPoi == null
                ? _buildSearchStep()
                : _buildConfigStep(context),
          ),
        ],
      ),
    );
  }

  Widget _buildSearchStep() {
    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
          child: TextField(
            controller: _searchCtrl,
            onChanged: _search,
            style: GoogleFonts.instrumentSans(
                color: VoyoColors.ink, fontSize: 14),
            decoration: InputDecoration(
              hintText: 'Search places…',
              hintStyle: GoogleFonts.instrumentSans(
                  color: VoyoColors.stone, fontSize: 14),
              prefixIcon: const Icon(Icons.search,
                  color: VoyoColors.stone, size: 18),
              suffixIcon: _searchCtrl.text.isNotEmpty
                  ? GestureDetector(
                      onTap: () { _searchCtrl.clear(); _search(''); },
                      child: const Icon(Icons.close,
                          color: VoyoColors.stone, size: 16),
                    )
                  : null,
              filled: true,
              fillColor: VoyoColors.vellum,
              contentPadding:
                  const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(22),
                  borderSide: BorderSide.none),
              enabledBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(22),
                  borderSide: BorderSide.none),
              focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(22),
                  borderSide:
                      const BorderSide(color: VoyoColors.terra, width: 1.5)),
            ),
          ),
        ),
        Expanded(
          child: _searching
              ? const Center(
                  child: CircularProgressIndicator(
                      color: VoyoColors.terra, strokeWidth: 2))
              : _results.isEmpty
                  ? Center(
                      child: Text('No places found.',
                          style: GoogleFonts.instrumentSans(
                              fontSize: 13, color: VoyoColors.stone)))
                  : ListView.separated(
                      padding: const EdgeInsets.symmetric(vertical: 4),
                      itemCount: _results.length,
                      separatorBuilder: (_, _) =>
                          Divider(color: VoyoColors.smoke, height: 1),
                      itemBuilder: (_, i) {
                        final poi = _results[i];
                        final name = poi.name as String;
                        final cat = poi.category as String?;
                        return ListTile(
                          leading: Container(
                            width: 40, height: 40,
                            decoration: BoxDecoration(
                                borderRadius: BorderRadius.circular(10),
                                gradient: _gradient(cat)),
                          ),
                          title: Text(name,
                              style: GoogleFonts.fraunces(
                                  fontSize: 15, color: VoyoColors.ink)),
                          subtitle: Text(cat ?? '',
                              style: GoogleFonts.instrumentSans(
                                  fontSize: 11, color: VoyoColors.stone)),
                          trailing: const Icon(Icons.chevron_right,
                              color: VoyoColors.smoke),
                          onTap: () => setState(() => _selectedPoi = poi),
                        );
                      },
                    ),
        ),
      ],
    );
  }

  Widget _buildConfigStep(BuildContext context) {
    final poi = _selectedPoi;
    return SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(20, 16, 20, 32),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Selected POI card
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: VoyoColors.paper,
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: VoyoColors.smoke),
            ),
            child: Row(
              children: [
                Container(
                  width: 44, height: 44,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(10),
                    gradient: _gradient(poi.category as String?),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(poi.name as String,
                          style: GoogleFonts.fraunces(
                              fontSize: 16, color: VoyoColors.ink)),
                      Text(poi.category as String? ?? '',
                          style: GoogleFonts.instrumentSans(
                              fontSize: 11, color: VoyoColors.stone)),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),

          // Day selector
          Text('Which day?',
              style: GoogleFonts.instrumentSans(
                  fontSize: 13,
                  fontWeight: FontWeight.w600,
                  color: VoyoColors.ink)),
          const SizedBox(height: 10),
          Wrap(
            spacing: 8, runSpacing: 8,
            children: [
              ...widget.existingDays.map(_dayChip),
              _dayChip(
                (widget.existingDays.isEmpty
                        ? 0
                        : widget.existingDays.last) +
                    1,
                label: 'New Day',
              ),
            ],
          ),
          const SizedBox(height: 20),

          // Time picker
          Text('What time?',
              style: GoogleFonts.instrumentSans(
                  fontSize: 13,
                  fontWeight: FontWeight.w600,
                  color: VoyoColors.ink)),
          const SizedBox(height: 10),
          GestureDetector(
            onTap: _pickTime,
            child: Container(
              padding: const EdgeInsets.symmetric(
                  horizontal: 16, vertical: 14),
              decoration: BoxDecoration(
                color: VoyoColors.vellum,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: VoyoColors.smoke),
              ),
              child: Row(
                children: [
                  const Icon(Icons.access_time_outlined,
                      color: VoyoColors.stone, size: 18),
                  const SizedBox(width: 10),
                  Text(_selectedTime.format(context),
                      style: GoogleFonts.jetBrainsMono(
                          fontSize: 16,
                          color: VoyoColors.terra,
                          fontWeight: FontWeight.w600)),
                  const Spacer(),
                  Text('tap to change',
                      style: GoogleFonts.instrumentSans(
                          fontSize: 11, color: VoyoColors.stone)),
                ],
              ),
            ),
          ),

          if (_error != null) ...[
            const SizedBox(height: 12),
            Text(_error!,
                style: GoogleFonts.instrumentSans(
                    fontSize: 12, color: VoyoColors.expedition)),
          ],
          const SizedBox(height: 24),

          SizedBox(
            width: double.infinity,
            height: 52,
            child: FilledButton(
              onPressed: _saving ? null : _save,
              style: FilledButton.styleFrom(
                backgroundColor: VoyoColors.terra,
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14)),
              ),
              child: _saving
                  ? const SizedBox(
                      width: 20, height: 20,
                      child: CircularProgressIndicator(
                          strokeWidth: 2, color: Colors.white))
                  : Text('Add to Itinerary',
                      style: GoogleFonts.instrumentSans(
                          fontSize: 15,
                          fontWeight: FontWeight.w600,
                          color: Colors.white)),
            ),
          ),
        ],
      ),
    );
  }

  Widget _dayChip(int day, {String? label}) {
    final isSelected = _selectedDay == day;
    return GestureDetector(
      onTap: () => setState(() => _selectedDay = day),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 150),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        decoration: BoxDecoration(
          color: isSelected ? VoyoColors.terra : VoyoColors.paper,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
              color: isSelected ? VoyoColors.terra : VoyoColors.smoke),
        ),
        child: Text(
          label ?? 'Day $day',
          style: GoogleFonts.instrumentSans(
              fontSize: 13,
              fontWeight: FontWeight.w500,
              color: isSelected ? Colors.white : VoyoColors.stone),
        ),
      ),
    );
  }

  LinearGradient _gradient(String? category) => switch (category) {
        'historical' || 'religious' => const LinearGradient(
            colors: [Color(0xFF3D2B1F), Color(0xFFC4622A)]),
        'natural' => const LinearGradient(
            colors: [Color(0xFF1A3A2A), Color(0xFF2A7A50)]),
        'cultural' || 'entertainment' => const LinearGradient(
            colors: [Color(0xFF1A2C40), Color(0xFF1C72B4)]),
        _ => const LinearGradient(
            colors: [Color(0xFF2C1A2E), Color(0xFF6040B0)]),
      };
}

// ---------------------------------------------------------------------------
// Create Trip Bottom Sheet
// ---------------------------------------------------------------------------

class _CreateTripSheet extends StatefulWidget {
  final void Function(Itinerary) onCreated;
  final SupabaseService service;
  final String userId;

  const _CreateTripSheet({
    required this.onCreated,
    required this.service,
    required this.userId,
  });

  @override
  State<_CreateTripSheet> createState() => _CreateTripSheetState();
}

class _CreateTripSheetState extends State<_CreateTripSheet> {
  final _titleCtrl = TextEditingController();
  DateTime? _startDate;
  DateTime? _endDate;
  bool _saving = false;
  String? _error;

  @override
  void dispose() {
    _titleCtrl.dispose();
    super.dispose();
  }

  Future<void> _pickDate(bool isStart) async {
    final initial = isStart
        ? (_startDate ?? DateTime.now())
        : (_endDate ?? (_startDate ?? DateTime.now()).add(const Duration(days: 7)));
    final first = isStart ? DateTime.now() : (_startDate ?? DateTime.now());

    final picked = await showDatePicker(
      context: context,
      initialDate: initial,
      firstDate: first,
      lastDate: DateTime.now().add(const Duration(days: 365 * 2)),
      builder: (ctx, child) => Theme(
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
        _startDate = picked;
        if (_endDate != null && _endDate!.isBefore(picked)) {
          _endDate = null;
        }
      } else {
        _endDate = picked;
      }
    });
  }

  Future<void> _create() async {
    final title = _titleCtrl.text.trim();
    if (title.isEmpty) {
      setState(() => _error = 'Please enter a trip name.');
      return;
    }
    setState(() { _saving = true; _error = null; });
    try {
      final itinerary = await widget.service.createItinerary(
        userId: widget.userId,
        title: title,
        startDate: _startDate,
        endDate: _endDate,
      );
      if (itinerary != null && mounted) {
        Navigator.pop(context);
        widget.onCreated(itinerary);
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString().contains('foreign key')
              ? 'Account setup incomplete. Try signing out and back in.'
              : e.toString();
          _saving = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final months = ['Jan','Feb','Mar','Apr','May','Jun',
                    'Jul','Aug','Sep','Oct','Nov','Dec'];

    String fmtDate(DateTime? d) => d == null
        ? 'Pick date'
        : '${months[d.month - 1]} ${d.day}, ${d.year}';

    return Padding(
      padding: EdgeInsets.only(
          bottom: MediaQuery.of(context).viewInsets.bottom),
      child: Container(
        decoration: const BoxDecoration(
          color: VoyoColors.paper,
          borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
        ),
        padding: const EdgeInsets.fromLTRB(20, 16, 20, 32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Center(
              child: Container(
                width: 36, height: 4,
                decoration: BoxDecoration(
                    color: VoyoColors.smoke,
                    borderRadius: BorderRadius.circular(2)),
              ),
            ),
            const SizedBox(height: 16),
            Text('Create a Trip',
                style: GoogleFonts.fraunces(
                    fontSize: 22,
                    fontStyle: FontStyle.italic,
                    color: VoyoColors.ink)),
            const SizedBox(height: 16),
            TextField(
              controller: _titleCtrl,
              autofocus: true,
              textInputAction: TextInputAction.done,
              style: GoogleFonts.instrumentSans(color: VoyoColors.ink),
              decoration: const InputDecoration(
                labelText: 'Trip name',
                hintText: 'e.g. Egypt Adventure 2025',
                prefixIcon: Icon(Icons.luggage_outlined,
                    color: VoyoColors.stone),
              ),
            ),
            const SizedBox(height: 14),
            Row(
              children: [
                Expanded(
                  child: _DateTile(
                    label: 'Start',
                    value: fmtDate(_startDate),
                    onTap: () => _pickDate(true),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: _DateTile(
                    label: 'End',
                    value: fmtDate(_endDate),
                    onTap: () => _pickDate(false),
                  ),
                ),
              ],
            ),
            if (_error != null) ...[
              const SizedBox(height: 10),
              Text(_error!,
                  style: GoogleFonts.instrumentSans(
                      fontSize: 12, color: VoyoColors.expedition)),
            ],
            const SizedBox(height: 20),
            SizedBox(
              width: double.infinity,
              height: 52,
              child: FilledButton(
                onPressed: _saving ? null : _create,
                style: FilledButton.styleFrom(
                  backgroundColor: VoyoColors.expedition,
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(14)),
                ),
                child: _saving
                    ? const SizedBox(
                        width: 20, height: 20,
                        child: CircularProgressIndicator(
                            strokeWidth: 2, color: Colors.white))
                    : Text('Create Trip',
                        style: GoogleFonts.instrumentSans(
                            fontSize: 15,
                            fontWeight: FontWeight.w600,
                            color: Colors.white)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _DateTile extends StatelessWidget {
  final String label;
  final String value;
  final VoidCallback onTap;

  const _DateTile(
      {required this.label, required this.value, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
        decoration: BoxDecoration(
          color: VoyoColors.vellum,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: VoyoColors.smoke),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(label,
                style: GoogleFonts.instrumentSans(
                    fontSize: 10,
                    fontWeight: FontWeight.w500,
                    color: VoyoColors.stone)),
            const SizedBox(height: 2),
            Text(value,
                style: GoogleFonts.instrumentSans(
                    fontSize: 13,
                    color: value == 'Pick date'
                        ? VoyoColors.stone
                        : VoyoColors.ink,
                    fontWeight: FontWeight.w500)),
          ],
        ),
      ),
    );
  }
}
