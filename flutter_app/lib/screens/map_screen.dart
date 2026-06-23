import 'dart:async';
import 'dart:convert';
import 'dart:math' show min, max;
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:http/http.dart' as http;
import 'package:latlong2/latlong.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../models/poi.dart';
import '../models/itinerary_poi.dart';
import '../services/supabase_service.dart';
import '../services/routing_service.dart';
import '../theme.dart';
import '../widgets/map_isochrone_overlay.dart';
import '../widgets/poi_detail_sheet.dart';
import 'chat_screen.dart';

// Day-slot colors (cycle for day 6+)
const _kDayColors = [
  Color(0xFF1C72B4), // sky   – day 1
  Color(0xFFC4622A), // terra – day 2
  Color(0xFF8860D4), // discovery – day 3
  Color(0xFF2A7A50), // green – day 4
  Color(0xFFD48A10), // amber – day 5
];

Color _dayColor(int dayNumber) =>
    _kDayColors[(dayNumber - 1) % _kDayColors.length];

class MapScreen extends StatefulWidget {
  const MapScreen({super.key});

  @override
  State<MapScreen> createState() => _MapScreenState();
}

class _MapScreenState extends State<MapScreen> {
  // ── Services ────────────────────────────────────────────────────────────────
  final _supabaseService = SupabaseService();
  final _routingService = RoutingService();
  final _mapController = MapController();

  // ── POI state ───────────────────────────────────────────────────────────────
  List<Poi> _pois = [];
  List<ItineraryPoi> _itineraryPois = [];
  Timer? _debounceTimer;
  bool _isLoading = false;

  // ── Routing state ───────────────────────────────────────────────────────────
  Map<int, List<LatLng>> _routesByDay = {};
  bool _routeLoading = false;
  bool _routeVisible = true;

  // ── Isochrone ("Explore from here") ───────────────────────────────────────
  // Owned entirely by widgets/map_isochrone_overlay.dart. Slider / profile
  // controls live there too — not here (avoids colliding with region work).
  final _isochrone = IsochroneController();

  // ── Day filter ──────────────────────────────────────────────────────────────
  int? _selectedDay; // null = show all days

  // ── Sorted itinerary POIs (day → sequence) ──────────────────────────────────
  List<ItineraryPoi> get _sortedPois => [..._itineraryPois]..sort((a, b) {
    final d = a.dayNumber.compareTo(b.dayNumber);
    return d != 0 ? d : a.sequenceOrder.compareTo(b.sequenceOrder);
  });

  Map<int, List<ItineraryPoi>> get _poisByDay {
    final map = <int, List<ItineraryPoi>>{};
    for (final p in _sortedPois) {
      map.putIfAbsent(p.dayNumber, () => []).add(p);
    }
    return map;
  }

  List<int> get _days => _poisByDay.keys.toList()..sort();

  // POIs and routes filtered to the selected day (or all if none selected)
  List<ItineraryPoi> get _visiblePois =>
      _selectedDay == null
          ? _sortedPois
          : _sortedPois.where((p) => p.dayNumber == _selectedDay).toList();

  Map<int, List<LatLng>> get _visibleRoutes =>
      _selectedDay == null
          ? _routesByDay
          : {
            if (_routesByDay.containsKey(_selectedDay))
              _selectedDay!: _routesByDay[_selectedDay]!,
          };

  // ── Lifecycle ───────────────────────────────────────────────────────────────

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadPoisForBounds(
        LatLngBounds(const LatLng(22.0, 24.0), const LatLng(32.0, 37.0)),
      );
      _loadItineraryPois();
    });
  }

  @override
  void dispose() {
    _debounceTimer?.cancel();
    _mapController.dispose();
    _isochrone.dispose();
    super.dispose();
  }

  // ── Data loading ─────────────────────────────────────────────────────────────

  void _onPositionChanged(MapCamera camera, bool hasGesture) {
    _debounceTimer?.cancel();
    _debounceTimer = Timer(const Duration(milliseconds: 500), () {
      _loadPoisForBounds(camera.visibleBounds);
    });
  }

  Future<void> _loadPoisForBounds(LatLngBounds bounds) async {
    if (_isLoading) return;
    setState(() => _isLoading = true);
    try {
      final pois = await _supabaseService.getPoisInView(
        minLat: bounds.southWest.latitude,
        maxLat: bounds.northEast.latitude,
        minLng: bounds.southWest.longitude,
        maxLng: bounds.northEast.longitude,
      );
      if (mounted) {
        setState(() {
          _pois = pois;
          _isLoading = false;
        });
      }
    } catch (e) {
      debugPrint('Error loading POIs: $e');
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _loadItineraryPois() async {
    final userId = Supabase.instance.client.auth.currentUser?.id;
    if (userId == null) return;
    final pois = await _supabaseService.getCurrentItineraryPois(userId);
    if (!mounted) return;
    setState(() => _itineraryPois = pois);
    if (pois.isNotEmpty) {
      // Defer until after the rebuild so the map controller is ready
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted) _fitRouteBounds(pois);
      });
      _fetchRoutes(pois);
    }
  }

  Future<void> _fetchRoutes(List<ItineraryPoi> pois) async {
    setState(() => _routeLoading = true);
    final routes = await _routingService.fetchRoutesByDay(pois);
    if (mounted) {
      setState(() {
        _routesByDay = routes;
        _routeLoading = false;
      });
    }
  }

  // ── Isochrone ("Explore from here") ─────────────────────────────────────────
  // All state/logic/presentation live in widgets/map_isochrone_overlay.dart.
  // This helper just feeds the loaded POI coordinates in for the reach count.
  Future<void> _onMapLongPress(LatLng point) async {
    await _isochrone.explore(
      point,
      [for (final p in _pois) LatLng(p.latitude, p.longitude)],
      mapController: _mapController,
      context: context,
    );
  }

  void _fitRouteBounds(List<ItineraryPoi> pois) {
    if (pois.isEmpty) return;
    final lats = pois.map((p) => p.latitude);
    final lngs = pois.map((p) => p.longitude);
    final bounds = LatLngBounds(
      LatLng(lats.reduce(min) - 0.04, lngs.reduce(min) - 0.04),
      LatLng(lats.reduce(max) + 0.04, lngs.reduce(max) + 0.04),
    );
    _mapController.fitCamera(
      CameraFit.bounds(bounds: bounds, padding: const EdgeInsets.all(48)),
    );
  }

  // ── Bottom sheets ────────────────────────────────────────────────────────────

  void _showPoiBottomSheet(Poi poi) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder:
          (_) => PoiDetailSheet(
            poi: poi,
            onAskCleo: () {
              Navigator.pop(context); // close the detail sheet first
              openCleoForPoi(context, poi);
            },
          ),
    );
  }

  void _showRoutePanel() {
    showModalBottomSheet(
      context: context,
      backgroundColor: VoyoColors.paper,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder:
          (_) => _RoutePanel(
            poisByDay: _poisByDay,
            selectedDay: _selectedDay,
            routeLoading: _routeLoading,
            onNavigate: (day) {
              Navigator.pop(context);
              final pois =
                  day == null
                      ? _itineraryPois
                      : _itineraryPois
                          .where((p) => p.dayNumber == day)
                          .toList();
              _routingService.openInGoogleMaps(pois);
            },
            onFitBounds: () {
              Navigator.pop(context);
              _fitRouteBounds(_visiblePois);
            },
          ),
    );
  }

  // ── Build ─────────────────────────────────────────────────────────────────────

  @override
  Widget build(BuildContext context) {
    final topPad = MediaQuery.of(context).padding.top;
    final hasRoute = _itineraryPois.isNotEmpty;

    return Scaffold(
      body: Stack(
        children: [
          // ── Map ──────────────────────────────────────────────────────────
          FlutterMap(
            mapController: _mapController,
            options: MapOptions(
              initialCenter: const LatLng(30.0444, 31.2357),
              initialZoom: 7.0,
              onPositionChanged: _onPositionChanged,
              onLongPress: (tapPosition, point) => _onMapLongPress(point),
            ),
            children: [
              TileLayer(
                urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                userAgentPackageName: 'com.voyo.app',
              ),
              // Isochrone reachable-area rings + center marker
              // (long-press the map to generate). Self-contained widgets:
              // logic + future sliders live in map_isochrone_overlay.dart.
              IsochronePolygons(controller: _isochrone),
              IsochroneCenterMarker(controller: _isochrone),
              if (_routeVisible && _visibleRoutes.isNotEmpty)
                PolylineLayer(
                  polylines: [
                    for (final e in _visibleRoutes.entries)
                      Polyline(
                        points: e.value,
                        color: Colors.white.withValues(alpha: 0.7),
                        strokeWidth: 6,
                      ),
                    for (final e in _visibleRoutes.entries)
                      Polyline(
                        points: e.value,
                        color: _dayColor(e.key),
                        strokeWidth: 3.5,
                      ),
                  ],
                ),
              MarkerLayer(
                markers:
                    _pois
                        .map(
                          (poi) => Marker(
                            point: LatLng(poi.latitude, poi.longitude),
                            width: 28,
                            height: 28,
                            child: GestureDetector(
                              onTap: () => _showPoiBottomSheet(poi),
                              child: Container(
                                width: 22,
                                height: 22,
                                decoration: BoxDecoration(
                                  color: VoyoColors.expedition,
                                  shape: BoxShape.circle,
                                  border: Border.all(
                                    color: Colors.white,
                                    width: 2.5,
                                  ),
                                  boxShadow: [
                                    BoxShadow(
                                      color: VoyoColors.expedition.withValues(
                                        alpha: 0.35,
                                      ),
                                      blurRadius: 6,
                                      offset: const Offset(0, 2),
                                    ),
                                  ],
                                ),
                                child: Center(
                                  child: Container(
                                    width: 5,
                                    height: 5,
                                    decoration: const BoxDecoration(
                                      color: Colors.white,
                                      shape: BoxShape.circle,
                                    ),
                                  ),
                                ),
                              ),
                            ),
                          ),
                        )
                        .toList(),
              ),
              if (_itineraryPois.isNotEmpty)
                MarkerLayer(
                  markers:
                      _visiblePois.map((poi) {
                        final c = _dayColor(poi.dayNumber);
                        return Marker(
                          point: LatLng(poi.latitude, poi.longitude),
                          width: 48,
                          height: 48,
                          child: GestureDetector(
                            onTap: () => _showStopInfo(poi),
                            child: Stack(
                              alignment: Alignment.center,
                              children: [
                                Container(
                                  width: 36,
                                  height: 36,
                                  decoration: BoxDecoration(
                                    shape: BoxShape.circle,
                                    color: c.withValues(alpha: 0.18),
                                  ),
                                ),
                                Container(
                                  width: 28,
                                  height: 28,
                                  decoration: BoxDecoration(
                                    color: c,
                                    shape: BoxShape.circle,
                                    border: Border.all(
                                      color: Colors.white,
                                      width: 2,
                                    ),
                                    boxShadow: [
                                      BoxShadow(
                                        color: c.withValues(alpha: 0.4),
                                        blurRadius: 8,
                                        offset: const Offset(0, 2),
                                      ),
                                    ],
                                  ),
                                  child: Center(
                                    child: Text(
                                      '${poi.sequenceOrder}',
                                      style: GoogleFonts.instrumentSans(
                                        fontSize: 11,
                                        fontWeight: FontWeight.w700,
                                        color: Colors.white,
                                        height: 1,
                                      ),
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        );
                      }).toList(),
                ),
            ],
          ),

          // ── Back button ───────────────────────────────────────────────────
          if (Navigator.of(context).canPop())
            Positioned(
              top: topPad + 12,
              left: 12,
              child: _MapIconButton(
                icon: Icons.arrow_back,
                onTap: () => Navigator.of(context).pop(),
              ),
            ),

          // ── Day filter chips (bottom of map) ─────────────────────────────
          if (_days.length > 1)
            Positioned(
              bottom: MediaQuery.of(context).padding.bottom + 16,
              left: 0,
              right: 0,
              child: SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                padding: const EdgeInsets.symmetric(horizontal: 16),
                child: Row(
                  children: [
                    _DayChip(
                      label: 'All',
                      color: VoyoColors.stone,
                      selected: _selectedDay == null,
                      onTap: () {
                        setState(() => _selectedDay = null);
                        WidgetsBinding.instance.addPostFrameCallback((_) {
                          if (mounted) _fitRouteBounds(_itineraryPois);
                        });
                      },
                    ),
                    const SizedBox(width: 8),
                    for (final day in _days) ...[
                      _DayChip(
                        label: 'Day $day',
                        color: _dayColor(day),
                        selected: _selectedDay == day,
                        onTap: () {
                          final dayPois =
                              _itineraryPois
                                  .where((p) => p.dayNumber == day)
                                  .toList();
                          setState(() => _selectedDay = day);
                          WidgetsBinding.instance.addPostFrameCallback((_) {
                            if (mounted) _fitRouteBounds(dayPois);
                          });
                        },
                      ),
                      const SizedBox(width: 8),
                    ],
                  ],
                ),
              ),
            ),

          // ── Top-right controls ────────────────────────────────────────────
          // ── "Explore from here" hint (empty state only) ───────────────────
          if (_isochrone.isEmpty && _itineraryPois.isEmpty)
            Positioned(
              bottom: MediaQuery.of(context).padding.bottom + 16,
              left: 0,
              right: 0,
              child: Center(
                child: IsochroneHintPill(
                  icon: Icons.touch_app_rounded,
                  text: "Long-press the map to explore what's reachable",
                ),
              ),
            ),

          // Isochrone clear button (+ future sliders). Self-positioning widget
          // owned by map_isochrone_overlay.dart.
          IsochroneControls(controller: _isochrone, topPad: topPad),

          Positioned(
            top: topPad + 12,
            right: 12,
            child: ListenableBuilder(
              listenable: _isochrone,
              builder: (ctx, _) {
                return Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    if (_isLoading || _routeLoading || _isochrone.isLoading)
                      _LoadingPill(
                        routeLoading: _routeLoading,
                        isochroneLoading: _isochrone.isLoading,
                      ),
                    if (hasRoute) ...[
                      const SizedBox(height: 8),
                      _MapIconButton(
                        icon:
                            _routeVisible
                                ? Icons.visibility
                                : Icons.visibility_off_outlined,
                        onTap:
                            () =>
                                setState(() => _routeVisible = !_routeVisible),
                        color:
                            _routeVisible ? VoyoColors.sky : VoyoColors.stone,
                      ),
                      const SizedBox(height: 8),
                      _MapIconButton(
                        icon: Icons.fit_screen,
                        onTap: () => _fitRouteBounds(_itineraryPois),
                      ),
                      const SizedBox(height: 8),
                      // Navigate button — opens Google Maps for the selected day (or all)
                      _MapIconButton(
                        icon: Icons.navigation_rounded,
                        color: VoyoColors.sky,
                        onTap:
                            () =>
                                _routingService.openInGoogleMaps(_visiblePois),
                      ),
                      const SizedBox(height: 8),
                      // Route details panel
                      _MapIconButton(
                        icon: Icons.list_alt_rounded,
                        onTap: _showRoutePanel,
                      ),
                    ],
                  ],
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  void _showStopInfo(ItineraryPoi poi) {
    showModalBottomSheet(
      context: context,
      backgroundColor: VoyoColors.paper,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (_) => _StopInfoSheet(poi: poi),
    );
  }
}

// ── Small shared widgets ────────────────────────────────────────────────────────

class _MapIconButton extends StatelessWidget {
  final IconData icon;
  final VoidCallback onTap;
  final Color color;

  const _MapIconButton({
    required this.icon,
    required this.onTap,
    this.color = VoyoColors.ink,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 40,
        height: 40,
        decoration: BoxDecoration(
          color: VoyoColors.paper,
          shape: BoxShape.circle,
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.1),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Icon(icon, color: color, size: 20),
      ),
    );
  }
}

class _LoadingPill extends StatelessWidget {
  final bool routeLoading;
  final bool isochroneLoading;
  const _LoadingPill({
    required this.routeLoading,
    this.isochroneLoading = false,
  });

  @override
  Widget build(BuildContext context) {
    final color =
        isochroneLoading
            ? VoyoColors.discovery
            : (routeLoading ? VoyoColors.sky : VoyoColors.expedition);
    final label =
        isochroneLoading
            ? 'Exploring reach…'
            : (routeLoading ? 'Building route…' : 'Loading places…');
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: VoyoColors.paper,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(color: Colors.black.withValues(alpha: 0.08), blurRadius: 8),
        ],
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          SizedBox(
            width: 12,
            height: 12,
            child: CircularProgressIndicator(strokeWidth: 2, color: color),
          ),
          const SizedBox(width: 6),
          Text(
            label,
            style: GoogleFonts.instrumentSans(
              fontSize: 12,
              color: VoyoColors.stone,
            ),
          ),
        ],
      ),
    );
  }
}

// ── Route panel bottom sheet ──────────────────────────────────────────────────

class _RoutePanel extends StatefulWidget {
  final Map<int, List<ItineraryPoi>> poisByDay;
  final int? selectedDay;
  final bool routeLoading;
  final void Function(int? day) onNavigate;
  final VoidCallback onFitBounds;

  const _RoutePanel({
    required this.poisByDay,
    required this.selectedDay,
    required this.routeLoading,
    required this.onNavigate,
    required this.onFitBounds,
  });

  @override
  State<_RoutePanel> createState() => _RoutePanelState();
}

class _RoutePanelState extends State<_RoutePanel> {
  late int? _activeDay;

  @override
  void initState() {
    super.initState();
    _activeDay = widget.selectedDay;
  }

  @override
  Widget build(BuildContext context) {
    final sortedDays = widget.poisByDay.keys.toList()..sort();
    final shownDays = _activeDay == null ? sortedDays : [_activeDay!];
    final shownStops = shownDays.fold(
      0,
      (s, d) => s + (widget.poisByDay[d]?.length ?? 0),
    );

    return DraggableScrollableSheet(
      initialChildSize: 0.6,
      minChildSize: 0.35,
      maxChildSize: 0.92,
      expand: false,
      builder: (_, scrollController) {
        return Column(
          children: [
            // ── Header ──────────────────────────────────────────────────────
            _PanelHeader(
              totalStops: shownStops,
              totalDays: shownDays.length,
              routeLoading: widget.routeLoading,
              onFitBounds: widget.onFitBounds,
            ),

            // ── Day selector chips ───────────────────────────────────────────
            if (sortedDays.length > 1)
              SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                padding: const EdgeInsets.fromLTRB(16, 10, 16, 6),
                child: Row(
                  children: [
                    _DayChip(
                      label: 'All days',
                      color: VoyoColors.stone,
                      selected: _activeDay == null,
                      onTap: () => setState(() => _activeDay = null),
                    ),
                    const SizedBox(width: 8),
                    for (final day in sortedDays) ...[
                      _DayChip(
                        label: 'Day $day',
                        color: _dayColor(day),
                        selected: _activeDay == day,
                        onTap: () => setState(() => _activeDay = day),
                      ),
                      const SizedBox(width: 8),
                    ],
                  ],
                ),
              ),
            Container(height: 1, color: VoyoColors.smoke),

            // ── Stop list ────────────────────────────────────────────────────
            Expanded(
              child: ListView(
                controller: scrollController,
                padding: const EdgeInsets.fromLTRB(20, 0, 20, 0),
                children: [
                  for (final day in shownDays) ...[
                    _DayHeader(
                      day: day,
                      stopCount: widget.poisByDay[day]!.length,
                    ),
                    for (final poi in widget.poisByDay[day]!)
                      _StopRow(poi: poi, dayColor: _dayColor(day)),
                    const SizedBox(height: 8),
                  ],
                  const SizedBox(height: 8),
                ],
              ),
            ),

            // ── Navigate CTA ─────────────────────────────────────────────────
            Padding(
              padding: EdgeInsets.fromLTRB(
                20,
                8,
                20,
                MediaQuery.of(context).padding.bottom + 16,
              ),
              child: SizedBox(
                width: double.infinity,
                height: 52,
                child: FilledButton.icon(
                  onPressed: () => widget.onNavigate(_activeDay),
                  style: FilledButton.styleFrom(
                    backgroundColor: VoyoColors.sky,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(14),
                    ),
                  ),
                  icon: const Icon(
                    Icons.open_in_new,
                    color: Colors.white,
                    size: 16,
                  ),
                  label: Text(
                    _activeDay == null
                        ? 'Navigate Full Trip'
                        : 'Navigate Day $_activeDay',
                    style: GoogleFonts.instrumentSans(
                      fontSize: 15,
                      fontWeight: FontWeight.w600,
                      color: Colors.white,
                    ),
                  ),
                ),
              ),
            ),
          ],
        );
      },
    );
  }
}

class _PanelHeader extends StatelessWidget {
  final int totalStops;
  final int totalDays;
  final bool routeLoading;
  final VoidCallback onFitBounds;

  const _PanelHeader({
    required this.totalStops,
    required this.totalDays,
    required this.routeLoading,
    required this.onFitBounds,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(20, 12, 16, 14),
      decoration: const BoxDecoration(
        color: VoyoColors.paper,
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Center(
            child: Container(
              width: 36,
              height: 4,
              decoration: BoxDecoration(
                color: VoyoColors.smoke,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),
          const SizedBox(height: 14),
          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Your Route',
                      style: GoogleFonts.fraunces(
                        fontSize: 22,
                        fontStyle: FontStyle.italic,
                        color: VoyoColors.ink,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      routeLoading
                          ? 'Calculating road route…'
                          : '$totalStops stop${totalStops == 1 ? '' : 's'}'
                              '  ·  $totalDays day${totalDays == 1 ? '' : 's'}',
                      style: GoogleFonts.instrumentSans(
                        fontSize: 13,
                        color: VoyoColors.stone,
                      ),
                    ),
                  ],
                ),
              ),
              GestureDetector(
                onTap: onFitBounds,
                child: Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: VoyoColors.vellum,
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: const Icon(
                    Icons.fit_screen,
                    size: 18,
                    color: VoyoColors.stone,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Container(height: 1, color: VoyoColors.smoke),
        ],
      ),
    );
  }
}

class _DayChip extends StatelessWidget {
  final String label;
  final Color color;
  final bool selected;
  final VoidCallback onTap;

  const _DayChip({
    required this.label,
    required this.color,
    required this.selected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 150),
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 7),
        decoration: BoxDecoration(
          color: selected ? color : VoyoColors.vellum,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: selected ? color : VoyoColors.smoke),
        ),
        child: Text(
          label,
          style: GoogleFonts.instrumentSans(
            fontSize: 12,
            fontWeight: FontWeight.w600,
            color: selected ? Colors.white : VoyoColors.stone,
          ),
        ),
      ),
    );
  }
}

class _DayHeader extends StatelessWidget {
  final int day;
  final int stopCount;
  const _DayHeader({required this.day, required this.stopCount});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(top: 16, bottom: 6),
      child: Row(
        children: [
          Container(
            width: 8,
            height: 8,
            decoration: BoxDecoration(
              color: _dayColor(day),
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 8),
          Text(
            'Day $day',
            style: GoogleFonts.instrumentSans(
              fontSize: 13,
              fontWeight: FontWeight.w700,
              color: VoyoColors.ink,
            ),
          ),
          const SizedBox(width: 6),
          Text(
            '($stopCount stop${stopCount == 1 ? '' : 's'})',
            style: GoogleFonts.instrumentSans(
              fontSize: 12,
              color: VoyoColors.stone,
            ),
          ),
        ],
      ),
    );
  }
}

class _StopRow extends StatelessWidget {
  final ItineraryPoi poi;
  final Color dayColor;
  const _StopRow({required this.poi, required this.dayColor});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          // Numbered circle
          Container(
            width: 26,
            height: 26,
            decoration: BoxDecoration(color: dayColor, shape: BoxShape.circle),
            child: Center(
              child: Text(
                '${poi.sequenceOrder}',
                style: GoogleFonts.instrumentSans(
                  fontSize: 11,
                  fontWeight: FontWeight.w700,
                  color: Colors.white,
                ),
              ),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  poi.name,
                  style: GoogleFonts.instrumentSans(
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                    color: VoyoColors.ink,
                  ),
                ),
                if (poi.category != null)
                  Text(
                    poi.category!,
                    style: GoogleFonts.instrumentSans(
                      fontSize: 11,
                      color: VoyoColors.stone,
                    ),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

// ── Wikipedia data + service ────────────────────────────────────────────────────

class _WikiData {
  final String? imageUrl;
  final String? extract;
  const _WikiData({this.imageUrl, this.extract});
}

class _MapWikiService {
  _MapWikiService._();
  static final instance = _MapWikiService._();

  final _cache = <String, _WikiData>{};
  final _inflight = <String, Future<_WikiData>>{};

  Future<_WikiData> fetch(String name) {
    if (_cache.containsKey(name)) return Future.value(_cache[name]!);
    return _inflight.putIfAbsent(name, () async {
      try {
        final encoded = Uri.encodeComponent(name);
        final uri = Uri.parse(
          'https://en.wikipedia.org/api/rest_v1/page/summary/$encoded',
        );
        final response = await http.get(
          uri,
          headers: {'Accept': 'application/json'},
        );
        if (response.statusCode == 200) {
          final body = jsonDecode(response.body) as Map<String, dynamic>;
          final thumb =
              (body['thumbnail'] as Map<String, dynamic>?)?['source']
                  as String?;
          final extract = body['extract'] as String?;
          final data = _WikiData(imageUrl: thumb, extract: extract);
          _cache[name] = data;
          _inflight.remove(name);
          return data;
        }
      } catch (_) {}
      const data = _WikiData();
      _cache[name] = data;
      _inflight.remove(name);
      return data;
    });
  }
}

// ── Stop info bottom sheet ──────────────────────────────────────────────────────

class _StopInfoSheet extends StatefulWidget {
  final ItineraryPoi poi;
  const _StopInfoSheet({required this.poi});

  @override
  State<_StopInfoSheet> createState() => _StopInfoSheetState();
}

class _StopInfoSheetState extends State<_StopInfoSheet> {
  _WikiData? _wiki;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _MapWikiService.instance.fetch(widget.poi.name).then((data) {
      if (mounted) {
        setState(() {
          _wiki = data;
          _loading = false;
        });
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final poi = widget.poi;
    final c = _dayColor(poi.dayNumber);
    final imageUrl = _wiki?.imageUrl;
    final extract = _wiki?.extract;

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        // ── Image header ─────────────────────────────────────────────────────
        ClipRRect(
          borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
          child: SizedBox(
            height: 160,
            width: double.infinity,
            child:
                _loading
                    ? Container(
                      color: VoyoColors.vellum,
                      child: const Center(
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: VoyoColors.stone,
                        ),
                      ),
                    )
                    : imageUrl != null
                    ? Stack(
                      fit: StackFit.expand,
                      children: [
                        Image.network(
                          imageUrl.replaceFirst(RegExp(r'/\d+px-'), '/1200px-'),
                          fit: BoxFit.cover,
                          filterQuality: FilterQuality.high,
                          errorBuilder:
                              (_, _, _) => Image.network(
                                imageUrl,
                                fit: BoxFit.cover,
                                filterQuality: FilterQuality.high,
                                errorBuilder:
                                    (_, _, _) => _colorFallback(poi.dayNumber),
                              ),
                        ),
                        Positioned.fill(
                          child: DecoratedBox(
                            decoration: BoxDecoration(
                              gradient: LinearGradient(
                                begin: Alignment.topCenter,
                                end: Alignment.bottomCenter,
                                colors: [
                                  Colors.transparent,
                                  VoyoColors.ink.withValues(alpha: 0.45),
                                ],
                              ),
                            ),
                          ),
                        ),
                      ],
                    )
                    : _colorFallback(poi.dayNumber),
          ),
        ),

        // ── Content ──────────────────────────────────────────────────────────
        Padding(
          padding: EdgeInsets.fromLTRB(
            20,
            16,
            20,
            MediaQuery.of(context).padding.bottom + 24,
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Day · Stop chip
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 10,
                  vertical: 4,
                ),
                decoration: BoxDecoration(
                  color: c.withValues(alpha: 0.12),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  'Day ${poi.dayNumber}  ·  Stop ${poi.sequenceOrder}',
                  style: GoogleFonts.instrumentSans(
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                    color: c,
                  ),
                ),
              ),
              const SizedBox(height: 10),
              // Name
              Text(
                poi.name,
                style: GoogleFonts.fraunces(
                  fontSize: 22,
                  fontStyle: FontStyle.italic,
                  color: VoyoColors.ink,
                ),
              ),
              if (poi.category != null) ...[
                const SizedBox(height: 4),
                Text(
                  poi.category!,
                  style: GoogleFonts.instrumentSans(
                    fontSize: 12,
                    color: VoyoColors.stone,
                  ),
                ),
              ],
              if (extract != null && extract.isNotEmpty) ...[
                const SizedBox(height: 12),
                Text(
                  extract.length > 300
                      ? '${extract.substring(0, 300)}…'
                      : extract,
                  style: GoogleFonts.instrumentSans(
                    fontSize: 13,
                    color: VoyoColors.ink.withValues(alpha: 0.75),
                    height: 1.55,
                  ),
                  maxLines: 4,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ],
          ),
        ),
      ],
    );
  }

  Widget _colorFallback(int dayNumber) {
    final c = _dayColor(dayNumber);
    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [c.withValues(alpha: 0.55), c],
        ),
      ),
    );
  }
}

