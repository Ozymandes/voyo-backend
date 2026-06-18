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
import '../widgets/map_poi_preview_card.dart';
import '../widgets/poi_detail_sheet.dart';
import '../widgets/add_to_itinerary_sheet.dart';
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

/// Map zoom at/above which POI name labels appear beside markers.
const _kPoiLabelZoomThreshold = 12.0;

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
  // Canonical (enriched) Poi records for the itinerary stops above, keyed
  // by poi_id. Hydrated once when stops load so that tapping an itinerary
  // marker opens the SAME MapPoiPreviewCard (with real Supabase image /
  // description / price) as a regular map POI — instead of the prior
  // Wikipedia-lookup sheet that showed stale, inconsistent data.
  Map<int, Poi> _itineraryPoiDetails = {};
  Timer? _debounceTimer;
  bool _isLoading = false;
  // Non-fatal POI/network error surfaced as a dismissible banner so the user
  // sees the real problem (DNS fail, offline, Supabase down) instead of a
  // silent debugPrint + blank map.
  String? _poisError;

  // ── Routing state ───────────────────────────────────────────────────────────
  Map<int, List<LatLng>> _routesByDay = {};
  bool _routeLoading = false;
  bool _routeVisible = true;
  // Route-engine honesty (#5): true when at least one day's route could
  // not be fetched (Valhalla down, etc.). Drives the honest fallback banner
  // instead of silently drawing straight-line polylines through the markers.
  bool _routesUnavailable = false;

  // ── Isochrone ("Explore from here") ───────────────────────────────────────
  // Owned entirely by widgets/map_isochrone_overlay.dart. Slider / profile
  // controls live there too — not here.
  final _isochrone = IsochroneController();

  // ── Zoom-aware POI name labels ──────────────────────────────────────────────
  // When the map zooms in past [_kPoiLabelZoomThreshold], each POI's name is
  // shown as a small label beside its marker (Google-Maps-style). Toggled only
  // on threshold crossing to avoid rebuilds on every frame of a pan/zoom.
  bool _labelsVisible = false;

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
    // Toggle zoom-aware POI labels only on threshold crossing.
    final labelsVisible = camera.zoom >= _kPoiLabelZoomThreshold;
    if (labelsVisible != _labelsVisible) {
      setState(() => _labelsVisible = labelsVisible);
    }
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
      // Keep any POIs already loaded (don't blank the map on a transient
      // failure) but surface the error as a banner so the user knows.
      if (mounted) {
        setState(() {
          _isLoading = false;
          _poisError = e.toString();
        });
      }
    }
  }

  Future<void> _loadItineraryPois() async {
    final userId = Supabase.instance.client.auth.currentUser?.id;
    if (userId == null) return;
    final pois = await _supabaseService.getCurrentItineraryPois(userId);
    if (!mounted) return;
    setState(() => _itineraryPois = pois);
    // Hydrate the canonical enriched records for these stop POIs in the
    // background. This is what makes tapping a stop marker open the same
    // rich MapPoiPreviewCard (real image / description / price) as a
    // regular POI — fixing the 'stale stop card' bug. Non-blocking: if it
    // fails or returns partial data, the marker still opens the preview
    // with whatever canonical fields it has (Poi.fromJson is defensive).
    if (pois.isNotEmpty) {
      final ids = pois.map((p) => p.poiId).toSet();
      final details = await _supabaseService.getPoisByIds(ids);
      if (mounted) setState(() => _itineraryPoiDetails = details);
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
      // Detect the route-engine-unavailable case: there are multi-stop days
      // in the itinerary but the fetch returned fewer day-routes than days.
      // This is the signal that Valhalla is down — we must NOT render the
      // missing days as straight-line polylines (the prior silent fallback).
      final expectedDayCount =
          pois.map((p) => p.dayNumber).toSet().length;
      final missingDays = expectedDayCount - routes.length;
      setState(() {
        _routesByDay = routes;
        _routeLoading = false;
        _routesUnavailable = missingDays > 0;
      });
    }
  }

  // ── Isochrone ("Explore from here") ─────────────────────────────────────────
  // All state/logic/presentation live in widgets/map_isochrone_overlay.dart.
  // This helper just feeds the loaded POI coordinates in for the reach count.
  Future<void> _onMapLongPress(LatLng point) async {
    await _isochrone.explore(point, _pois, mapController: _mapController);
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
    // Geotag tap → compact preview card (canonical enriched POI, truncated
    // copy, two actions). The full `PoiDetailSheet` opens only when the user
    // taps 'View details'. Keeps the map interaction light while preserving
    // the same data source as Planner/Explore.
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder:
          (sheetCtx) => Padding(
            padding: EdgeInsets.only(
              bottom: MediaQuery.of(sheetCtx).viewInsets.bottom,
            ),
            child: MapPoiPreviewCard(
              poi: poi,
              onViewDetails: () {
                Navigator.pop(sheetCtx); // close preview
                _showPoiDetailSheet(poi);
              },
              onAddToTrip: () {
                Navigator.pop(sheetCtx); // close preview, then run add flow
                _addPoiToItinerary(poi);
              },
            ),
          ),
    );
  }

  /// Full enriched detail modal. Opened from the map preview's 'View details'
  /// action — identical sheet used across the app, so the detail view is the
  /// single canonical deep-dive.
  void _showPoiDetailSheet(Poi poi) {
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

  /// Opens the shared add-to-itinerary flow for a POI. Used by the isochrone
  /// top-5 ranked rows. Mirrors the pattern in explore_screen.dart.
  Future<void> _addPoiToItinerary(Poi poi) async {
    final userId = Supabase.instance.client.auth.currentUser?.id;
    if (userId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Sign in to save places to your trip.')),
      );
      return;
    }
    final added = await showModalBottomSheet<bool>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder:
          (_) => AddToItineraryFlow(
            poi: poi,
            service: _supabaseService,
            userId: userId,
          ),
    );
    if (added == true && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('${poi.name} added to your itinerary!'),
          backgroundColor: VoyoColors.terra,
          duration: const Duration(seconds: 2),
        ),
      );
    }
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
                // CartoDB Voyager tiles — the same VOYO-styled basemap the
                // Explore home uses. The bare OSM tile server is rate-limited
                // and frequently 403s from mobile clients; this subdomain-
                // load-balanced source is far more reliable.
                urlTemplate:
                    'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png',
                subdomains: const ['a', 'b', 'c', 'd'],
                userAgentPackageName: 'com.voyo.app',
                // Soft fallback: a failed tile (DNS/offline/403) logs a
                // debug message and renders a transparent tile instead of
                // throwing into the console as an uncaught exception.
                errorTileCallback: (tile, error, stackTrace) {
                  debugPrint('Map tile load failed: $error');
                },
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
              // Zoom-aware POI name labels — appear beside markers once the
              // map zooms in past the threshold (Google-Maps-style).
              if (_labelsVisible)
                MarkerLayer(
                  markers:
                      _pois
                          .map(
                            (poi) => Marker(
                              point: LatLng(poi.latitude, poi.longitude),
                              width: 112,
                              height: 24,
                              alignment: Alignment.centerLeft,
                              child: _PoiLabel(
                                text: poi.name,
                                onTap: () => _showPoiBottomSheet(poi),
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

          // Isochrone reachability panel: travel-mode chips + time-budget
          // slider + clear. Positioned directly under the Stack — a
          // ParentDataWidget can't live inside the widget's own
          // ListenableBuilder (causes "Incorrect use of ParentDataWidget").
          // Top-centred so it reads like Google Maps' travel-mode selector and
          // leaves the ranked-POI summary card clear at the bottom.
          Positioned(
            top: topPad + 12,
            left: 12,
            right: 72,
            child: Align(
              alignment: Alignment.topLeft,
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 320),
                child: IsochroneControls(
                  controller: _isochrone,
                  mapController: _mapController,
                ),
              ),
            ),
          ),

          // Non-modal reachable-area summary card: slides up over the map with
          // no scrim so the isochrone bloom stays visible beside the ranked
          // top-5 POI list. Positioned directly under the Stack.
          Positioned(
            left: 0,
            right: 0,
            bottom:
                MediaQuery.of(context).padding.bottom +
                (_days.length > 1 ? 56 : 12),
            child: IsochroneSummaryCard(
              controller: _isochrone,
              onPoiTap: _addPoiToItinerary,
            ),
          ),

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
          // ── Offline / error banner ────────────────────────────────────────────
          // When POIs fail to load (DNS down, offline, Supabase unreachable)
          // we surface a warm VOYO-styled banner with a retry, instead of
          // leaving the user staring at a blank map with raw console errors.
          if (_poisError != null && _pois.isEmpty)
            Positioned(
              top: topPad + 12,
              left: 16,
              right: 16,
              child: _OfflineBanner(
                message: _poisError!,
                onRetry: () {
                  setState(() => _poisError = null);
                  _loadPoisForBounds(_mapController.camera.visibleBounds);
                },
                onDismiss: () => setState(() => _poisError = null),
              ),
            ),

          // ── Route-engine unavailable banner (#5) ────────────────────────────
          // Honesty layer: when Valhalla is down, route lines for the
          // affected day(s) are omitted (we never draw a straight line as a
          // fake route). This banner surfaces the real status + offers the
          // Google Maps redirect as the trusted external fallback. Per the
          // spec: "Do not fake route intelligence."
          if (_routesUnavailable && _itineraryPois.isNotEmpty)
            Positioned(
              bottom: MediaQuery.of(context).padding.bottom + 72,
              left: 16,
              right: 16,
              child: _RouteUnavailableBanner(
                onOpenGoogleMaps: () =>
                    _routingService.openInGoogleMaps(_visiblePois),
                onRetry: () => _fetchRoutes(_itineraryPois),
              ),
            ),
        ],
      ),
    );
  }

  void _showStopInfo(ItineraryPoi poi) {
    // Resolve the canonical enriched record for this stop POI, then open
    // the SAME preview card a regular map POI uses — so itinerary stops
    // show identical data (real Supabase image / description / price) as
    // Explore / Planner / Details. Falls back to the dedicated stop sheet
    // only if the canonical record isn't hydrated yet (e.g. the background
    // fetch is still in flight or failed), so the marker is never dead.
    final canonical = _itineraryPoiDetails[poi.poiId];
    if (canonical != null) {
      _showPoiBottomSheet(canonical);
      return;
    }
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

/// Honest fallback banner shown when the route engine (Valhalla) is
/// unavailable. The map omits the affected day's route line entirely
/// rather than rendering a straight-line fake; this banner explains why
/// and offers the trusted Google Maps redirect as the external fallback.
class _RouteUnavailableBanner extends StatelessWidget {
  final VoidCallback onOpenGoogleMaps;
  final VoidCallback onRetry;

  const _RouteUnavailableBanner({
    required this.onOpenGoogleMaps,
    required this.onRetry,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: Container(
        padding: const EdgeInsets.fromLTRB(14, 10, 10, 10),
        decoration: BoxDecoration(
          color: VoyoColors.paper.withValues(alpha: 0.97),
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: VoyoColors.caution.withValues(alpha: 0.45)),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.1),
              blurRadius: 12,
              offset: const Offset(0, 3),
            ),
          ],
        ),
        child: Row(
          children: [
            Icon(Icons.route_outlined, size: 18, color: VoyoColors.caution),
            const SizedBox(width: 10),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    'Route engine unavailable',
                    style: GoogleFonts.instrumentSans(
                      fontSize: 12.5,
                      fontWeight: FontWeight.w700,
                      color: VoyoColors.ink,
                    ),
                  ),
                  const SizedBox(height: 1),
                  Text(
                    'Showing approximate connections — real routes need the Valhalla engine.',
                    style: GoogleFonts.instrumentSans(
                      fontSize: 10.5,
                      color: VoyoColors.stone,
                      height: 1.35,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(width: 8),
            // Primary: trusted external fallback.
            FilledButton.icon(
              onPressed: onOpenGoogleMaps,
              style: FilledButton.styleFrom(
                backgroundColor: VoyoColors.expedition,
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                minimumSize: const Size(0, 32),
                textStyle: GoogleFonts.instrumentSans(
                    fontSize: 11, fontWeight: FontWeight.w600),
              ),
              icon: const Icon(Icons.map_outlined, size: 14, color: Colors.white),
              label: const Text('Open in Maps',
                  style: TextStyle(color: Colors.white)),
            ),
            IconButton(
              onPressed: onRetry,
              icon: const Icon(Icons.refresh_rounded, size: 16),
              color: VoyoColors.stone,
              tooltip: 'Retry',
              visualDensity: VisualDensity.compact,
            ),
          ],
        ),
      ),
    );
  }
}

class _OfflineBanner extends StatelessWidget {
  final String message;
  final VoidCallback onRetry;
  final VoidCallback onDismiss;

  const _OfflineBanner({
    required this.message,
    required this.onRetry,
    required this.onDismiss,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      elevation: 6,
      borderRadius: BorderRadius.circular(14),
      color: VoyoColors.paper,
      child: Padding(
        padding: const EdgeInsets.fromLTRB(14, 12, 10, 12),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            const Icon(
              Icons.cloud_off_outlined,
              size: 22,
              color: VoyoColors.caution,
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    'Map offline',
                    style: GoogleFonts.fraunces(
                      fontSize: 15,
                      fontWeight: FontWeight.w600,
                      color: VoyoColors.ink,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    'We couldn\'t reach the map or places. Check your connection and retry.',
                    style: GoogleFonts.instrumentSans(
                      fontSize: 11,
                      color: VoyoColors.stone,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(width: 8),
            GestureDetector(
              onTap: onRetry,
              child: Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 12,
                  vertical: 7,
                ),
                decoration: BoxDecoration(
                  color: VoyoColors.expedition,
                  borderRadius: BorderRadius.circular(14),
                ),
                child: Text(
                  'Retry',
                  style: GoogleFonts.instrumentSans(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: Colors.white,
                  ),
                ),
              ),
            ),
            IconButton(
              icon: const Icon(Icons.close, size: 16, color: VoyoColors.stone),
              onPressed: onDismiss,
              padding: EdgeInsets.zero,
              constraints: const BoxConstraints(),
              visualDensity: VisualDensity.compact,
            ),
          ],
        ),
      ),
    );
  }
}

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

/// Small Google-Maps-style name label rendered beside a POI marker when the
/// map is zoomed in. Anchored via `Marker(alignment: Alignment.centerLeft)` so
/// its left edge sits at the POI coordinate; the internal left padding clears
/// the dot marker drawn by the layer below.
///
/// Transparent (no white pillbox) — legibility comes from a text stroke +
/// soft shadow, like Google Maps. Tappable: opens the same POI preview as the
/// marker dot. Color shifts to the VOYO accent on press for feedback. Does
/// NOT block the long-press isochrone gesture (no onLongPress defined → the
/// map's long-press recognizer wins the gesture arena).
class _PoiLabel extends StatefulWidget {
  final String text;
  final VoidCallback onTap;
  const _PoiLabel({required this.text, required this.onTap});

  @override
  State<_PoiLabel> createState() => _PoiLabelState();
}

class _PoiLabelState extends State<_PoiLabel> {
  bool _pressed = false;

  @override
  Widget build(BuildContext context) {
    // Transparent label: no fill, no border. Legibility on any basemap comes
    // from a white stroke (drawn by stacking two shadows) + a soft drop
    // shadow — the same trick Google Maps uses for its POI labels.
    final color = _pressed ? VoyoColors.expedition : VoyoColors.ink;
    return GestureDetector(
      onTap: widget.onTap,
      onTapDown: (_) => setState(() => _pressed = true),
      onTapUp: (_) => setState(() => _pressed = false),
      onTapCancel: () => setState(() => _pressed = false),
      // translucent so the label still receives taps inside its padded box,
      // but doesn't claim a long-press (no onLongPress → map wins isochrone).
      behavior: HitTestBehavior.translucent,
      child: Padding(
        // Clear the marker dot (radius ~11) plus a small gap.
        padding: const EdgeInsets.only(left: 15),
        child: Stack(
          children: [
            // Stroke layer: white text with an outline, drawn underneath for
            // legibility on any basemap (Google Maps uses the same trick).
            // Implemented via 4-direction white shadows rather than a Paint
            // cascade so the TextStyle composes cleanly.
            Text(
              widget.text,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: GoogleFonts.instrumentSans(
                fontSize: 11,
                fontWeight: FontWeight.w600,
                height: 1.2,
                color: Colors.white,
                shadows: const [
                  Shadow(color: Colors.white, offset: Offset(-0.8, -0.8)),
                  Shadow(color: Colors.white, offset: Offset(0.8, -0.8)),
                  Shadow(color: Colors.white, offset: Offset(-0.8, 0.8)),
                  Shadow(color: Colors.white, offset: Offset(0.8, 0.8)),
                  Shadow(
                    color: Colors.black26,
                    offset: Offset(0, 1),
                    blurRadius: 2,
                  ),
                ],
              ),
            ),
            // Fill layer: the label colour; pressed-state shifts to accent.
            Text(
              widget.text,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: GoogleFonts.instrumentSans(
                fontSize: 11,
                fontWeight: FontWeight.w600,
                height: 1.2,
                color: color,
              ),
            ),
          ],
        ),
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
