import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:latlong2/latlong.dart';
import 'package:url_launcher/url_launcher.dart';
import '../models/itinerary_poi.dart';

class RoutingService {
  static const _osrmBase =
      'https://router.project-osrm.org/route/v1/driving';

  /// Fetches a road-following polyline from OSRM.
  /// Falls back to straight-line connections when the API is unavailable.
  Future<List<LatLng>> fetchRoute(List<LatLng> waypoints) async {
    if (waypoints.length < 2) return waypoints;

    final coords =
        waypoints.map((p) => '${p.longitude},${p.latitude}').join(';');
    final uri = Uri.parse(
        '$_osrmBase/$coords?overview=full&geometries=geojson');

    try {
      final response =
          await http.get(uri).timeout(const Duration(seconds: 10));
      if (response.statusCode != 200) return waypoints;

      final data = json.decode(response.body) as Map<String, dynamic>;
      final routes = data['routes'] as List?;
      if (routes == null || routes.isEmpty) return waypoints;

      final coordinates =
          routes[0]['geometry']['coordinates'] as List;
      return coordinates
          .map((c) => LatLng(
                (c[1] as num).toDouble(),
                (c[0] as num).toDouble(),
              ))
          .toList();
    } catch (e) {
      debugPrint('OSRM unavailable, using straight lines: $e');
      return waypoints;
    }
  }

  /// Fetches road-following routes for every day in the itinerary.
  /// Returns dayNumber → sorted route polyline.
  Future<Map<int, List<LatLng>>> fetchRoutesByDay(
      List<ItineraryPoi> pois) async {
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
      routes[entry.key] = await fetchRoute(waypoints);
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

    final sorted = [...pois]
      ..sort((a, b) {
        final d = a.dayNumber.compareTo(b.dayNumber);
        return d != 0 ? d : a.sequenceOrder.compareTo(b.sequenceOrder);
      });

    final origin =
        '${sorted.first.latitude},${sorted.first.longitude}';
    final destination =
        '${sorted.last.latitude},${sorted.last.longitude}';

    final buffer = StringBuffer(
      'https://www.google.com/maps/dir/?api=1'
      '&origin=$origin'
      '&destination=$destination'
      '&travelmode=driving',
    );

    // Google Maps URL supports at most 8 intermediate waypoints
    if (sorted.length > 2) {
      final middle =
          sorted.sublist(1, sorted.length - 1).take(8).toList();
      final waypoints =
          middle.map((p) => '${p.latitude},${p.longitude}').join('|');
      buffer.write('&waypoints=$waypoints');
    }

    return buffer.toString();
  }
}
