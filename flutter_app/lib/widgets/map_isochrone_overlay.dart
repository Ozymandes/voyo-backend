// Isochrone ("Explore from here") overlay for the map screen.
//
// Self-contained: owns all reachable-area state, logic, and presentation so
// that slider / profile-selector work can happen here without touching
// `map_screen.dart` (which is owned by the region-outlines workstream).
//
// The map screen consumes four small pieces:
//   - [IsochroneController]           — state + `explore()` / `clear()`
//   - [IsochronePolygons]             — drop into `FlutterMap.children`
//   - [IsochroneCenterMarker]         — drop into `FlutterMap.children`
//   - [IsochroneControls]             — drop into the map `Stack` (clear
//                                       button + future sliders live here)
import 'dart:math';

import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:latlong2/latlong.dart';

import '../models/poi.dart';
import '../services/routing_service.dart';
import '../theme.dart';

/// A reachable POI ranked by travel time from the explored point.
class RankedPoi {
  final Poi poi;
  final double distanceKm;
  final double durationMin;

  /// `true` when the time/distance came from the offline haversine estimate
  /// rather than the road-following OSRM table.
  final bool estimated;

  const RankedPoi({
    required this.poi,
    required this.distanceKm,
    required this.durationMin,
    required this.estimated,
  });
}

/// Per-mode configuration for the reachability explorer (Tier 2).
/// Carries the slider stops, the default reach, and the one-line copy shown
/// in the summary card header. Capping walking at 30 min and starting
/// driving at 15 min is what makes the tool feel like travel planning
/// rather than a raw radius.
class IsochroneModeConfig {
  final String id; // 'auto' | 'pedestrian' | 'bicycle'
  final String label; // 'Driving' | 'Walking' | 'Cycling'
  final List<int> stops; // slider stops (minutes)
  final int defaultMinutes;
  final String shortBlurb;
  const IsochroneModeConfig({
    required this.id,
    required this.label,
    required this.stops,
    required this.defaultMinutes,
    required this.shortBlurb,
  });
}

/// Owns the "Explore from here" isochrone state + fetch/recompute logic.
///
/// Mutate [ranges] / [profile] from UI controls (sliders, profile selector),
/// then call [explore] (fresh point) or [reExplore] (re-run from the current
/// center with the new settings).
class IsochroneController extends ChangeNotifier {
  final RoutingService _routing = RoutingService();

  List<IsochroneRing> _rings = [];
  LatLng? _center;
  bool _loading = false;
  List<Poi> _lastPois = const [];
  int _reachableCount = 0;
  List<RankedPoi> _rankedPois = const [];
  bool _ranking = false;

  /// Reachable-area time ranges in minutes. Sliders write here.
  List<int> ranges = const [15, 30, 45];

  /// Travel profile: 'auto', 'pedestrian', or 'bicycle'.
  String profile = 'auto';

  List<IsochroneRing> get rings => _rings;
  LatLng? get center => _center;
  bool get isLoading => _loading;
  bool get hasData => _rings.isNotEmpty || _center != null || _loading;
  bool get isEmpty => !hasData;

  /// Summary-card data. The card renders when [hasSummary] is true.
  bool get hasSummary => _center != null && _rings.isNotEmpty;
  int get reachableCount => _reachableCount;
  List<RankedPoi> get rankedPois => _rankedPois;
  bool get isRanking => _ranking;
  int get maxMinutes => _rings.isEmpty ? 0 : _rings.last.timeMinutes;

  /// Fetch reachable-area rings from [point], fit them into view, and expose
  /// a reachable-POI summary (count + the 5 nearest by travel time) for the
  /// persistent summary card. [pois] are all currently-loaded POIs (used both
  /// for the point-in-polygon count and the ranked list).
  Future<void> explore(
    LatLng point,
    List<Poi> pois, {
    required MapController mapController,
    List<int>? ranges,
    String? profile,
    bool autoPickMode = true,
  }) => _explore(
    point,
    pois,
    mapController: mapController,
    ranges: ranges,
    profile: profile,
    autoPickMode: autoPickMode,
    isRefinement: false,
  );

  /// Core implementation. [isRefinement] distinguishes a fresh long-press
  /// (show loading, clear rings) from a slider/mode tweak. Refinements keep
  /// the existing rings visible and NEVER flip `_loading` — otherwise the
  /// synchronous `notifyListeners()` inside this method disables the
  /// Material `Slider` mid-drag on desktop, which is exactly the regression
  /// where the slider stopped being draggable on laptop builds.
  Future<void> _explore(
    LatLng point,
    List<Poi> pois, {
    required MapController mapController,
    List<int>? ranges,
    String? profile,
    bool autoPickMode = true,
    bool isRefinement = false,
  }) async {
    // On a fresh long-press, infer the most realistic mode + reach from how
    // nearby POIs are actually spread (no fabricated traffic). A press in
    // Islamic Cairo → walk 15 min; a press out near Saqqara → drive 45 min.
    // Manual mode/budget changes from the panel pass explicit values and
    // bypass this.
    String p = profile ?? this.profile;
    List<int> r = ranges ?? this.ranges;
    if (autoPickMode && profile == null && ranges == null) {
      p = suggestMode(point, pois);
      final cfg = modeConfig(p);
      r = _nestedRanges(cfg.defaultMinutes);
    }
    this.profile = p;
    this.ranges = r;
    final center = point;
    _center = center;
    _lastPois = pois;
    if (!isRefinement) {
      // Fresh long-press: loading spinner + clear the stale bloom.
      _loading = true;
      _rings = [];
      _reachableCount = 0;
      _rankedPois = const [];
      _ranking = false;
      notifyListeners();
    } else {
      // Refinement: invalidate the ranked list (it's about to change) but
      // leave `_rings` + `_loading` untouched so the slider stays draggable
      // and the previous bloom stays painted until the new one lands.
      _rankedPois = const [];
      _ranking = true;
      notifyListeners();
    }

    final fetched = await _routing.fetchIsochrone(
      center,
      ranges: r,
      profile: p,
    );
    _rings = fetched;
    if (!isRefinement) {
      _loading = false;
    }
    notifyListeners();

    if (fetched.isEmpty) {
      if (isRefinement) {
        _ranking = false;
        notifyListeners();
      }
      return;
    }
    if (!isRefinement) {
      _fitBounds(fetched, mapController);
    }

    final reachable = _reachablePois(_lastPois, fetched.last.points);
    _reachableCount = reachable.length;
    if (!isRefinement) {
      _ranking = true;
      notifyListeners();
    }

    _rankedPois = await _rankPois(center, reachable, p);
    _ranking = false;
    notifyListeners();
  }

  /// Re-run the last query from the current center with the current
  /// [ranges]/[profile]. Intended for slider / profile changes.
  Future<void> reExplore({required MapController mapController}) async {
    final c = _center;
    if (c == null) return;
    // Refinement path: keep the slider interactive + the old bloom painted
    // while the new query is in flight (see `_explore` for the rationale).
    await _explore(
      c,
      _lastPois,
      mapController: mapController,
      ranges: ranges,
      profile: profile,
      autoPickMode: false,
      isRefinement: true,
    );
  }

  void clear() {
    _rings = [];
    _center = null;
    _reachableCount = 0;
    _rankedPois = const [];
    _ranking = false;
    notifyListeners();
  }

  // ── Helpers ──────────────────────────────────────────────────────────────

  List<Poi> _reachablePois(List<Poi> pois, List<LatLng> polygon) {
    if (polygon.length < 3) return const [];
    return pois
        .where((p) => _pointInPolygon(LatLng(p.latitude, p.longitude), polygon))
        .toList();
  }

  /// Ranks reachable POIs by travel time and returns the closest 5.
  ///
  /// Prefers the road-following OSRM table endpoint; when that is
  /// unreachable (503 / offline) it falls back to a haversine distance plus
  /// a profile-aware speed estimate so the feature never breaks. Rows built
  /// from the fallback are flagged `estimated: true`.
  Future<List<RankedPoi>> _rankPois(
    LatLng origin,
    List<Poi> reachable,
    String profile,
  ) async {
    if (reachable.isEmpty) return const [];

    // Pre-filter to the nearest by straight-line distance so the OSRM table
    // request stays small + fast. The road-time top 5 sit well within these.
    final byHaversine = [...reachable]..sort(
      (a, b) => _haversineKm(
        origin,
        LatLng(a.latitude, a.longitude),
      ).compareTo(_haversineKm(origin, LatLng(b.latitude, b.longitude))),
    );
    final subset = byHaversine.take(60).toList();

    final dests = subset.map((p) => LatLng(p.latitude, p.longitude)).toList();
    final table = await _routing.fetchTable(
      origin: origin,
      destinations: dests,
      profile: profile,
    );

    final ranked = <RankedPoi>[];
    if (table != null && table.length == subset.length) {
      for (final row in table) {
        ranked.add(
          RankedPoi(
            poi: subset[row.index],
            distanceKm: row.distanceM / 1000.0,
            durationMin: row.durationS / 60.0,
            estimated: false,
          ),
        );
      }
    } else {
      final speedKmh = _profileSpeedKmh(profile);
      for (final poi in subset) {
        final dKm = _haversineKm(origin, LatLng(poi.latitude, poi.longitude));
        ranked.add(
          RankedPoi(
            poi: poi,
            distanceKm: dKm,
            durationMin: dKm / speedKmh * 60.0,
            estimated: true,
          ),
        );
      }
    }

    // Drop OSRM-unreachable cells (null -> 0.0) so they don't surface at
    // rank #1 as a misleading "0 km · 0 min".
    ranked.removeWhere((r) => r.distanceKm == 0 && r.durationMin == 0);

    ranked.sort((a, b) => a.durationMin.compareTo(b.durationMin));
    return ranked.take(5).toList();
  }

  /// Straight-line distance in kilometres between two points.
  static double _haversineKm(LatLng a, LatLng b) {
    const r = 6371.0;
    final dLat = (b.latitude - a.latitude) * pi / 180.0;
    final dLng = (b.longitude - a.longitude) * pi / 180.0;
    final lat1 = a.latitude * pi / 180.0;
    final lat2 = b.latitude * pi / 180.0;
    final s =
        sin(dLat / 2) * sin(dLat / 2) +
        cos(lat1) * cos(lat2) * sin(dLng / 2) * sin(dLng / 2);
    return r * 2 * atan2(sqrt(s), sqrt(1 - s));
  }

  /// Rough cruise speed (km/h) per profile, used only for the offline
  /// duration estimate.
  static double _profileSpeedKmh(String profile) {
    switch (profile) {
      case 'pedestrian':
        return 5.0;
      case 'bicycle':
        return 15.0;
      default: // 'auto'
        return 40.0;
    }
  }

  // ── Mode-aware config (Tier 2: realistic travel planning) ──────────────
  // Each mode has its own slider stops + sensible default. Walking is capped
  // at 30 min (no sane tourist walks 90 min); driving starts at 15 min (no
  // car icon for a 100 m hop); bike sits between. These prevent the
  // "accessibility-radius visualizer" feel the spec called out.
  static const Map<String, IsochroneModeConfig> modeConfigs = {
    'pedestrian': IsochroneModeConfig(
      id: 'pedestrian',
      label: 'Walking',
      stops: [5, 10, 15, 20, 30],
      defaultMinutes: 15,
      shortBlurb: 'Best for compact historic areas and nearby stops.',
    ),
    'bicycle': IsochroneModeConfig(
      id: 'bicycle',
      label: 'Cycling',
      stops: [10, 20, 30, 45, 60],
      defaultMinutes: 30,
      shortBlurb: 'Check local road comfort before relying on this route.',
    ),
    'auto': IsochroneModeConfig(
      id: 'auto',
      label: 'Driving',
      stops: [15, 30, 45, 60, 90, 120],
      defaultMinutes: 45,
      shortBlurb: 'Best for cross-city movement and wider day planning.',
    ),
  };

  static IsochroneModeConfig modeConfig(String profile) =>
      modeConfigs[profile] ?? modeConfigs['auto']!;

  /// Build 3 nested contour rings (inner / mid / outer) for a target max
  /// reach so the multicolour ramp always has bands to render. Snaps each
  /// to the mode's own stops so we never request a 23-min contour when the
  /// slider moves in 5-min increments.
  static List<int> _nestedRanges(int maxMinutes, {String? profile}) {
    final stops = modeConfig(profile ?? 'auto').stops;
    int snapTo(int v) {
      if (stops.contains(v)) return v;
      return stops.reduce((a, b) => ((b - v).abs() <= (a - v).abs()) ? b : a);
    }

    final inner = snapTo((maxMinutes / 3).round());
    final mid = snapTo((maxMinutes * 2 / 3).round());
    final outer = snapTo(maxMinutes);
    // Dedupe while preserving order (small reaches may collapse bands).
    final out = <int>[];
    for (final v in [inner, mid, outer]) {
      if (!out.contains(v)) out.add(v);
    }
    return out;
  }

  /// Pick the most realistic default mode for a freshly-explored point,
  /// based on how the nearby POIs are spread (straight-line). Compact
  /// historic districts → walk; spread-out / remote → drive. No fabricated
  /// data — pure haversine on the POIs already loaded in view.
  static String suggestMode(LatLng point, List<Poi> nearby) {
    if (nearby.isEmpty) return 'auto';
    final dists =
        nearby
            .map((p) => _haversineKm(point, LatLng(p.latitude, p.longitude)))
            .where((d) => d > 0.05) // ignore on-top-of-marker noise
            .toList()
          ..sort();
    if (dists.isEmpty) return 'pedestrian';
    // Median distance to the nearest 6 POIs decides the cluster scale.
    final nearest = dists.take(6).toList();
    final med = nearest[nearest.length ~/ 2];
    // NOTE: cycling is disabled for the Egypt prototype (#3) — Cairo/Giza
    // tourist cycling is impractical (traffic, road quality, heat). The
    // suggester therefore jumps straight from walkable → driveable.
    if (med <= 1.5) return 'pedestrian'; // compact / walkable
    return 'auto'; // wide / cross-city / remote → drive
  }

  static bool _pointInPolygon(LatLng p, List<LatLng> poly) {
    var inside = false;
    for (var i = 0, j = poly.length - 1; i < poly.length; j = i++) {
      final yi = poly[i].latitude, xi = poly[i].longitude;
      final yj = poly[j].latitude, xj = poly[j].longitude;
      final intersect =
          ((yi > p.latitude) != (yj > p.latitude)) &&
          (p.longitude <
              (xj - xi) *
                      (p.latitude - yi) /
                      ((yj - yi).abs() < 1e-12 ? 1e-12 : yj - yi) +
                  xi);
      if (intersect) inside = !inside;
    }
    return inside;
  }

  void _fitBounds(List<IsochroneRing> rings, MapController mapController) {
    final all = rings.expand((r) => r.points).toList();
    if (all.isEmpty) return;
    final lats = all.map((p) => p.latitude);
    final lngs = all.map((p) => p.longitude);
    final bounds = LatLngBounds(
      LatLng(lats.reduce(min) - 0.01, lngs.reduce(min) - 0.01),
      LatLng(lats.reduce(max) + 0.01, lngs.reduce(max) + 0.01),
    );
    mapController.fitCamera(
      CameraFit.bounds(bounds: bounds, padding: const EdgeInsets.all(56)),
    );
  }
}

/// Reachable-area rings rendered as a `PolygonLayer`. Drop into
/// `FlutterMap.children`. Outer rings render first so inner rings sit on top.
///
/// Multicolored by time band (Tier 2 isochrone upgrade): inner = strong
/// accent, fading to lighter/paler as travel time grows — the standard
/// reachability-ramp look (traveltime / Mapbox Isochrone). Gives instant
/// visual gradient of "how far can I get".
class IsochronePolygons extends StatelessWidget {
  final IsochroneController controller;
  const IsochronePolygons({super.key, required this.controller});

  @override
  Widget build(BuildContext context) {
    return ListenableBuilder(
      listenable: controller,
      builder: (ctx, _) {
        final rings = [...controller.rings]
          ..sort((a, b) => b.timeMinutes.compareTo(a.timeMinutes));
        return PolygonLayer(
          polygons: [
            for (final ring in rings)
              Polygon(
                points: ring.points,
                // Color ramp by time band (outer = paler). The ramp is fixed
                // across known bands so the user learns the colour code.
                color: isochroneFill(ring.timeMinutes),
                borderColor: isochroneBorder(ring.timeMinutes),
                borderStrokeWidth: 1.5,
              ),
          ],
        );
      },
    );
  }
}

/// Fill colour for an isochrone ring of [minutes] travel time.
/// Inner bands are warmer/stronger, outer bands paler — the standard
/// reachability ramp. Bands chosen to match the slider presets.
Color isochroneFill(int minutes) {
  switch (minutes) {
    case <= 15:
      return const Color(0xFFE8B431).withValues(alpha: 0.32); // amber
    case <= 30:
      return const Color(0xFF3FA9A4).withValues(alpha: 0.26); // teal
    case <= 45:
      return const Color(0xFF4A78C9).withValues(alpha: 0.22); // blue
    case <= 60:
      return const Color(0xFF7C5BC9).withValues(alpha: 0.18); // violet
    case <= 90:
      return const Color(0xFF9B4FA8).withValues(alpha: 0.15); // magenta
    default:
      return const Color(0xFF6B7280).withValues(alpha: 0.12); // grey (far)
  }
}

/// Border colour for an isochrone ring — same ramp, higher alpha so edges
/// read clearly on any basemap.
Color isochroneBorder(int minutes) {
  switch (minutes) {
    case <= 15:
      return const Color(0xFFE8B431).withValues(alpha: 0.75);
    case <= 30:
      return const Color(0xFF3FA9A4).withValues(alpha: 0.7);
    case <= 45:
      return const Color(0xFF4A78C9).withValues(alpha: 0.65);
    case <= 60:
      return const Color(0xFF7C5BC9).withValues(alpha: 0.6);
    case <= 90:
      return const Color(0xFF9B4FA8).withValues(alpha: 0.55);
    default:
      return const Color(0xFF6B7280).withValues(alpha: 0.5);
  }
}

/// Center marker for the explored point. Drop into `FlutterMap.children`.
class IsochroneCenterMarker extends StatelessWidget {
  final IsochroneController controller;
  const IsochroneCenterMarker({super.key, required this.controller});

  @override
  Widget build(BuildContext context) {
    return ListenableBuilder(
      listenable: controller,
      builder: (ctx, _) {
        final center = controller.center;
        return MarkerLayer(
          markers: [
            if (center != null)
              Marker(
                point: center,
                width: 40,
                height: 40,
                child: const Icon(
                  Icons.radio_button_checked_rounded,
                  color: VoyoColors.discovery,
                  size: 28,
                ),
              ),
          ],
        );
      },
    );
  }
}

/// Right-side control cluster for the isochrone: the clear button today, and
/// the natural home for time-range sliders / profile selectors moving forward.
class IsochroneControls extends StatelessWidget {
  final IsochroneController controller;

  /// Map controller passed through to [IsochroneController.reExplore] when
  /// the user flips travel mode or slides the time budget — the new rings
  /// re-fit into view.
  final MapController mapController;

  const IsochroneControls({
    super.key,
    required this.controller,
    required this.mapController,
  });

  @override
  Widget build(BuildContext context) {
    return ListenableBuilder(
      listenable: controller,
      builder: (ctx, _) {
        // NOTE: do NOT wrap this in Positioned here. A ParentDataWidget like
        // Positioned must be a DIRECT child of the Stack that owns it;
        // nesting it under ListenableBuilder throws "Incorrect use of
        // ParentDataWidget" on every rebuild. The caller positions us.
        if (!controller.hasData) return const SizedBox.shrink();
        return _ControlPanel(
          controller: controller,
          mapController: mapController,
        );
      },
    );
  }
}

/// Compact reachability panel: travel-mode chips + time-budget slider + clear.
/// Shown only while an isochrone is active. Mode/budget changes trigger a real
/// re-query via Valhalla (no fabricated traffic — each mode uses its true
/// road-network costing, and the budget sets the outer contour).
class _ControlPanel extends StatelessWidget {
  final IsochroneController controller;
  final MapController mapController;
  const _ControlPanel({required this.controller, required this.mapController});

  // Modes offered in the control panel. Cycling is intentionally absent
  // for the Egypt prototype (#3): tourist cycling in Cairo/Giza is
  // impractical (traffic, road quality, heat). Keeping Walk + Drive only
  // means the suggester and UI never offer a mode we can't stand behind.
  // If a bike-friendly area is later marked explicitly, add 'bicycle' here.
  static const _modeOrder = ['pedestrian', 'auto'];

  @override
  Widget build(BuildContext context) {
    final cfg = IsochroneController.modeConfig(controller.profile);
    final stops = cfg.stops;
    // Current outer reach, snapped to a stop for the slider thumb.
    final currentMax =
        controller.ranges.isEmpty
            ? cfg.defaultMinutes
            : controller.ranges.reduce((a, b) => a > b ? a : b);
    final activeStop =
        stops.contains(currentMax)
            ? currentMax
            : stops.reduce(
              (a, b) =>
                  ((b - currentMax).abs() <= (a - currentMax).abs()) ? b : a,
            );

    return Container(
      padding: const EdgeInsets.fromLTRB(10, 8, 10, 10),
      decoration: BoxDecoration(
        color: VoyoColors.paper.withValues(alpha: 0.97),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: VoyoColors.smoke, width: 0.5),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.12),
            blurRadius: 16,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Header row: title + clear button.
          Row(
            children: [
              Icon(
                Icons.explore_rounded,
                size: 15,
                color: VoyoColors.discovery,
              ),
              const SizedBox(width: 6),
              Text(
                'Reachable area',
                style: GoogleFonts.fraunces(
                  fontSize: 13,
                  fontWeight: FontWeight.w600,
                  color: VoyoColors.ink,
                ),
              ),
              const Spacer(),
              GestureDetector(
                onTap: controller.clear,
                child: Padding(
                  padding: const EdgeInsets.all(2),
                  child: Icon(
                    Icons.close_rounded,
                    size: 18,
                    color: VoyoColors.stone,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          // Travel-mode chips. Order: Walk · Bike · Drive (most-local first).
          Row(
            children: [
              for (var i = 0; i < _modeOrder.length; i++) ...[
                Expanded(
                  child: _ModeChip(
                    icon: _modeIcon(_modeOrder[i]),
                    label: IsochroneController.modeConfig(_modeOrder[i]).label,
                    selected: controller.profile == _modeOrder[i],
                    onTap: () => _onModeChange(_modeOrder[i]),
                  ),
                ),
                if (i < _modeOrder.length - 1) const SizedBox(width: 6),
              ],
            ],
          ),
          const SizedBox(height: 10),
          // Time-budget slider row.
          Row(
            children: [
              Icon(Icons.schedule_rounded, size: 14, color: VoyoColors.stone),
              const SizedBox(width: 6),
              Text(
                'Reach',
                style: GoogleFonts.instrumentSans(
                  fontSize: 11,
                  fontWeight: FontWeight.w600,
                  color: VoyoColors.stone,
                ),
              ),
            ],
          ),
          SliderTheme(
            data: SliderTheme.of(context).copyWith(
              trackHeight: 3,
              activeTrackColor: VoyoColors.discovery,
              inactiveTrackColor: VoyoColors.smoke,
              thumbColor: VoyoColors.paper,
              overlayColor: VoyoColors.discovery.withValues(alpha: 0.12),
            ),
            child: Slider(
              min: 0,
              max: (stops.length - 1).toDouble(),
              divisions: stops.length - 1,
              value: stops.indexOf(activeStop).toDouble(),
              label: '$activeStop min',
              onChanged:
                  controller.isLoading
                      ? null
                      : (v) => _onBudgetChange(stops[v.round()]),
            ),
          ),
          // Colour-coded budget legend (per-mode stops).
          Padding(
            padding: const EdgeInsets.only(top: 2),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                for (final stop in stops)
                  Text(
                    '${stop}m',
                    style: GoogleFonts.jetBrainsMono(
                      fontSize: 9,
                      fontWeight: FontWeight.w600,
                      color:
                          stop == activeStop
                              ? VoyoColors.ink
                              : VoyoColors.stone.withValues(alpha: 0.7),
                    ),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  void _onModeChange(String mode) {
    if (controller.profile == mode) return;
    // Switching mode resets to that mode's sensible default reach — never
    // keeps a 90-min walk after flipping from driving.
    final cfg = IsochroneController.modeConfig(mode);
    controller.profile = mode;
    controller.ranges = IsochroneController._nestedRanges(
      cfg.defaultMinutes,
      profile: mode,
    );
    controller.reExplore(mapController: mapController);
  }

  void _onBudgetChange(int maxMinutes) {
    controller.ranges = IsochroneController._nestedRanges(
      maxMinutes,
      profile: controller.profile,
    );
    controller.reExplore(mapController: mapController);
  }
}

class _ModeChip extends StatelessWidget {
  final IconData icon;
  final String label;
  final bool selected;
  final VoidCallback onTap;
  const _ModeChip({
    required this.icon,
    required this.label,
    required this.selected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final accent = VoyoColors.discovery;
    // `behavior: opaque` is required for reliable desktop/mouse hits:
    // without it, the unselected chip's transparent background fails
    // hit-testing on the padding regions under a mouse pointer (touch
    // usually still works, which masked this on mobile). Opaque makes the
    // whole chip area clickable on both platforms.
    return GestureDetector(
      behavior: HitTestBehavior.opaque,
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 160),
        padding: const EdgeInsets.symmetric(vertical: 7),
        decoration: BoxDecoration(
          color: selected ? accent.withValues(alpha: 0.14) : Colors.transparent,
          borderRadius: BorderRadius.circular(9),
          border: Border.all(
            color: selected ? accent.withValues(alpha: 0.5) : VoyoColors.smoke,
          ),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 16, color: selected ? accent : VoyoColors.stone),
            const SizedBox(height: 2),
            Text(
              label,
              style: GoogleFonts.instrumentSans(
                fontSize: 10,
                fontWeight: FontWeight.w600,
                color: selected ? accent : VoyoColors.stone,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Empty-state hint pill — shown when no isochrone has been generated.
class IsochroneHintPill extends StatelessWidget {
  final IconData icon;
  final String text;
  const IsochroneHintPill({super.key, required this.icon, required this.text});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
      decoration: BoxDecoration(
        color: VoyoColors.paper,
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.08),
            blurRadius: 10,
          ),
        ],
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 16, color: VoyoColors.discovery),
          const SizedBox(width: 8),
          Text(
            text,
            style: GoogleFonts.instrumentSans(
              fontSize: 12,
              color: VoyoColors.stone,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }
}

// ── Transport-mode helpers ──────────────────────────────────────────────────

IconData _modeIcon(String profile) {
  switch (profile) {
    case 'pedestrian':
      return Icons.directions_walk_rounded;
    case 'bicycle':
      return Icons.directions_bike_rounded;
    default: // 'auto'
      return Icons.directions_car_rounded;
  }
}

/// Non-modal, persistent summary card rendered inside the map `Stack`.
///
/// Shows the reachable-area headline plus the 5 nearest reachable POIs
/// ranked by travel time. Slides up over the map with **no scrim**, so the
/// isochrone bloom stays fully visible beside the list — a signature demo
/// moment. The card is anchored bottom-left with a constrained width so most
/// of the map (and the bloom) remains visible. Reset via the `Clear` action.
class IsochroneSummaryCard extends StatelessWidget {
  final IsochroneController controller;

  /// Called when a ranked POI row is tapped — opens the add-to-itinerary flow.
  final void Function(Poi poi) onPoiTap;

  // NOTE: vertical positioning is owned by the caller's Positioned wrapper
  // (ParentDataWidget must be a direct child of the map Stack, not nested
  // inside this widget's ListenableBuilder).
  const IsochroneSummaryCard({
    super.key,
    required this.controller,
    required this.onPoiTap,
  });

  @override
  Widget build(BuildContext context) {
    // NOTE: caller wraps us in Positioned. Returning Positioned here would
    // nest a ParentDataWidget under ListenableBuilder → "Incorrect use of
    // ParentDataWidget" on every rebuild.
    return ListenableBuilder(
      listenable: controller,
      builder: (ctx, _) {
        final visible = controller.hasSummary;
        return AnimatedSlide(
          offset: visible ? Offset.zero : const Offset(0, 1.15),
          duration: const Duration(milliseconds: 320),
          curve: Curves.easeOutCubic,
          child: AnimatedOpacity(
            opacity: visible ? 1 : 0,
            duration: const Duration(milliseconds: 220),
            child: Align(
              alignment: Alignment.bottomLeft,
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 12),
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 348),
                  child:
                      visible
                          ? _card(controller.profile)
                          : const SizedBox(height: 1),
                ),
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _card(String profile) {
    final cfg = IsochroneController.modeConfig(profile);
    final modeLabel = cfg.label;
    final ranked = controller.rankedPois;
    final anyEstimated = ranked.any((r) => r.estimated);

    return DecoratedBox(
      decoration: BoxDecoration(
        color: VoyoColors.paper.withValues(alpha: 0.97),
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: VoyoColors.smoke, width: 0.5),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.14),
            blurRadius: 24,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      // Transparent Material so the row InkWells get a visible splash without
      // losing the custom soft shadow on the DecoratedBox above.
      child: ClipRRect(
        borderRadius: BorderRadius.circular(18),
        child: Material(
          type: MaterialType.transparency,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              _header(modeLabel),
              Container(height: 1, color: VoyoColors.smoke),
              if (controller.isRanking)
                _rankingPlaceholder()
              else if (ranked.isEmpty)
                _emptyPlaces()
              else ...[
                for (var i = 0; i < ranked.length; i++)
                  _PoiRankRow(
                    rank: i + 1,
                    data: ranked[i],
                    // Per-row transport label: a 0.3 km hop shows a walk icon
                    // even in driving mode, so a car icon never sits next to
                    // a '0 km · 0 min' row.
                    profile: profile,
                    onTap: () => onPoiTap(ranked[i].poi),
                  ),
                if (anyEstimated) _estimateNote(),
              ],
              // Mode-aware blurb: walking = compact-area copy, driving =
              // cross-city copy, cycling = caveat about road comfort.
              _modeBlurb(cfg),
              Container(height: 1, color: VoyoColors.smoke),
              _footer(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _header(String modeLabel) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(14, 12, 14, 10),
      child: Row(
        children: [
          Container(
            width: 30,
            height: 30,
            decoration: BoxDecoration(
              color: VoyoColors.discovery.withValues(alpha: 0.12),
              borderRadius: BorderRadius.circular(9),
            ),
            child: const Icon(
              Icons.explore_rounded,
              size: 17,
              color: VoyoColors.discovery,
            ),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  'Reachable from this point',
                  style: GoogleFonts.fraunces(
                    fontSize: 15,
                    fontWeight: FontWeight.w600,
                    color: VoyoColors.ink,
                  ),
                ),
                const SizedBox(height: 1),
                Text(
                  '$modeLabel within ${controller.maxMinutes} min'
                  ' · ${controller.reachableCount}'
                  ' ${controller.reachableCount == 1 ? 'place' : 'places'}',
                  style: GoogleFonts.instrumentSans(
                    fontSize: 11.5,
                    color: VoyoColors.stone,
                    height: 1.3,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// One-line, mode-aware blurb under the ranked list. Sets realistic
  /// expectations: walking = compact-area framing, cycling = road-comfort
  /// caveat, driving = cross-city framing. (From the Tier 2 spec.)
  Widget _modeBlurb(IsochroneModeConfig cfg) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(14, 6, 14, 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(
            cfg.id == 'bicycle'
                ? Icons.info_outline_rounded
                : Icons.lightbulb_outline_rounded,
            size: 12,
            color: VoyoColors.stone,
          ),
          const SizedBox(width: 6),
          Expanded(
            child: Text(
              cfg.shortBlurb,
              style: GoogleFonts.instrumentSans(
                fontSize: 10.5,
                color: VoyoColors.stone,
                fontStyle: FontStyle.italic,
                height: 1.4,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _rankingPlaceholder() {
    return const Padding(
      padding: EdgeInsets.symmetric(vertical: 18),
      child: Center(
        child: SizedBox(
          width: 16,
          height: 16,
          child: CircularProgressIndicator(
            strokeWidth: 2,
            color: VoyoColors.discovery,
          ),
        ),
      ),
    );
  }

  Widget _emptyPlaces() {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 14),
      child: Text(
        'No saved places fall inside this area yet.',
        style: GoogleFonts.instrumentSans(
          fontSize: 12.5,
          color: VoyoColors.stone,
        ),
      ),
    );
  }

  Widget _estimateNote() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(14, 6, 14, 8),
      child: Row(
        children: [
          const Icon(
            Icons.timeline_outlined,
            size: 12,
            color: VoyoColors.stone,
          ),
          const SizedBox(width: 6),
          Expanded(
            child: Text(
              'Times approximate (offline estimate).',
              style: GoogleFonts.instrumentSans(
                fontSize: 10.5,
                color: VoyoColors.stone,
                fontStyle: FontStyle.italic,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _footer() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(8, 2, 8, 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.end,
        children: [
          TextButton.icon(
            onPressed: controller.clear,
            icon: const Icon(Icons.explore_off_outlined, size: 16),
            label: Text(
              'Clear',
              style: GoogleFonts.instrumentSans(
                color: VoyoColors.stone,
                fontWeight: FontWeight.w600,
                fontSize: 12,
              ),
            ),
            style: TextButton.styleFrom(
              foregroundColor: VoyoColors.stone,
              visualDensity: VisualDensity.compact,
            ),
          ),
        ],
      ),
    );
  }
}

class _PoiRankRow extends StatelessWidget {
  final int rank;
  final RankedPoi data;
  final String profile;
  final VoidCallback onTap;

  const _PoiRankRow({
    required this.rank,
    required this.data,
    required this.profile,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final rowMode = _effectiveMode(profile, data.distanceKm, data.durationMin);
    final rawMin = data.durationMin;
    // Minimum-ETA clamp (#8): any real movement is ≥ 1 min. A 0.1 km hop is
    // '1–2 min', never '0 min'. Only the exact origin (excluded upstream)
    // could legitimately read 0.
    final timeMin =
        (rawMin.isFinite && rawMin > 0)
            ? rawMin.round().clamp(1, 999)
            : _walkTimeMin(data.distanceKm).clamp(1, 999);
    return InkWell(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 9),
        child: Row(
          children: [
            SizedBox(
              width: 18,
              child: Text(
                '$rank',
                textAlign: TextAlign.center,
                style: GoogleFonts.fraunces(
                  fontSize: 15,
                  fontWeight: FontWeight.w600,
                  fontStyle: FontStyle.italic,
                  color: VoyoColors.discovery,
                ),
              ),
            ),
            const SizedBox(width: 10),
            Icon(_modeIcon(rowMode), size: 15, color: VoyoColors.stone),
            const SizedBox(width: 10),
            Expanded(
              child: Text(
                data.poi.name,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: GoogleFonts.instrumentSans(
                  fontSize: 13,
                  fontWeight: FontWeight.w500,
                  color: VoyoColors.ink,
                ),
              ),
            ),
            const SizedBox(width: 8),
            Text(
              '${data.distanceKm.toStringAsFixed(1)} km'
              ' · ${data.estimated ? '~' : ''}$timeMin min',
              style: GoogleFonts.instrumentSans(
                fontSize: 11.5,
                color: VoyoColors.stone,
                fontWeight: FontWeight.w500,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Decide which transport mode a row should *display*, independent of the
/// globally-selected mode. The spec: never show a car icon for a ~100 m hop.
/// Concretely — if the road/haversine distance is ≤ 1 km, the row is a walk
/// regardless of selected mode, and we recompute a plausible walk time so it
/// doesn't read '0 km · 0 min'.
String _effectiveMode(String selected, double distanceKm, double durationMin) {
  if (distanceKm <= 1.0) return 'pedestrian';
  // A 0-duration from a driving matrix at very short range is also a walk.
  if (selected == 'auto' && distanceKm <= 1.2 && durationMin < 2) {
    return 'pedestrian';
  }
  return selected;
}

/// Walk time estimate for short hops where the matrix returned ~0. ~5 km/h.
int _walkTimeMin(double distanceKm) =>
    (distanceKm / 5.0 * 60.0).round().clamp(1, 999);
