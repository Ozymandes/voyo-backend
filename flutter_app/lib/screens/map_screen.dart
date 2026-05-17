import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:latlong2/latlong.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../models/poi.dart';
import '../models/itinerary_poi.dart';
import '../services/supabase_service.dart';
import '../theme.dart';

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
        const LatLng(22.0, 24.0),
        const LatLng(32.0, 37.0),
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
    if (mounted) setState(() => _itineraryPois = pois);
  }

  void _showPoiBottomSheet(Poi poi) {
    showModalBottomSheet(
      context: context,
      backgroundColor: VoyoColors.paper,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (_) => Padding(
        padding: const EdgeInsets.fromLTRB(20, 12, 20, 28),
        child: Column(
          mainAxisSize: MainAxisSize.min,
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
            const SizedBox(height: 16),
            Text(
              poi.name,
              style: GoogleFonts.fraunces(
                fontSize: 24,
                fontStyle: FontStyle.italic,
                color: VoyoColors.ink,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              poi.category ?? '',
              style: GoogleFonts.instrumentSans(
                fontSize: 13,
                color: VoyoColors.stone,
              ),
            ),
            const SizedBox(height: 20),
            SizedBox(
              width: double.infinity,
              height: 48,
              child: FilledButton(
                onPressed: () => Navigator.pop(context),
                style: FilledButton.styleFrom(
                  backgroundColor: VoyoColors.terra,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14),
                  ),
                ),
                child: Text(
                  '+ Add to Itinerary',
                  style: GoogleFonts.instrumentSans(
                    fontSize: 15,
                    fontWeight: FontWeight.w600,
                    color: Colors.white,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showItineraryPoiInfo(ItineraryPoi poi) {
    ScaffoldMessenger.of(context).clearSnackBars();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          'Day ${poi.dayNumber} · Stop ${poi.sequenceOrder}: ${poi.name}',
          style: GoogleFonts.instrumentSans(color: Colors.white),
        ),
        backgroundColor: VoyoColors.sky,
        duration: const Duration(seconds: 3),
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          FlutterMap(
            options: MapOptions(
              initialCenter: const LatLng(30.0444, 31.2357),
              initialZoom: 7.0,
              onPositionChanged: _onPositionChanged,
            ),
            children: [
              TileLayer(
                urlTemplate:
                    'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                userAgentPackageName: 'com.voyo.app',
              ),
              // Regular POI markers
              MarkerLayer(
                markers: _pois.map((poi) {
                  return Marker(
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
                          border: Border.all(color: Colors.white, width: 2.5),
                          boxShadow: [
                            BoxShadow(
                              color: VoyoColors.expedition.withValues(alpha: 0.35),
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
                  );
                }).toList(),
              ),
              // Itinerary overlay markers
              MarkerLayer(
                markers: _itineraryPois.map((poi) {
                  return Marker(
                    point: LatLng(poi.latitude, poi.longitude),
                    width: 44,
                    height: 44,
                    child: GestureDetector(
                      onTap: () => _showItineraryPoiInfo(poi),
                      child: Stack(
                        alignment: Alignment.center,
                        children: [
                          Container(
                            width: 28,
                            height: 28,
                            decoration: BoxDecoration(
                              color: VoyoColors.sky,
                              shape: BoxShape.circle,
                              border: Border.all(color: Colors.white, width: 2.5),
                              boxShadow: [
                                BoxShadow(
                                  color: VoyoColors.sky.withValues(alpha: 0.35),
                                  blurRadius: 6,
                                ),
                              ],
                            ),
                          ),
                          Positioned(
                            top: 2,
                            child: Text(
                              'D${poi.dayNumber}',
                              style: GoogleFonts.instrumentSans(
                                fontSize: 8,
                                fontWeight: FontWeight.w700,
                                color: Colors.white,
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
          // Back button (shown when pushed via Navigator)
          if (Navigator.of(context).canPop())
            Positioned(
              top: MediaQuery.of(context).padding.top + 12,
              left: 12,
              child: GestureDetector(
                onTap: () => Navigator.of(context).pop(),
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
                  child: const Icon(Icons.arrow_back, color: VoyoColors.ink, size: 20),
                ),
              ),
            ),
          // Loading indicator
          if (_isLoading)
            Positioned(
              top: MediaQuery.of(context).padding.top + 12,
              right: 12,
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: VoyoColors.paper,
                  borderRadius: BorderRadius.circular(20),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withValues(alpha: 0.08),
                      blurRadius: 8,
                    ),
                  ],
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const SizedBox(
                      width: 12,
                      height: 12,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: VoyoColors.expedition,
                      ),
                    ),
                    const SizedBox(width: 6),
                    Text(
                      'Loading places…',
                      style: GoogleFonts.instrumentSans(
                        fontSize: 12,
                        color: VoyoColors.stone,
                      ),
                    ),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }
}
