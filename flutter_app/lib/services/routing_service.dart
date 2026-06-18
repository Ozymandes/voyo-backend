import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:http/http.dart' as http;
import 'package:latlong2/latlong.dart';
import 'package:url_launcher/url_launcher.dart';
import '../models/itinerary_poi.dart';

/// One reachable-area ring returned by the isochrone endpoint.
class IsochroneRing {
  final int timeMinutes;
  final List<LatLng> points;

  const IsochroneRing({required this.timeMinutes, required this.points});
}

/// One row of the origin→destinations travel matrix returned by the OSRM
/// ``/table`` endpoint. ``index`` aligns to the caller's destinations order.
class DistanceTableRow {
  final int index;
  final double distanceM;
  final double durationS;

  const DistanceTableRow({
    required this.index,
    required this.distanceM,
    required this.durationS,
  });
}

class RoutingService {
  static const _defaultBackend = 'http://10.0.2.2:8000';

  String get _backend => dotenv.env['CLEO_API_URL'] ?? _defaultBackend;

  /// Fetches a road-following polyline from the self-hosted Valhalla backend
  /// (``GET /api/v1/routing/route``). Returns ``null`` when the backend is
  /// unavailable so the caller can render an honest fallback banner instead
  /// of silently drawing a straight line through the POI markers (which
  /// previously looked indistinguishable from a real routed path — the
  /// exact failure mode the spec calls out as demo-dangerous). On success
  /// returns the decoded [lat, lng] polyline.
  Future<List<LatLng>?> fetchRoute(
    List<LatLng> waypoints, {
    String profile = 'auto',
  }) async {
    if (waypoints.length < 2) return waypoints;

    final coords = waypoints
        .map((p) => '${p.latitude},${p.longitude}')
        .join(';');
    final uri = Uri.parse(
      '$_backend/api/v1/routing/route?waypoints=$coords&profile=$profile',
    );

    try {
      final response = await http.get(uri).timeout(const Duration(seconds: 15));
      if (response.statusCode != 200) {
        debugPrint('Route engine returned ${response.statusCode}; '
            'refusing to render a straight line as a real route.');
        return null;
      }

      final data = json.decode(response.body) as Map<String, dynamic>;
      // Valhalla backend returns polyline as [[lat, lng], ...]
      final polyline = data['polyline'] as List?;
      if (polyline == null || polyline.isEmpty) {
        debugPrint('Route response had no polyline geometry; returning null.');
        return null;
      }

      return polyline
          .map(
            (c) => LatLng((c[0] as num).toDouble(), (c[1] as num).toDouble()),
          )
          .toList();
    } catch (e) {
      debugPrint('Valhalla route unavailable (will NOT fake a straight line): $e');
      return null;
    }
  }

  /// Fetches reachable-area rings (isochrone) from a center point via the
  /// self-hosted Valhalla backend (``POST /api/v1/routing/isochrone``).
  /// Returns one [IsochroneRing] per requested time range, ordered inner
  /// (shortest time) to outer (longest time). Returns an empty list on error.
  Future<List<IsochroneRing>> fetchIsochrone(
    LatLng center, {
    List<int> ranges = const [30, 60],
    String profile = 'auto',
  }) async {
    final uri = Uri.parse('$_backend/api/v1/routing/isochrone');
    final body = json.encode({
      'latitude': center.latitude,
      'longitude': center.longitude,
      'ranges': ranges,
      'profile': profile,
    });

    try {
      final response = await http
          .post(uri, headers: {'Content-Type': 'application/json'}, body: body)
          .timeout(const Duration(seconds: 25));
      if (response.statusCode != 200) return [];

      final data = json.decode(response.body) as Map<String, dynamic>;
      final polygons = data['polygons'] as List?;
      if (polygons == null) return [];

      final rings = <IsochroneRing>[];
      for (final p in polygons) {
        final timeMin = (p['time_minutes'] as num?)?.toInt() ?? 0;
        final geojson = p['geojson'] as Map<String, dynamic>?;
        final coords = _extractRingCoordinates(geojson);
        if (coords.isNotEmpty) {
          rings.add(IsochroneRing(timeMinutes: timeMin, points: coords));
        }
      }
      // Sort inner (smallest time) first so the outer ring renders underneath.
      rings.sort((a, b) => a.timeMinutes.compareTo(b.timeMinutes));
      return rings;
    } catch (e) {
      debugPrint('Valhalla isochrone unavailable: $e');
      return [];
    }
  }

  /// Fetches an origin→destinations travel matrix (distance + duration) from
  /// the self-hosted OSRM backend (``POST /api/v1/routing/table``). Returns one
  /// [DistanceTableRow] per destination, aligned to the input order, or `null`
  /// when the backend is unreachable (503/timeout) so the caller can fall back
  /// to a local straight-line estimate.
  Future<List<DistanceTableRow>?> fetchTable({
    required LatLng origin,
    required List<LatLng> destinations,
    String profile = 'auto',
  }) async {
    if (destinations.isEmpty) return const [];
    final uri = Uri.parse('$_backend/api/v1/routing/table');
    final body = json.encode({
      'origin': {'lat': origin.latitude, 'lng': origin.longitude},
      'destinations': [
        for (final d in destinations) {'lat': d.latitude, 'lng': d.longitude},
      ],
      'profile': profile,
    });

    try {
      final response = await http
          .post(uri, headers: {'Content-Type': 'application/json'}, body: body)
          .timeout(const Duration(seconds: 15));
      if (response.statusCode != 200) return null;
      final data = json.decode(response.body) as List;
      return [
        for (final row in data)
          DistanceTableRow(
            index: (row['index'] as num).toInt(),
            distanceM: (row['distance_m'] as num).toDouble(),
            durationS: (row['duration_s'] as num).toDouble(),
          ),
      ];
    } catch (e) {
      debugPrint('Routing table unavailable, will estimate: $e');
      return null;
    }
  }

  /// Extracts a flat ring of [LatLng] from a Valhalla isochrone GeoJSON
  /// feature (Polygon or MultiPolygon — takes the largest outer ring).
  List<LatLng> _extractRingCoordinates(Map<String, dynamic>? geojson) {
    if (geojson == null) return [];
    final geom = (geojson['geometry'] ?? geojson) as Map<String, dynamic>;
    final type = geom['type'];
    final coords = geom['coordinates'];
    if (coords == null) return [];

    List ring;
    if (type == 'Polygon') {
      // coordinates = [ [outerRing], [hole1], ... ] — take the outer ring.
      ring = (coords as List).isNotEmpty ? coords[0] as List : [];
    } else if (type == 'MultiPolygon') {
      // Pick the polygon with the most points as the representative ring.
      List best = [];
      for (final poly in coords as List) {
        if (poly is List &&
            poly.isNotEmpty &&
            (poly[0] as List).length > best.length) {
          best = poly[0] as List;
        }
      }
      ring = best;
    } else {
      return [];
    }

    return ring
        .whereType<List>()
        .map((c) => LatLng((c[1] as num).toDouble(), (c[0] as num).toDouble()))
        .toList();
  }

  /// Fetches road-following routes for every day in the itinerary.
  /// Returns dayNumber → sorted route polyline. Days whose route could
  /// not be fetched (Valhalla down, etc.) are OMITTED — the caller renders
  /// an honest fallback banner rather than a fake straight-line polyline.
  Future<Map<int, List<LatLng>>> fetchRoutesByDay(
    List<ItineraryPoi> pois,
  ) async {
    final byDay = <int, List<ItineraryPoi>>{};
    for (final poi in pois) {
      byDay.putIfAbsent(poi.dayNumber, () => []).add(poi);
    }
    for (final stops in byDay.values) {
      stops.sort((a, b) => a.sequenceOrder.compareTo(b.sequenceOrder));
    }

    final routes = <int, List<LatLng>>{};
    for (final entry in byDay.entries) {
      final waypoints =
          entry.value.map((p) => LatLng(p.latitude, p.longitude)).toList();
      final route = await fetchRoute(waypoints);
      if (route != null) {
        routes[entry.key] = route;
      }
      // route == null → omit; the caller shows the fallback banner.
    }
    return routes;
  }

  /// Launches the full itinerary route in Google Maps.
  Future<void> openInGoogleMaps(List<ItineraryPoi> pois) async {
    final url = buildGoogleMapsUrl(pois);
    if (url == null) return;
    final uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    }
  }

  /// Builds the Google Maps directions URL for the full itinerary.
  /// Returns null when the list is empty.
  String? buildGoogleMapsUrl(List<ItineraryPoi> pois) {
    if (pois.isEmpty) return null;

    final sorted = [...pois]..sort((a, b) {
      final d = a.dayNumber.compareTo(b.dayNumber);
      return d != 0 ? d : a.sequenceOrder.compareTo(b.sequenceOrder);
    });

    final origin = '${sorted.first.latitude},${sorted.first.longitude}';
    final destination = '${sorted.last.latitude},${sorted.last.longitude}';

    final buffer = StringBuffer(
      'https://www.google.com/maps/dir/?api=1'
      '&origin=$origin'
      '&destination=$destination'
      '&travelmode=driving',
    );

    // Google Maps URL supports at most 8 intermediate waypoints
    if (sorted.length > 2) {
      final middle = sorted.sublist(1, sorted.length - 1).take(8).toList();
      final waypoints = middle
          .map((p) => '${p.latitude},${p.longitude}')
          .join('|');
      buffer.write('&waypoints=$waypoints');
    }

    return buffer.toString();
  }
}
