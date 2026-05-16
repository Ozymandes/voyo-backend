import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../models/poi.dart';
import '../models/itinerary_poi.dart';
import '../services/supabase_service.dart';

class MapScreen extends StatefulWidget {
  const MapScreen({super.key});

  @override
  State<MapScreen> createState() => _MapScreenState();
}

class _MapScreenState extends State<MapScreen> {
  final _supabaseService = SupabaseService();
  List<Poi> _pois = [];
  List<ItineraryPoi> _itineraryPois = [];
  Timer? _debounceTimer;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadPoisForBounds(LatLngBounds(
        const LatLng(22.0, 24.0), // SW corner of Egypt
        const LatLng(32.0, 37.0), // NE corner of Egypt
      ));
      _loadItineraryPois();
    });
  }

  @override
  void dispose() {
    _debounceTimer?.cancel();
    super.dispose();
  }

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
      setState(() {
        _pois = pois;
        _isLoading = false;
      });
    } catch (e) {
      debugPrint('Error loading POIs: $e');
      setState(() => _isLoading = false);
    }
  }

  Future<void> _loadItineraryPois() async {
    final userId = Supabase.instance.client.auth.currentUser?.id;
    if (userId == null) return;
    final pois = await _supabaseService.getCurrentItineraryPois(userId);
    if (mounted) {
      setState(() => _itineraryPois = pois);
    }
  }

  void _showPoiSnackBar(Poi poi) {
    ScaffoldMessenger.of(context).clearSnackBars();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(poi.name)),
    );
  }

  void _showItineraryPoiInfo(ItineraryPoi poi) {
    ScaffoldMessenger.of(context).clearSnackBars();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Day ${poi.dayNumber} · Stop ${poi.sequenceOrder}: ${poi.name}'),
        backgroundColor: Colors.blue,
        duration: const Duration(seconds: 3),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: FlutterMap(
        options: MapOptions(
          initialCenter: const LatLng(30.0444, 31.2357), // Cairo
          initialZoom: 7.0,
          onPositionChanged: _onPositionChanged,
        ),
        children: [
          TileLayer(
            urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
            userAgentPackageName: 'com.voyo.mapsandbox',
          ),
          // Regular POI markers — red pins
          MarkerLayer(
            markers: _pois.map((poi) {
              return Marker(
                point: LatLng(poi.latitude, poi.longitude),
                width: 40,
                height: 40,
                child: GestureDetector(
                  onTap: () => _showPoiSnackBar(poi),
                  child: const Icon(
                    Icons.location_pin,
                    color: Colors.red,
                    size: 40,
                  ),
                ),
              );
            }).toList(),
          ),
          // Itinerary overlay — blue stars with day label, always on top
          MarkerLayer(
            markers: _itineraryPois.map((poi) {
              return Marker(
                point: LatLng(poi.latitude, poi.longitude),
                width: 50,
                height: 50,
                child: GestureDetector(
                  onTap: () => _showItineraryPoiInfo(poi),
                  child: Stack(
                    alignment: Alignment.topCenter,
                    children: [
                      const Icon(Icons.star, color: Colors.blue, size: 36),
                      Positioned(
                        top: 0,
                        child: Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 4, vertical: 1),
                          decoration: BoxDecoration(
                            color: Colors.blue,
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Text(
                            'D${poi.dayNumber}',
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 9,
                              fontWeight: FontWeight.bold,
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
    );
  }
}
