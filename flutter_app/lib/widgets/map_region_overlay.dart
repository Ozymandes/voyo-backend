// Region outlines + sliding info card for the map screen.
//
// Self-contained, mirroring widgets/map_isochrone_overlay.dart: owns all
// region state (GeoJSON + blurbs loading), tap resolution, and the info-card
// presentation so the region workstream never touches isochrone or routing.
//
// The map screen consumes three small pieces:
//   - [RegionController]   — loads assets, holds selection + the layer
//                            hit notifier that powers tap detection
//   - [RegionPolygons]     — drop into `FlutterMap.children`, placed between
//                            `IsochroneCenterMarker` and `PolylineLayer`
//                            (above isochrone rings, below routes & markers)
//   - [RegionInfoCard]     — drop into the map `Stack` (bottom-anchored card)
import 'dart:convert';
import 'dart:math' show min, max;

import 'package:flutter/material.dart';
import 'package:flutter/services.dart' show rootBundle;
import 'package:flutter_map/flutter_map.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:latlong2/latlong.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import '../theme.dart';

/// Distinct tint per region id, drawn from the Voyo palette. Six of eight use
/// exact `VoyoColors` accents; the two coastal regions use closely-related
/// muted hues so all eight read as one editorial palette.
const Map<String, Color> _kRegionTints = {
  'cairo': VoyoColors.sky, // blue
  'giza': VoyoColors.expedition, // red-orange
  'alexandria': VoyoColors.discovery, // purple
  'luxor': VoyoColors.caution, // gold
  'aswan': VoyoColors.verified, // green
  'sinai': VoyoColors.terra, // orange
  'red_sea': Color(0xFF2A6E8A), // muted deep teal (coastal)
  'marsa_alam': Color(0xFF8A5A2A), // warm bronze (desert coast)
};

/// A single region outline parsed from the GeoJSON, joined with its blurb.
@immutable
class RegionFeature {
  final String id;
  final String name;
  final double centerLng;
  final double centerLat;
  final double zoom;
  final List<LatLng> ring;
  final Color color;
  final String tagline;
  final String blurb;

  const RegionFeature({
    required this.id,
    required this.name,
    required this.centerLng,
    required this.centerLat,
    required this.zoom,
    required this.ring,
    required this.color,
    required this.tagline,
    required this.blurb,
  });

  // Bounding-box extents — used for the per-region POI query.
  double get minLat => ring.map((p) => p.latitude).reduce(min);
  double get maxLat => ring.map((p) => p.latitude).reduce(max);
  double get minLng => ring.map((p) => p.longitude).reduce(min);
  double get maxLng => ring.map((p) => p.longitude).reduce(max);
}

/// Result of the per-region POI query: total count in the region + the top
/// names ordered by popularity.
class _RegionPoiSummary {
  final int count;
  final List<String> topNames;
  const _RegionPoiSummary({required this.count, required this.topNames});
}

/// Owns region state: parses the GeoJSON + blurbs, tracks the selected region,
/// and exposes a `LayerHitNotifier` that flutter_map writes to during taps
/// (read from `MapOptions.onTap` to resolve which region was tapped).
class RegionController extends ChangeNotifier {
  /// flutter_map writes the tapped polygon(s) here during gesture handling;
  /// the map screen reads `.value` inside its `onTap` callback.
  final LayerHitNotifier<String> hitNotifier =
      ValueNotifier<LayerHitResult<String>?>(null);

  List<RegionFeature> _features = const [];
  Map<String, RegionFeature> _byId = const {};
  String? _selectedId;
  bool _loading = true;

  List<RegionFeature> get features => _features;
  String? get selectedId => _selectedId;
  RegionFeature? get selected =>
      _selectedId == null ? null : _byId[_selectedId];
  bool get isLoading => _loading;

  RegionFeature? byId(String id) => _byId[id];

  /// Loads `egypt_regions.geojson` and `egypt_region_blurbs.json` from the
  /// bundle and joins them into [features]. Safe to call from `initState`.
  Future<void> load() async {
    try {
      final geo =
          jsonDecode(
                await rootBundle.loadString(
                  'assets/geojson/egypt_regions.geojson',
                ),
              )
              as Map<String, dynamic>;
      final blurbs =
          jsonDecode(
                await rootBundle.loadString(
                  'assets/data/egypt_region_blurbs.json',
                ),
              )
              as Map<String, dynamic>;

      final fc = geo['features'] as List;
      final features = <RegionFeature>[];
      final byId = <String, RegionFeature>{};
      for (final raw in fc) {
        final f = raw as Map<String, dynamic>;
        final props = f['properties'] as Map<String, dynamic>;
        final id = props['id'] as String;
        // geometry.coordinates = [ ring ] where ring = [[lng, lat], ...]
        final coords =
            (f['geometry'] as Map<String, dynamic>)['coordinates'] as List;
        final ring =
            (coords.first as List).map((c) {
              final p = c as List;
              // GeoJSON orders [lng, lat]; LatLng takes (lat, lng).
              return LatLng((p[1] as num).toDouble(), (p[0] as num).toDouble());
            }).toList();
        final b = (blurbs[id] as Map<String, dynamic>?) ?? const {};
        final feature = RegionFeature(
          id: id,
          name: props['name'] as String,
          centerLng: (props['center_lng'] as num).toDouble(),
          centerLat: (props['center_lat'] as num).toDouble(),
          zoom: (props['zoom'] as num).toDouble(),
          ring: ring,
          color: _kRegionTints[id] ?? VoyoColors.discovery,
          tagline: (b['tagline'] as String?) ?? '',
          blurb: (b['blurb'] as String?) ?? '',
        );
        features.add(feature);
        byId[id] = feature;
      }
      _features = List.unmodifiable(features);
      _byId = byId;
      _loading = false;
      notifyListeners();
    } catch (e) {
      // Region outlines are a non-critical layer: fail soft (empty) so the
      // rest of the map keeps working. The error is logged for debugging.
      debugPrint('RegionController: failed to load regions: $e');
      _features = const [];
      _byId = const {};
      _loading = false;
      notifyListeners();
    }
  }

  void select(String id) {
    if (_selectedId == id) return;
    _selectedId = id;
    notifyListeners();
  }

  void dismiss() {
    if (_selectedId == null) return;
    _selectedId = null;
    notifyListeners();
  }

  @override
  void dispose() {
    hitNotifier.dispose();
    super.dispose();
  }
}

/// Region outlines rendered as a tappable `PolygonLayer`. Drop into
/// `FlutterMap.children`. Each polygon carries its region id as `hitValue`
/// so flutter_map can report which one was tapped via [RegionController.hitNotifier].
class RegionPolygons extends StatelessWidget {
  final RegionController controller;
  const RegionPolygons({super.key, required this.controller});

  @override
  Widget build(BuildContext context) {
    return ListenableBuilder(
      listenable: controller,
      builder: (ctx, _) {
        final sel = controller.selectedId;
        return PolygonLayer(
          hitNotifier: controller.hitNotifier,
          polygons: [
            for (final f in controller.features)
              Polygon(
                hitValue: f.id,
                points: f.ring,
                color: f.color.withValues(alpha: sel == f.id ? 0.26 : 0.12),
                borderColor: f.color.withValues(
                  alpha: sel == f.id ? 0.95 : 0.7,
                ),
                borderStrokeWidth: sel == f.id ? 2.5 : 2.0,
              ),
          ],
        );
      },
    );
  }
}

/// Bottom-anchored, sliding region info card. Reacts to the controller's
/// selection: slides up when a region is selected, slides down when cleared.
/// Loads the region's POI count + top picks via a single bounding-box query.
class RegionInfoCard extends StatefulWidget {
  final RegionController controller;

  /// Extra pixels to lift the card off the bottom edge (e.g. to clear the
  /// day-filter chip strip when an itinerary is active).
  final double bottomInset;
  const RegionInfoCard({
    super.key,
    required this.controller,
    this.bottomInset = 0,
  });

  @override
  State<RegionInfoCard> createState() => _RegionInfoCardState();
}

class _RegionInfoCardState extends State<RegionInfoCard> {
  // The last shown feature is retained so the slide-out animation has real
  // content to animate with (it sits off-screen + IgnorePointer'd while closed).
  RegionFeature? _display;
  _RegionPoiSummary? _poi;
  bool _poiLoading = false;

  @override
  void initState() {
    super.initState();
    widget.controller.addListener(_onChanged);
    _onChanged();
  }

  @override
  void didUpdateWidget(covariant RegionInfoCard oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.controller != widget.controller) {
      oldWidget.controller.removeListener(_onChanged);
      widget.controller.addListener(_onChanged);
      _onChanged();
    }
  }

  @override
  void dispose() {
    widget.controller.removeListener(_onChanged);
    super.dispose();
  }

  void _onChanged() {
    final sel = widget.controller.selected;
    if (sel == null) {
      if (mounted) setState(() {}); // re-render to slide out
      return;
    }
    if (sel.id == _display?.id) return; // same region, nothing to reload
    setState(() {
      _display = sel;
      _poi = null;
      _poiLoading = true;
    });
    _loadPois(sel);
  }

  Future<void> _loadPois(RegionFeature f) async {
    try {
      // One query, two results: count() ignores the limit and returns the
      // full regional tally; data returns the top-5 names by popularity.
      final res = await Supabase.instance.client
          .from('pois')
          .select('name')
          .eq('is_active', true)
          .gte('latitude', f.minLat)
          .lte('latitude', f.maxLat)
          .gte('longitude', f.minLng)
          .lte('longitude', f.maxLng)
          .order('popularity_score', ascending: false)
          .limit(5)
          .count(CountOption.exact);
      if (!mounted) return;
      final names = (res.data as List)
          .map((r) => (r as Map)['name'] as String)
          .toList(growable: false);
      setState(() {
        _poi = _RegionPoiSummary(count: res.count, topNames: names);
        _poiLoading = false;
      });
    } catch (e) {
      debugPrint('RegionInfoCard: POI query failed: $e');
      if (!mounted) return;
      setState(() => _poiLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final isOpen = widget.controller.selected != null;
    final mq = MediaQuery.of(context);
    final cardHeight = mq.size.height * 0.46;

    return Positioned(
      left: 0,
      right: 0,
      bottom: mq.padding.bottom + widget.bottomInset,
      child: AnimatedSlide(
        offset: isOpen ? Offset.zero : const Offset(0, 1),
        duration: const Duration(milliseconds: 320),
        curve: Curves.easeOutCubic,
        child: IgnorePointer(
          ignoring: !isOpen,
          child: AnimatedOpacity(
            opacity: isOpen ? 1 : 0,
            duration: const Duration(milliseconds: 220),
            child:
                _display == null
                    ? const SizedBox.shrink()
                    : _buildCard(context, _display!, cardHeight),
          ),
        ),
      ),
    );
  }

  Widget _buildCard(BuildContext context, RegionFeature f, double cardHeight) {
    final c = f.color;
    return Container(
      height: cardHeight,
      decoration: BoxDecoration(
        color: VoyoColors.paper,
        borderRadius: const BorderRadius.vertical(top: Radius.circular(28)),
        boxShadow: [
          BoxShadow(
            color: VoyoColors.ink.withValues(alpha: 0.14),
            blurRadius: 28,
            offset: const Offset(0, -4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Region accent strip
          Container(
            height: 4,
            decoration: BoxDecoration(
              color: c,
              borderRadius: const BorderRadius.vertical(
                top: Radius.circular(28),
              ),
            ),
          ),
          // Drag / grab handle
          Center(
            child: Container(
              margin: const EdgeInsets.only(top: 8),
              width: 36,
              height: 4,
              decoration: BoxDecoration(
                color: VoyoColors.smoke,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),
          // Header: name + tagline + close
          Padding(
            padding: const EdgeInsets.fromLTRB(20, 12, 14, 8),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        f.name,
                        style: GoogleFonts.fraunces(
                          fontSize: 26,
                          fontStyle: FontStyle.italic,
                          fontWeight: FontWeight.w600,
                          color: VoyoColors.ink,
                          height: 1.05,
                        ),
                      ),
                      if (f.tagline.isNotEmpty) ...[
                        const SizedBox(height: 4),
                        Text(
                          f.tagline,
                          style: GoogleFonts.instrumentSans(
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                            letterSpacing: 0.4,
                            color: c,
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
                GestureDetector(
                  onTap: widget.controller.dismiss,
                  child: Container(
                    padding: const EdgeInsets.all(6),
                    decoration: BoxDecoration(
                      color: VoyoColors.vellum,
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(
                      Icons.close_rounded,
                      size: 18,
                      color: VoyoColors.stone,
                    ),
                  ),
                ),
              ],
            ),
          ),
          // Scrollable body: blurb + POI summary
          Expanded(
            child: ListView(
              padding: const EdgeInsets.fromLTRB(20, 4, 20, 24),
              children: [
                if (f.blurb.isNotEmpty)
                  Text(
                    f.blurb,
                    style: GoogleFonts.instrumentSans(
                      fontSize: 13.5,
                      height: 1.6,
                      color: VoyoColors.ink.withValues(alpha: 0.8),
                    ),
                  ),
                const SizedBox(height: 16),
                Container(height: 1, color: VoyoColors.smoke),
                const SizedBox(height: 14),
                _poiSection(f),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _poiSection(RegionFeature f) {
    final c = f.color;
    if (_poiLoading) {
      return Row(
        children: [
          SizedBox(
            width: 14,
            height: 14,
            child: CircularProgressIndicator(strokeWidth: 2, color: c),
          ),
          const SizedBox(width: 8),
          Text(
            'Finding places…',
            style: GoogleFonts.instrumentSans(
              fontSize: 12,
              color: VoyoColors.stone,
            ),
          ),
        ],
      );
    }
    final s = _poi;
    if (s == null) {
      return Row(
        children: [
          Icon(Icons.place_outlined, size: 16, color: VoyoColors.stone),
          const SizedBox(width: 6),
          Text(
            'Places in this region',
            style: GoogleFonts.instrumentSans(
              fontSize: 12,
              color: VoyoColors.stone,
            ),
          ),
        ],
      );
    }
    final names = s.topNames;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(Icons.place_rounded, size: 16, color: c),
            const SizedBox(width: 6),
            Text(
              '${s.count} ${s.count == 1 ? "place" : "places"} in this region',
              style: GoogleFonts.instrumentSans(
                fontSize: 13,
                fontWeight: FontWeight.w600,
                color: VoyoColors.ink,
              ),
            ),
          ],
        ),
        if (names.isNotEmpty) ...[
          const SizedBox(height: 12),
          Text(
            'TOP PICKS',
            style: GoogleFonts.instrumentSans(
              fontSize: 10.5,
              fontWeight: FontWeight.w700,
              letterSpacing: 0.8,
              color: VoyoColors.stone,
            ),
          ),
          const SizedBox(height: 8),
          for (var i = 0; i < names.length; i++)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 4),
              child: Row(
                children: [
                  Container(
                    width: 22,
                    height: 22,
                    alignment: Alignment.center,
                    decoration: BoxDecoration(
                      color: c.withValues(alpha: 0.12),
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: Text(
                      '${i + 1}',
                      style: GoogleFonts.instrumentSans(
                        fontSize: 11,
                        fontWeight: FontWeight.w700,
                        color: c,
                      ),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      names[i],
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: GoogleFonts.instrumentSans(
                        fontSize: 13.5,
                        color: VoyoColors.ink,
                      ),
                    ),
                  ),
                ],
              ),
            ),
        ],
      ],
    );
  }
}
