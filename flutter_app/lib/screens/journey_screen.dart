import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../models/itinerary.dart';
import '../services/supabase_service.dart';
import '../theme.dart';

class JourneyScreen extends StatefulWidget {
  const JourneyScreen({super.key});

  @override
  State<JourneyScreen> createState() => _JourneyScreenState();
}

class _JourneyScreenState extends State<JourneyScreen> {
  final _service = SupabaseService();
  final _supabase = Supabase.instance.client;

  List<Map<String, dynamic>> _trips = [];
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() { _loading = true; _error = null; });
    final uid = _supabase.auth.currentUser?.id;
    if (uid == null) { setState(() => _loading = false); return; }
    try {
      final trips = await _service.getPastItineraries(uid);
      if (mounted) setState(() { _trips = trips; _loading = false; });
    } catch (e) {
      if (mounted) setState(() { _error = e.toString(); _loading = false; });
    }
  }

  @override
  Widget build(BuildContext context) {
    final top = MediaQuery.of(context).padding.top;
    return Scaffold(
      backgroundColor: VoyoColors.page,
      body: _loading
          ? const Center(
              child: CircularProgressIndicator(
                  color: VoyoColors.ink, strokeWidth: 2))
          : _error != null
              ? _buildError()
              : CustomScrollView(
                  slivers: [
                    SliverToBoxAdapter(child: _buildHeader(top)),
                    if (_trips.isEmpty)
                      SliverFillRemaining(child: _buildEmpty())
                    else ...[
                      SliverToBoxAdapter(child: _buildStats()),
                      SliverList(
                        delegate: SliverChildBuilderDelegate(
                          (_, i) => _buildTripCard(_trips[i]),
                          childCount: _trips.length,
                        ),
                      ),
                    ],
                    const SliverToBoxAdapter(child: SizedBox(height: 32)),
                  ],
                ),
    );
  }

  // ── Header ────────────────────────────────────────────────────────────────

  Widget _buildHeader(double top) {
    return Container(
      color: VoyoColors.paper,
      padding: EdgeInsets.fromLTRB(20, top + 14, 20, 14),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Journey',
            style: GoogleFonts.fraunces(
                fontSize: 26,
                fontStyle: FontStyle.italic,
                color: VoyoColors.ink),
          ),
          const SizedBox(height: 2),
          Text(
            'Your trips through Egypt',
            style: GoogleFonts.instrumentSans(
                fontSize: 13, color: VoyoColors.stone),
          ),
          const SizedBox(height: 10),
          Container(height: 1, color: VoyoColors.smoke),
        ],
      ),
    );
  }

  // ── Aggregate stats bar ───────────────────────────────────────────────────

  Widget _buildStats() {
    final totalStops = _trips.fold<int>(
        0, (sum, t) => sum + (t['stop_count'] as int));
    final totalDays = _trips.fold<int>(0, (sum, t) {
      final start = t['start_date'] != null
          ? DateTime.tryParse(t['start_date'] as String)
          : null;
      final end = t['end_date'] != null
          ? DateTime.tryParse(t['end_date'] as String)
          : null;
      if (start != null && end != null) {
        return sum + end.difference(start).inDays + 1;
      }
      return sum;
    });

    return Container(
      margin: const EdgeInsets.fromLTRB(16, 16, 16, 4),
      padding: const EdgeInsets.symmetric(vertical: 14),
      decoration: BoxDecoration(
        color: VoyoColors.paper,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: VoyoColors.smoke),
      ),
      child: Row(
        children: [
          _stat(_trips.length.toString(), 'trips', VoyoColors.expedition),
          _statDivider(),
          _stat(totalDays.toString(), 'days', VoyoColors.terra),
          _statDivider(),
          _stat(totalStops.toString(), 'stops', VoyoColors.sky),
        ],
      ),
    );
  }

  Widget _stat(String value, String label, Color color) => Expanded(
        child: Column(
          children: [
            Text(value,
                style: GoogleFonts.jetBrainsMono(
                    fontSize: 20,
                    fontWeight: FontWeight.w700,
                    color: color)),
            Text(label,
                style: GoogleFonts.instrumentSans(
                    fontSize: 11, color: VoyoColors.stone)),
          ],
        ),
      );

  Widget _statDivider() =>
      Container(width: 1, height: 28, color: VoyoColors.smoke);

  // ── Trip card ─────────────────────────────────────────────────────────────

  Widget _buildTripCard(Map<String, dynamic> trip) {
    final title = trip['title'] as String? ?? 'Untitled Trip';
    final stopCount = trip['stop_count'] as int;
    final startDate = trip['start_date'] != null
        ? DateTime.tryParse(trip['start_date'] as String)
        : null;
    final endDate = trip['end_date'] != null
        ? DateTime.tryParse(trip['end_date'] as String)
        : null;
    final status = trip['status'] as String? ?? 'draft';

    int? days;
    if (startDate != null && endDate != null) {
      days = endDate.difference(startDate).inDays + 1;
    }

    return GestureDetector(
      onTap: () => _showTripDetail(trip),
      child: Container(
        margin: const EdgeInsets.fromLTRB(16, 10, 16, 0),
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
        child: Row(
          children: [
            // Colored left stripe
            Container(
              width: 5,
              height: 90,
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [Color(0xFFD45028), Color(0xFFB83818)],
                ),
                borderRadius: const BorderRadius.only(
                  topLeft: Radius.circular(16),
                  bottomLeft: Radius.circular(16),
                ),
              ),
            ),
            const SizedBox(width: 14),
            // Content
            Expanded(
              child: Padding(
                padding: const EdgeInsets.symmetric(vertical: 14),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            title,
                            style: GoogleFonts.fraunces(
                                fontSize: 17,
                                color: VoyoColors.ink),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        if (status == 'completed')
                          Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 8, vertical: 3),
                            decoration: BoxDecoration(
                              color: VoyoColors.verified
                                  .withValues(alpha: 0.12),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Text('Completed',
                                style: GoogleFonts.instrumentSans(
                                    fontSize: 10,
                                    fontWeight: FontWeight.w600,
                                    color: VoyoColors.verified)),
                          ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      _dateRange(startDate, endDate),
                      style: GoogleFonts.instrumentSans(
                          fontSize: 12, color: VoyoColors.stone),
                    ),
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        _miniStat(days?.toString() ?? '—', 'days'),
                        const SizedBox(width: 16),
                        _miniStat(stopCount.toString(), 'stops'),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.only(right: 12),
              child: const Icon(Icons.chevron_right,
                  color: VoyoColors.smoke, size: 20),
            ),
          ],
        ),
      ),
    );
  }

  Widget _miniStat(String value, String label) => Row(
        children: [
          Text(value,
              style: GoogleFonts.jetBrainsMono(
                  fontSize: 14,
                  fontWeight: FontWeight.w700,
                  color: VoyoColors.ink)),
          const SizedBox(width: 3),
          Text(label,
              style: GoogleFonts.instrumentSans(
                  fontSize: 11, color: VoyoColors.stone)),
        ],
      );

  // ── Empty state ───────────────────────────────────────────────────────────

  Widget _buildEmpty() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 40),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.terrain_outlined,
                size: 60, color: VoyoColors.smoke),
            const SizedBox(height: 20),
            Text(
              'No past trips yet.',
              style: GoogleFonts.fraunces(
                  fontSize: 24,
                  fontStyle: FontStyle.italic,
                  color: VoyoColors.ink),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 8),
            Text(
              'Once you complete a trip, it will appear here as a memory.',
              style: GoogleFonts.instrumentSans(
                  fontSize: 13, color: VoyoColors.stone, height: 1.5),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  // ── Error ─────────────────────────────────────────────────────────────────

  Widget _buildError() {
    return Center(
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
          const SizedBox(height: 16),
          TextButton(
            onPressed: _load,
            child: Text('Try again',
                style: GoogleFonts.instrumentSans(
                    color: VoyoColors.expedition,
                    fontWeight: FontWeight.w600)),
          ),
        ],
      ),
    );
  }

  // ── Trip detail sheet ─────────────────────────────────────────────────────

  void _showTripDetail(Map<String, dynamic> trip) {
    final itinerary = Itinerary(
      id: trip['id'] as int,
      userId: trip['user_id'] as String,
      title: trip['title'] as String? ?? 'Trip',
      status: trip['status'] as String? ?? 'draft',
      startDate: trip['start_date'] != null
          ? DateTime.tryParse(trip['start_date'] as String)
          : null,
      endDate: trip['end_date'] != null
          ? DateTime.tryParse(trip['end_date'] as String)
          : null,
    );
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => _TripDetailSheet(
          service: _service, itinerary: itinerary),
    );
  }

  // ── Helpers ───────────────────────────────────────────────────────────────

  String _dateRange(DateTime? start, DateTime? end) {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    if (start != null && end != null) {
      return '${months[start.month - 1]} ${start.day}, ${start.year}'
          ' – ${months[end.month - 1]} ${end.day}, ${end.year}';
    }
    if (start != null) {
      return '${months[start.month - 1]} ${start.day}, ${start.year}';
    }
    return 'No dates set';
  }
}

// ---------------------------------------------------------------------------
// Trip detail bottom sheet — read-only day-by-day timeline
// ---------------------------------------------------------------------------

class _TripDetailSheet extends StatefulWidget {
  final SupabaseService service;
  final Itinerary itinerary;

  const _TripDetailSheet(
      {required this.service, required this.itinerary});

  @override
  State<_TripDetailSheet> createState() => _TripDetailSheetState();
}

class _TripDetailSheetState extends State<_TripDetailSheet> {
  List<Map<String, dynamic>> _items = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final items =
        await widget.service.getItineraryItemsWithPois(widget.itinerary.id);
    if (mounted) setState(() { _items = items; _loading = false; });
  }

  Map<int, List<Map<String, dynamic>>> get _byDay {
    final map = <int, List<Map<String, dynamic>>>{};
    for (final item in _items) {
      final day = item['day_number'] as int;
      map.putIfAbsent(day, () => []).add(item);
    }
    return map;
  }

  @override
  Widget build(BuildContext context) {
    final screenH = MediaQuery.of(context).size.height;
    final trip = widget.itinerary;
    final byDay = _byDay;
    final days = byDay.keys.toList()..sort();

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
                Expanded(
                  child: Text(
                    trip.title,
                    style: GoogleFonts.fraunces(
                        fontSize: 22,
                        fontStyle: FontStyle.italic,
                        color: VoyoColors.ink),
                  ),
                ),
                GestureDetector(
                  onTap: () => Navigator.pop(context),
                  child: const Icon(Icons.close,
                      size: 20, color: VoyoColors.stone),
                ),
              ],
            ),
          ),
          if (trip.startDate != null || trip.endDate != null)
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 0, 20, 8),
              child: Align(
                alignment: Alignment.centerLeft,
                child: Text(
                  _dateRange(trip.startDate, trip.endDate),
                  style: GoogleFonts.instrumentSans(
                      fontSize: 12, color: VoyoColors.stone),
                ),
              ),
            ),
          Divider(color: VoyoColors.smoke, height: 1),
          // Body
          Expanded(
            child: _loading
                ? const Center(
                    child: CircularProgressIndicator(
                        color: VoyoColors.terra, strokeWidth: 2))
                : _items.isEmpty
                    ? Center(
                        child: Text('No stops in this trip.',
                            style: GoogleFonts.instrumentSans(
                                fontSize: 13, color: VoyoColors.stone)))
                    : ListView(
                        padding: const EdgeInsets.fromLTRB(20, 12, 20, 32),
                        children: [
                          for (final day in days) ...[
                            _buildDayHeader(day, trip),
                            ...byDay[day]!.map(_buildStopRow),
                            const SizedBox(height: 8),
                          ],
                        ],
                      ),
          ),
        ],
      ),
    );
  }

  Widget _buildDayHeader(int day, Itinerary trip) {
    final date = trip.startDate?.add(Duration(days: day - 1));
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    final dateStr = date != null
        ? '${months[date.month - 1]} ${date.day}'
        : '';

    return Padding(
      padding: const EdgeInsets.fromLTRB(0, 12, 0, 8),
      child: Row(
        children: [
          Container(
            width: 28, height: 28,
            decoration: BoxDecoration(
              color: VoyoColors.vellum,
              shape: BoxShape.circle,
              border: Border.all(color: VoyoColors.smoke),
            ),
            child: Center(
              child: Text('$day',
                  style: GoogleFonts.instrumentSans(
                      fontSize: 12,
                      fontWeight: FontWeight.w700,
                      color: VoyoColors.stone)),
            ),
          ),
          const SizedBox(width: 10),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Day $day',
                  style: GoogleFonts.instrumentSans(
                      fontSize: 13,
                      fontWeight: FontWeight.w600,
                      color: VoyoColors.ink)),
              if (dateStr.isNotEmpty)
                Text(dateStr,
                    style: GoogleFonts.instrumentSans(
                        fontSize: 11, color: VoyoColors.stone)),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStopRow(Map<String, dynamic> item) {
    final poi = item['pois'] as Map<String, dynamic>?;
    final name = item['custom_title'] as String? ??
        poi?['name'] as String? ?? 'Stop';
    final category = poi?['category'] as String?;
    final timeStr = item['start_time'] as String? ?? '';

    return Padding(
      padding: const EdgeInsets.only(bottom: 8, left: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Column(
            children: [
              Container(width: 2, height: 10, color: VoyoColors.smoke),
              Container(
                width: 10, height: 10,
                decoration: const BoxDecoration(
                    shape: BoxShape.circle, color: VoyoColors.smoke),
              ),
              Container(width: 2, height: 10, color: VoyoColors.smoke),
            ],
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: VoyoColors.paper,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: VoyoColors.smoke),
              ),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        if (timeStr.isNotEmpty)
                          Text(_formatTime(timeStr),
                              style: GoogleFonts.jetBrainsMono(
                                  fontSize: 10, color: VoyoColors.stone)),
                        Text(name,
                            style: GoogleFonts.fraunces(
                                fontSize: 15, color: VoyoColors.ink)),
                        if (category != null)
                          Text(_categoryLabel(category),
                              style: GoogleFonts.instrumentSans(
                                  fontSize: 11, color: VoyoColors.stone)),
                      ],
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 6, vertical: 3),
                    decoration: BoxDecoration(
                      color: _categoryColor(category)
                          .withValues(alpha: 0.12),
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: Icon(_categoryIcon(category),
                        size: 14, color: _categoryColor(category)),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  String _dateRange(DateTime? start, DateTime? end) {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    if (start != null && end != null) {
      return '${months[start.month - 1]} ${start.day}, ${start.year}'
          ' – ${months[end.month - 1]} ${end.day}, ${end.year}';
    }
    if (start != null) {
      return 'From ${months[start.month - 1]} ${start.day}, ${start.year}';
    }
    return '';
  }

  String _formatTime(String t) {
    final parts = t.split(':');
    if (parts.length < 2) return t;
    final h = int.tryParse(parts[0]) ?? 0;
    final m = parts[1];
    final period = h >= 12 ? 'PM' : 'AM';
    final disp = h > 12 ? h - 12 : (h == 0 ? 12 : h);
    return '$disp:$m $period';
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

  Color _categoryColor(String? cat) => switch (cat) {
        'historical' || 'religious' => VoyoColors.terra,
        'natural' => const Color(0xFF2A7A50),
        'cultural' || 'entertainment' => VoyoColors.sky,
        'dining' => const Color(0xFFE08C3A),
        _ => VoyoColors.stone,
      };

  IconData _categoryIcon(String? cat) => switch (cat) {
        'historical' => Icons.account_balance_outlined,
        'religious' => Icons.mosque_outlined,
        'natural' => Icons.park_outlined,
        'cultural' => Icons.theater_comedy_outlined,
        'entertainment' => Icons.local_activity_outlined,
        'dining' => Icons.restaurant_outlined,
        'shopping' => Icons.shopping_bag_outlined,
        _ => Icons.place_outlined,
      };
}
