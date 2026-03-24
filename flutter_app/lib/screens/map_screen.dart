import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import '../models/poi.dart';
import '../services/supabase_service.dart';

class MapScreen extends StatefulWidget {
  const MapScreen({super.key});

  @override
  State<MapScreen> createState() => _MapScreenState();
}

class _MapScreenState extends State<MapScreen> {
  final _supabaseService = SupabaseService();
  List<Poi> _pois = [];
  Timer? _debounceTimer;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    // Load initial POIs after the first frame renders
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadPoisForBounds(LatLngBounds(
        const LatLng(22.0, 24.0), // SW corner of Egypt
        const LatLng(32.0, 37.0), // NE corner of Egypt
      ));
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

  void _showPoiSnackBar(Poi poi) {
    ScaffoldMessenger.of(context).clearSnackBars();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(poi.name)),
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
        ],
      ),
    );
  }
}
