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
import 'dart:math' show min, max;

import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:latlong2/latlong.dart';

import '../services/routing_service.dart';
import '../theme.dart';

/// Owns the "Explore from here" isochrone state + fetch/recompute logic.
class IsochroneController extends ChangeNotifier {
  final RoutingService _routing = RoutingService();

  List<IsochroneRing> _rings = [];
  LatLng? _center;
  bool _loading = false;

  List<int> ranges = const [30, 60];
  String profile = 'auto';

  List<IsochroneRing> get rings => _rings;
  LatLng? get center => _center;
  bool get isLoading => _loading;
  bool get hasData => _rings.isNotEmpty || _center != null || _loading;
  bool get isEmpty => !hasData;

  Future<void> explore(
    LatLng point,
    List<LatLng> poiPoints, {
    required MapController mapController,
    required BuildContext context,
    List<int>? ranges,
    String? profile,
  }) async {
    final r = ranges ?? this.ranges;
    final p = profile ?? this.profile;
    _center = point;
    _loading = true;
    _rings = [];
    notifyListeners();

    final rings = await _routing.fetchIsochrone(point, ranges: r, profile: p);
    _rings = rings;
    _loading = false;
    notifyListeners();

    if (rings.isEmpty) return;
    _fitBounds(rings, mapController);
    final reachable = _countReachable(poiPoints, rings.last.points);
    if (context.mounted) {
      showIsochroneSummary(
        context: context,
        controller: this,
        maxMinutes: rings.last.timeMinutes,
        reachableCount: reachable,
        profile: p,
      );
    }
  }

  Future<void> reExplore({
    required List<LatLng> poiPoints,
    required MapController mapController,
    required BuildContext context,
  }) async {
    final c = _center;
    if (c == null) return;
    await explore(c, poiPoints, mapController: mapController, context: context);
  }

  void clear() {
    _rings = [];
    _center = null;
    notifyListeners();
  }

  int _countReachable(List<LatLng> poiPoints, List<LatLng> polygon) {
    if (polygon.length < 3) return 0;
    var count = 0;
    for (final p in poiPoints) {
      if (_pointInPolygon(p, polygon)) count++;
    }
    return count;
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

/// Reachable-area rings rendered as a `PolygonLayer`.
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
                color: VoyoColors.discovery.withValues(alpha: 0.10),
                borderColor: VoyoColors.discovery.withValues(alpha: 0.55),
                borderStrokeWidth: 1.5,
              ),
          ],
        );
      },
    );
  }
}

/// Center marker for the explored point.
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

/// Right-side control cluster: clear button. Self-positions inside the Stack.
class IsochroneControls extends StatelessWidget {
  final IsochroneController controller;
  final double topPad;

  const IsochroneControls({
    super.key,
    required this.controller,
    required this.topPad,
  });

  @override
  Widget build(BuildContext context) {
    return ListenableBuilder(
      listenable: controller,
      builder: (ctx, _) {
        if (!controller.hasData) return const SizedBox.shrink();
        return Positioned(
          top: topPad + 12,
          right: 12,
          child: _IsochroneIconButton(
            icon: Icons.explore_off_outlined,
            color: VoyoColors.discovery,
            onTap: controller.clear,
          ),
        );
      },
    );
  }
}

class _IsochroneIconButton extends StatelessWidget {
  final IconData icon;
  final Color color;
  final VoidCallback onTap;
  const _IsochroneIconButton({
    required this.icon,
    required this.color,
    required this.onTap,
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

/// Empty-state hint pill.
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

/// Reachable-POI summary sheet shown after a successful explore().
void showIsochroneSummary({
  required BuildContext context,
  required IsochroneController controller,
  required int maxMinutes,
  required int reachableCount,
  String profile = 'auto',
}) {
  final profileLabel =
      const {
        'auto': 'Driving',
        'pedestrian': 'Walking',
        'bicycle': 'Cycling',
      }[profile] ??
      'Driving';
  showModalBottomSheet(
    context: context,
    backgroundColor: VoyoColors.paper,
    shape: const RoundedRectangleBorder(
      borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
    ),
    builder: (_) => SafeArea(
      child: Padding(
        padding: const EdgeInsets.fromLTRB(20, 18, 20, 16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.explore_rounded, color: VoyoColors.discovery, size: 22),
                const SizedBox(width: 10),
                Text(
                  'Reachable from this point',
                  style: GoogleFonts.fraunces(
                    fontSize: 17,
                    fontWeight: FontWeight.w600,
                    color: VoyoColors.ink,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            RichText(
              text: TextSpan(
                style: GoogleFonts.instrumentSans(
                  fontSize: 14,
                  color: VoyoColors.ink,
                  height: 1.5,
                ),
                children: [
                  TextSpan(text: '$profileLabel within '),
                  TextSpan(
                    text: '$maxMinutes minutes',
                    style: const TextStyle(fontWeight: FontWeight.w700),
                  ),
                  const TextSpan(text: ' from here you can reach '),
                  TextSpan(
                    text: '$reachableCount',
                    style: const TextStyle(fontWeight: FontWeight.w700),
                  ),
                  TextSpan(
                    text: ' ${reachableCount == 1 ? "place" : "places"} in the VOYO database.',
                  ),
                ],
              ),
            ),
            const SizedBox(height: 14),
            Row(
              children: [
                TextButton.icon(
                  onPressed: () => Navigator.pop(context),
                  icon: const Icon(Icons.check, size: 18),
                  label: const Text('Got it'),
                ),
                const Spacer(),
                TextButton(
                  onPressed: () {
                    Navigator.pop(context);
                    controller.clear();
                  },
                  child: Text('Clear', style: TextStyle(color: VoyoColors.stone)),
                ),
              ],
            ),
          ],
        ),
      ),
    ),
  );
}
