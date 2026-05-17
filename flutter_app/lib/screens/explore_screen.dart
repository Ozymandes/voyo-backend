import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:latlong2/latlong.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:flutter/foundation.dart';
import '../models/poi.dart';
import '../services/supabase_service.dart';
import '../theme.dart';
import '../widgets/cleo_owl.dart';
import 'map_screen.dart';
import 'settings_sheets.dart';

const _categories = [
  'All',
  'Historical',
  'Religious',
  'Nature',
  'Dining',
  'Shopping',
  'Hidden Gems',
];

// Fallback sample data shown when the DB has no POIs yet.
final _fallbackPois = [
  Poi(id: 1, name: 'Khan el-Khalili', latitude: 30.0478, longitude: 31.2625, category: 'shopping', city: 'Cairo', averageRating: 4.6, totalReviews: 2840, isVerified: true, popularityScore: 85, ticketPrice: 0, currency: 'EGP', historicalSignificance: 'One of the oldest bazaars in the world, dating back to 1382. A hub of commerce and culture in Islamic Cairo.'),
  Poi(id: 2, name: 'Egyptian Museum', latitude: 30.0478, longitude: 31.2336, category: 'historical', city: 'Cairo', averageRating: 4.7, totalReviews: 5200, isVerified: true, popularityScore: 92, ticketPrice: 200, currency: 'EGP', historicalSignificance: 'Home to the world\'s largest collection of ancient Egyptian artifacts, including the treasures of Tutankhamun.'),
  Poi(id: 3, name: 'Coptic Cairo', latitude: 30.0054, longitude: 31.2296, category: 'historical', city: 'Cairo', averageRating: 4.5, totalReviews: 1100, isVerified: true, popularityScore: 60, ticketPrice: 0, currency: 'EGP', historicalSignificance: 'The oldest part of Cairo, containing some of the earliest Christian churches in Egypt.'),
  Poi(id: 4, name: 'Karnak Temple', latitude: 25.7188, longitude: 32.6573, category: 'historical', city: 'Luxor', averageRating: 4.9, totalReviews: 6800, isVerified: true, popularityScore: 97, ticketPrice: 220, currency: 'EGP', historicalSignificance: 'The largest ancient religious site in the world, built over 2,000 years by successive pharaohs.'),
  Poi(id: 5, name: 'Luxor Temple', latitude: 25.6997, longitude: 32.6390, category: 'historical', city: 'Luxor', averageRating: 4.8, totalReviews: 4200, isVerified: true, popularityScore: 88, ticketPrice: 160, currency: 'EGP'),
  Poi(id: 6, name: 'Medinet Habu', latitude: 25.7197, longitude: 32.6016, category: 'historical', city: 'Luxor', averageRating: 4.8, totalReviews: 820, isVerified: true, popularityScore: 22, historicalSignificance: 'The mortuary temple of Ramesses III, one of the best-preserved temples in Egypt — and far less crowded than Karnak.'),
  Poi(id: 7, name: 'Philae Temple', latitude: 24.0247, longitude: 32.8836, category: 'historical', city: 'Aswan', averageRating: 4.8, totalReviews: 3100, isVerified: true, popularityScore: 78, ticketPrice: 180, currency: 'EGP', historicalSignificance: 'An island temple complex dedicated to Isis, relocated to save it from the rising waters of Lake Nasser.'),
  Poi(id: 8, name: 'Bibliotheca Alexandrina', latitude: 31.2089, longitude: 29.9085, category: 'cultural', city: 'Alexandria', averageRating: 4.6, totalReviews: 1900, isVerified: true, popularityScore: 65, ticketPrice: 70, currency: 'EGP'),
];

// ---------------------------------------------------------------------------
// ExploreScreen
// ---------------------------------------------------------------------------

class ExploreScreen extends StatefulWidget {
  final VoidCallback? onSwitchToCleo;
  const ExploreScreen({super.key, this.onSwitchToCleo});

  @override
  State<ExploreScreen> createState() => _ExploreScreenState();
}

class _ExploreScreenState extends State<ExploreScreen> {
  final _supabaseService = SupabaseService();
  final _supabase = Supabase.instance.client;

  String? _userName;
  String? _userEmail;
  List<Poi> _pois = [];
  String _selectedCategory = 'All';
  bool _loadingPois = true;
  bool _profileOpen = false;
  bool _usingFallback = false;
  String? _poisError;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    final userId = _supabase.auth.currentUser?.id;

    // Load POIs — fall back to sample data if DB is empty or unavailable
    try {
      final pois = await _supabaseService.getFeaturedPois();
      if (mounted) {
        setState(() {
          _pois = pois.isNotEmpty ? pois : _fallbackPois;
          _usingFallback = pois.isEmpty;
          _loadingPois = false;
        });
      }
    } catch (e) {
      debugPrint('ExploreScreen: POI load failed — $e');
      if (mounted) {
        setState(() {
          _pois = _fallbackPois;
          _usingFallback = true;
          _poisError = e.toString();
          _loadingPois = false;
        });
      }
    }

    if (userId == null) return;

    try {
      final profile = await _supabase
          .from('user_profiles')
          .select('full_name')
          .eq('user_id', userId)
          .maybeSingle() as Map<String, dynamic>?;
      if (mounted) {
        setState(() {
          _userName = profile?['full_name'] as String?;
          _userEmail = _supabase.auth.currentUser?.email;
        });
      }
    } catch (_) {}
  }

  String get _greeting {
    final h = DateTime.now().hour;
    if (h >= 5 && h < 12) return 'Good morning';
    if (h >= 12 && h < 18) return 'Good afternoon';
    return 'Good evening';
  }

  String get _greetingEmoji {
    final h = DateTime.now().hour;
    if (h >= 5 && h < 12) return '☀️';
    if (h >= 12 && h < 18) return '🌤️';
    return '🌙';
  }

  List<Poi> get _filteredPois {
    if (_selectedCategory == 'All') return _pois;
    if (_selectedCategory == 'Hidden Gems') {
      return _pois.where((p) => p.isHiddenGem).toList();
    }
    final cat = _selectedCategory.toLowerCase();
    return _pois.where((p) => p.category?.toLowerCase() == cat).toList();
  }

  List<Poi> get _hiddenGems => _pois.where((p) => p.isHiddenGem).toList();

  @override
  Widget build(BuildContext context) {
    final top = MediaQuery.of(context).padding.top;
    return Scaffold(
      backgroundColor: VoyoColors.page,
      body: Stack(
        children: [
          CustomScrollView(
            slivers: [
              SliverToBoxAdapter(child: _buildHeader(top)),
              SliverToBoxAdapter(child: _buildMapZone()),
              SliverToBoxAdapter(child: _buildCategoryRow()),
              SliverToBoxAdapter(child: _buildDiscoverSection()),
              if (_hiddenGems.isNotEmpty)
                SliverToBoxAdapter(child: _buildHiddenGemsStrip()),
              const SliverToBoxAdapter(child: SizedBox(height: 24)),
            ],
          ),
          // Sidebar barrier
          AnimatedOpacity(
            opacity: _profileOpen ? 1.0 : 0.0,
            duration: const Duration(milliseconds: 250),
            child: IgnorePointer(
              ignoring: !_profileOpen,
              child: GestureDetector(
                onTap: () => setState(() => _profileOpen = false),
                child: Container(color: Colors.black.withValues(alpha: 0.45)),
              ),
            ),
          ),
          // Profile sidebar
          Align(
            alignment: Alignment.centerLeft,
            child: AnimatedSlide(
              offset: _profileOpen ? Offset.zero : const Offset(-1, 0),
              duration: const Duration(milliseconds: 300),
              curve: Curves.easeInOut,
              child: _buildSidebar(top),
            ),
          ),
        ],
      ),
    );
  }

  // ── Header ────────────────────────────────────────────────────────────────

  Widget _buildHeader(double topPadding) {
    final initial =
        (_userName?.isNotEmpty == true) ? _userName![0].toUpperCase() : 'V';
    return Container(
      color: VoyoColors.paper,
      padding: EdgeInsets.fromLTRB(16, topPadding + 12, 16, 14),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              GestureDetector(
                onTap: () => setState(() => _profileOpen = true),
                child: Container(
                  width: 36,
                  height: 36,
                  decoration: const BoxDecoration(
                    color: Color(0x1AD45028),
                    shape: BoxShape.circle,
                  ),
                  child: Center(
                    child: Text(
                      initial,
                      style: GoogleFonts.fraunces(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                        color: VoyoColors.expedition,
                      ),
                    ),
                  ),
                ),
              ),
              const Spacer(),
              Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    'VOYO',
                    style: GoogleFonts.fraunces(
                      fontSize: 22,
                      fontWeight: FontWeight.w400,
                      color: VoyoColors.ink,
                      letterSpacing: 1,
                    ),
                  ),
                  const SizedBox(width: 3),
                  Container(
                    width: 6,
                    height: 6,
                    decoration: const BoxDecoration(
                      color: VoyoColors.expedition,
                      shape: BoxShape.circle,
                    ),
                  ),
                ],
              ),
              const Spacer(),
              GestureDetector(
                onTap: _showNotificationPanel,
                child: Container(
                  width: 36,
                  height: 36,
                  decoration: BoxDecoration(
                    color: VoyoColors.vellum,
                    shape: BoxShape.circle,
                    border: Border.all(color: VoyoColors.smoke),
                  ),
                  child: const Icon(Icons.notifications_none_outlined,
                      size: 18, color: VoyoColors.stone),
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          Text(
            '$_greeting, ${_userName ?? 'Explorer'} $_greetingEmoji',
            style: GoogleFonts.fraunces(
              fontSize: 22,
              fontStyle: FontStyle.italic,
              color: VoyoColors.ink,
            ),
          ),
          const SizedBox(height: 12),
          GestureDetector(
            onTap: () => Navigator.push(
              context,
              PageRouteBuilder(
                pageBuilder: (_, __, ___) => _SearchOverlay(
                  service: _supabaseService,
                  onSelect: _showPoiSheet,
                ),
                transitionsBuilder: (_, anim, __, child) =>
                    FadeTransition(opacity: anim, child: child),
                transitionDuration: const Duration(milliseconds: 180),
              ),
            ),
            child: Container(
              height: 44,
              decoration: BoxDecoration(
                color: VoyoColors.vellum,
                borderRadius: BorderRadius.circular(22),
                border: Border.all(color: VoyoColors.smoke),
              ),
              child: Row(
                children: [
                  const Padding(
                    padding: EdgeInsets.only(left: 14),
                    child: Icon(Icons.search, color: VoyoColors.stone, size: 18),
                  ),
                  const SizedBox(width: 8),
                  Text(
                    'Search places, landmarks…',
                    style: GoogleFonts.instrumentSans(
                        color: VoyoColors.stone, fontSize: 14),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  // ── Map zone ──────────────────────────────────────────────────────────────

  Widget _buildMapZone() {
    return Stack(
      children: [
        SizedBox(
          height: 240,
          child: FlutterMap(
            options: const MapOptions(
              initialCenter: LatLng(27.0, 30.5),
              initialZoom: 5.8,
              interactionOptions: InteractionOptions(
                flags: InteractiveFlag.pinchZoom |
                    InteractiveFlag.doubleTapZoom |
                    InteractiveFlag.scrollWheelZoom,
              ),
            ),
            children: [
              TileLayer(
                urlTemplate:
                    'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png',
                subdomains: const ['a', 'b', 'c', 'd'],
                userAgentPackageName: 'com.voyo.mapsandbox',
              ),
              if (_pois.isNotEmpty)
                MarkerLayer(
                  markers: _pois.map((poi) {
                    final color = poi.isHiddenGem
                        ? VoyoColors.discovery
                        : VoyoColors.expedition;
                    return Marker(
                      point: LatLng(poi.latitude, poi.longitude),
                      width: 26,
                      height: 26,
                      child: GestureDetector(
                        onTap: () => _showPoiSheet(poi),
                        child: Container(
                          width: 22,
                          height: 22,
                          decoration: BoxDecoration(
                            color: color,
                            shape: BoxShape.circle,
                            border:
                                Border.all(color: Colors.white, width: 2.5),
                            boxShadow: [
                              BoxShadow(
                                color: color.withValues(alpha: 0.35),
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
            ],
          ),
        ),
        // Bottom gradient fade
        Positioned(
          bottom: 0, left: 0, right: 0,
          child: Container(
            height: 70,
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
                colors: [Colors.transparent, VoyoColors.page],
              ),
            ),
          ),
        ),
        // Full map button
        Positioned(
          top: 12, right: 12,
          child: GestureDetector(
            onTap: () => Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => const MapScreen()),
            ),
            child: Container(
              padding:
                  const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              decoration: BoxDecoration(
                color: VoyoColors.paper,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: VoyoColors.smoke),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: 0.06),
                    blurRadius: 6,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Icon(Icons.fullscreen,
                      size: 14, color: VoyoColors.stone),
                  const SizedBox(width: 4),
                  Text('Full Map',
                      style: GoogleFonts.instrumentSans(
                          fontSize: 12,
                          fontWeight: FontWeight.w500,
                          color: VoyoColors.stone)),
                ],
              ),
            ),
          ),
        ),
        // POI count badge
        if (_pois.isNotEmpty)
          Positioned(
            top: 12, left: 12,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
              decoration: BoxDecoration(
                color: VoyoColors.paper,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: VoyoColors.smoke),
              ),
              child: Text(
                '${_pois.length} places',
                style: GoogleFonts.instrumentSans(
                    fontSize: 11,
                    fontWeight: FontWeight.w500,
                    color: VoyoColors.stone),
              ),
            ),
          ),
      ],
    );
  }

  // ── Day Briefing Card ─────────────────────────────────────────────────────

  // ── Category row ──────────────────────────────────────────────────────────

  Widget _buildCategoryRow() {
    return SizedBox(
      height: 44,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        itemCount: _categories.length,
        separatorBuilder: (_, __) => const SizedBox(width: 8),
        itemBuilder: (_, i) {
          final cat = _categories[i];
          final isSelected = cat == _selectedCategory;
          return GestureDetector(
            onTap: () => setState(() => _selectedCategory = cat),
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 150),
              padding:
                  const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              decoration: BoxDecoration(
                color: isSelected
                    ? VoyoColors.expedition
                    : VoyoColors.paper,
                borderRadius: BorderRadius.circular(20),
                border: Border.all(
                  color: isSelected
                      ? VoyoColors.expedition
                      : VoyoColors.smoke,
                ),
              ),
              child: Text(
                cat,
                style: GoogleFonts.instrumentSans(
                  fontSize: 13,
                  fontWeight: FontWeight.w500,
                  color: isSelected ? Colors.white : VoyoColors.stone,
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  // ── Discover section ──────────────────────────────────────────────────────

  Widget _buildDiscoverSection() {
    final pois = _filteredPois;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 20, 16, 4),
          child: Text('Discover Egypt',
              style: GoogleFonts.fraunces(
                  fontSize: 24, color: VoyoColors.ink)),
        ),
        if (_usingFallback)
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 0, 16, 10),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(Icons.info_outline,
                        size: 13, color: VoyoColors.caution),
                    const SizedBox(width: 5),
                    Expanded(
                      child: Text(
                        _poisError != null
                            ? 'DB error: $_poisError'
                            : 'Showing sample data — run the seed SQL in Supabase to see real places.',
                        style: GoogleFonts.instrumentSans(
                            fontSize: 11, color: VoyoColors.caution),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        if (_loadingPois)
          const Padding(
            padding: EdgeInsets.symmetric(vertical: 40),
            child: Center(
              child: CircularProgressIndicator(
                  color: VoyoColors.expedition, strokeWidth: 2),
            ),
          )
        else if (pois.isEmpty)
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 8, 16, 16),
            child: Text(
              'No places in this category yet.',
              style: GoogleFonts.fraunces(
                  fontSize: 16,
                  fontStyle: FontStyle.italic,
                  color: VoyoColors.stone),
            ),
          )
        else
          SizedBox(
            height: 215,
            child: ListView.separated(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(horizontal: 16),
              itemCount: pois.length,
              separatorBuilder: (_, __) => const SizedBox(width: 12),
              itemBuilder: (_, i) => _buildPoiCard(pois[i]),
            ),
          ),
      ],
    );
  }

  Widget _buildPoiCard(Poi poi) {
    final subtitle = _poiSubtitle(poi);
    return GestureDetector(
      onTap: () => _showPoiSheet(poi),
      child: Container(
        width: 148,
        decoration: BoxDecoration(
          color: VoyoColors.paper,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: VoyoColors.smoke),
          boxShadow: [
            BoxShadow(
                color: Colors.black.withValues(alpha: 0.05),
                blurRadius: 8,
                offset: const Offset(0, 2)),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Stack(
              children: [
                Container(
                  height: 108,
                  decoration: BoxDecoration(
                    borderRadius: const BorderRadius.vertical(
                        top: Radius.circular(16)),
                    gradient: _categoryGradient(poi.category),
                  ),
                ),
                if (poi.isHiddenGem)
                  Positioned(
                    top: 8, right: 8,
                    child: _hiddenGemBadge(),
                  ),
                if (poi.isVerified)
                  Positioned(
                    bottom: 8, left: 8,
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 6, vertical: 2),
                      decoration: BoxDecoration(
                        color: VoyoColors.verified.withValues(alpha: 0.9),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Text('✓ Verified',
                          style: GoogleFonts.instrumentSans(
                              fontSize: 9,
                              fontWeight: FontWeight.w600,
                              color: Colors.white)),
                    ),
                  ),
              ],
            ),
            Padding(
              padding: const EdgeInsets.fromLTRB(10, 8, 10, 2),
              child: Text(poi.name,
                  style: GoogleFonts.fraunces(
                      fontSize: 14, color: VoyoColors.ink, height: 1.3),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis),
            ),
            Padding(
              padding: const EdgeInsets.fromLTRB(10, 0, 10, 6),
              child: Text(subtitle,
                  style: GoogleFonts.instrumentSans(
                      fontSize: 10, color: VoyoColors.stone),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis),
            ),
            if (poi.averageRating != null)
              Padding(
                padding: const EdgeInsets.fromLTRB(10, 0, 10, 10),
                child: _miniRatingBar(poi.averageRating!),
              ),
          ],
        ),
      ),
    );
  }

  // ── Hidden gems strip ─────────────────────────────────────────────────────

  Widget _buildHiddenGemsStrip() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 12, 16, 12),
          child: Row(
            children: [
              Container(
                width: 8, height: 8,
                decoration: const BoxDecoration(
                    color: VoyoColors.discovery, shape: BoxShape.circle),
              ),
              const SizedBox(width: 8),
              Text('Hidden Gems',
                  style: GoogleFonts.fraunces(
                      fontSize: 20,
                      fontStyle: FontStyle.italic,
                      color: VoyoColors.discoveryAccessible)),
            ],
          ),
        ),
        ..._hiddenGems.map(_buildGemRow),
      ],
    );
  }

  Widget _buildGemRow(Poi poi) {
    return GestureDetector(
      onTap: () => _showPoiSheet(poi),
      child: Container(
        margin: const EdgeInsets.fromLTRB(16, 0, 16, 10),
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: VoyoColors.paper,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: const Color(0x288860D4)),
        ),
        child: Row(
          children: [
            Container(
              width: 42, height: 42,
              decoration: BoxDecoration(
                gradient: _categoryGradient(poi.category),
                borderRadius: BorderRadius.circular(10),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(poi.name,
                      style: GoogleFonts.fraunces(
                          fontSize: 15, color: VoyoColors.ink)),
                  Text(_poiSubtitle(poi),
                      style: GoogleFonts.instrumentSans(
                          fontSize: 11, color: VoyoColors.stone)),
                ],
              ),
            ),
            if (poi.averageRating != null)
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text(
                    poi.averageRating!.toStringAsFixed(1),
                    style: GoogleFonts.jetBrainsMono(
                        fontSize: 13,
                        fontWeight: FontWeight.w700,
                        color: VoyoColors.terra),
                  ),
                  Text('/ 5.0',
                      style: GoogleFonts.instrumentSans(
                          fontSize: 9, color: VoyoColors.stone)),
                ],
              ),
          ],
        ),
      ),
    );
  }

  // ── POI Sheet ─────────────────────────────────────────────────────────────

  void _showPoiSheet(Poi poi) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => _PoiSheet(
        poi: poi,
        onAskCleo: () {
          Navigator.pop(context);
          widget.onSwitchToCleo?.call();
        },
      ),
    );
  }

  // ── Profile sidebar ───────────────────────────────────────────────────────

  Widget _buildSidebar(double topPadding) {
    final initial =
        (_userName?.isNotEmpty == true) ? _userName![0].toUpperCase() : 'V';
    return SizedBox(
      width: 300,
      height: double.infinity,
      child: Material(
        color: VoyoColors.paper,
        child: SafeArea(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Padding(
                padding: const EdgeInsets.fromLTRB(20, 16, 12, 0),
                child: Row(
                  children: [
                    Text('Profile',
                        style: GoogleFonts.fraunces(
                            fontSize: 22,
                            fontStyle: FontStyle.italic,
                            color: VoyoColors.ink)),
                    const Spacer(),
                    GestureDetector(
                      onTap: () => setState(() => _profileOpen = false),
                      child: Container(
                        width: 32, height: 32,
                        decoration: BoxDecoration(
                          color: VoyoColors.vellum,
                          shape: BoxShape.circle,
                          border: Border.all(color: VoyoColors.smoke),
                        ),
                        child: const Icon(Icons.close,
                            size: 16, color: VoyoColors.stone),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 20),
                child: Row(
                  children: [
                    Container(
                      width: 52, height: 52,
                      decoration: const BoxDecoration(
                          color: Color(0x1AD45028), shape: BoxShape.circle),
                      child: Center(
                        child: Text(initial,
                            style: GoogleFonts.fraunces(
                                fontSize: 22,
                                fontWeight: FontWeight.w600,
                                color: VoyoColors.expedition)),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(_userName ?? 'Explorer',
                              style: GoogleFonts.instrumentSans(
                                  fontSize: 15,
                                  fontWeight: FontWeight.w600,
                                  color: VoyoColors.ink)),
                          if (_userEmail != null)
                            Text(_userEmail!,
                                style: GoogleFonts.instrumentSans(
                                    fontSize: 12, color: VoyoColors.stone),
                                overflow: TextOverflow.ellipsis),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),
              Divider(color: VoyoColors.smoke, height: 1),
              const SizedBox(height: 8),
              ..._sidebarItems.map((item) =>
                  _sidebarTile(item.$1, item.$2, item.$3)),
              const Spacer(),
              Divider(color: VoyoColors.smoke, height: 1),
              ListTile(
                leading: const Icon(Icons.logout,
                    color: VoyoColors.expedition, size: 20),
                title: Text('Sign Out',
                    style: GoogleFonts.instrumentSans(
                        fontSize: 14,
                        fontWeight: FontWeight.w500,
                        color: VoyoColors.expedition)),
                onTap: _signOut,
              ),
              const SizedBox(height: 8),
            ],
          ),
        ),
      ),
    );
  }

  static const _sidebarItems = [
    (Icons.person_outline, 'Personal Info', 'Name, home country'),
    (Icons.tune_outlined, 'Travel Preferences', 'Pace, budget, interests'),
    (Icons.accessibility_new_outlined, 'Mobility & Accessibility',
        'Mobility needs'),
  ];

  void _openSidebarItem(String title) {
    setState(() => _profileOpen = false);
    Future.delayed(const Duration(milliseconds: 250), () {
      if (!mounted) return;
      switch (title) {
        case 'Personal Info':
          showModalBottomSheet(
            context: context,
            isScrollControlled: true,
            backgroundColor: Colors.transparent,
            builder: (_) => PersonalInfoSheet(onSaved: () {
              // Refresh name in sidebar after save
              _supabase
                  .from('user_profiles')
                  .select('full_name')
                  .eq('user_id', _supabase.auth.currentUser!.id)
                  .maybeSingle()
                  .then((p) {
                if (mounted) {
                  setState(() =>
                      _userName = (p as Map?)?['full_name'] as String?);
                }
              });
            }),
          );
        case 'Travel Preferences':
          showModalBottomSheet(
            context: context,
            isScrollControlled: true,
            backgroundColor: Colors.transparent,
            builder: (_) => const TravelPreferencesSheet(),
          );
        case 'Mobility & Accessibility':
          showModalBottomSheet(
            context: context,
            isScrollControlled: true,
            backgroundColor: Colors.transparent,
            builder: (_) => const MobilitySheet(),
          );
      }
    });
  }

  Widget _sidebarTile(IconData icon, String title, String subtitle) {
    return ListTile(
      leading: Icon(icon, color: VoyoColors.stone, size: 20),
      title: Text(title,
          style: GoogleFonts.instrumentSans(
              fontSize: 14,
              fontWeight: FontWeight.w500,
              color: VoyoColors.ink)),
      subtitle: Text(subtitle,
          style: GoogleFonts.instrumentSans(
              fontSize: 11, color: VoyoColors.stone)),
      trailing: const Icon(Icons.chevron_right,
          color: VoyoColors.smoke, size: 18),
      onTap: () => _openSidebarItem(title),
    );
  }

  Future<void> _signOut() async {
    setState(() => _profileOpen = false);
    await _supabase.auth.signOut();
  }

  // ── Notification panel ────────────────────────────────────────────────────

  void _showNotificationPanel() {
    showModalBottomSheet(
      context: context,
      backgroundColor: VoyoColors.paper,
      shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (_) => Padding(
        padding: const EdgeInsets.fromLTRB(20, 16, 20, 32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 36, height: 4,
              decoration: BoxDecoration(
                  color: VoyoColors.smoke,
                  borderRadius: BorderRadius.circular(2)),
            ),
            const SizedBox(height: 16),
            Align(
              alignment: Alignment.centerLeft,
              child: Text('Notifications',
                  style: GoogleFonts.fraunces(
                      fontSize: 22,
                      fontStyle: FontStyle.italic,
                      color: VoyoColors.ink)),
            ),
            const SizedBox(height: 24),
            const Icon(Icons.notifications_none_outlined,
                size: 48, color: VoyoColors.smoke),
            const SizedBox(height: 12),
            Text('You\'re all caught up.',
                style: GoogleFonts.fraunces(
                    fontSize: 18,
                    fontStyle: FontStyle.italic,
                    color: VoyoColors.stone)),
            const SizedBox(height: 6),
            Text('Trip reminders and CLEO updates will appear here.',
                style: GoogleFonts.instrumentSans(
                    fontSize: 13, color: VoyoColors.stone),
                textAlign: TextAlign.center),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }

  // ── Helpers ───────────────────────────────────────────────────────────────

  String _poiSubtitle(Poi poi) {
    final parts = <String>[];
    if (poi.category != null) {
      parts.add(_categoryLabel(poi.category!));
    }
    if (poi.city != null) parts.add(poi.city!);
    return parts.join(' · ');
  }

  String _categoryLabel(String cat) {
    return switch (cat) {
      'historical' => 'Historical Site',
      'cultural' => 'Cultural',
      'natural' => 'Nature',
      'entertainment' => 'Entertainment',
      'religious' => 'Religious Site',
      'shopping' => 'Shopping',
      'dining' => 'Dining',
      'accommodation' => 'Accommodation',
      _ => cat[0].toUpperCase() + cat.substring(1),
    };
  }

  Widget _hiddenGemBadge() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 3),
      decoration: BoxDecoration(
          color: VoyoColors.discovery,
          borderRadius: BorderRadius.circular(10)),
      child: Text('Hidden Gem',
          style: GoogleFonts.instrumentSans(
              fontSize: 9,
              fontWeight: FontWeight.w600,
              color: Colors.white)),
    );
  }

  Widget _miniRatingBar(double rating) {
    final pct = (rating / 5.0).clamp(0.0, 1.0);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text('Rating',
                style: GoogleFonts.instrumentSans(
                    fontSize: 9, color: VoyoColors.stone)),
            Text('${rating.toStringAsFixed(1)}/5',
                style: GoogleFonts.jetBrainsMono(
                    fontSize: 9,
                    fontWeight: FontWeight.w700,
                    color: VoyoColors.terra)),
          ],
        ),
        const SizedBox(height: 3),
        ClipRRect(
          borderRadius: BorderRadius.circular(3),
          child: LinearProgressIndicator(
            value: pct,
            backgroundColor: VoyoColors.smoke,
            valueColor:
                const AlwaysStoppedAnimation(VoyoColors.terra),
            minHeight: 4,
          ),
        ),
      ],
    );
  }

  LinearGradient _categoryGradient(String? category) {
    return switch (category) {
      'historical' || 'religious' => const LinearGradient(
          colors: [Color(0xFF3D2B1F), Color(0xFFC4622A)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight),
      'natural' => const LinearGradient(
          colors: [Color(0xFF1A3A2A), Color(0xFF2A7A50)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight),
      'cultural' || 'entertainment' => const LinearGradient(
          colors: [Color(0xFF1A2C40), Color(0xFF1C72B4)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight),
      'dining' || 'shopping' => const LinearGradient(
          colors: [Color(0xFF1A2A1A), Color(0xFF2A5A3A)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight),
      _ => const LinearGradient(
          colors: [Color(0xFF2C1A2E), Color(0xFF6040B0)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight),
    };
  }
}

// ---------------------------------------------------------------------------
// POI Info Bottom Sheet
// ---------------------------------------------------------------------------

class _PoiSheet extends StatelessWidget {
  final Poi poi;
  final VoidCallback onAskCleo;

  const _PoiSheet({required this.poi, required this.onAskCleo});

  @override
  Widget build(BuildContext context) {
    final subtitle = _sub();
    return DraggableScrollableSheet(
      initialChildSize: 0.72,
      minChildSize: 0.4,
      maxChildSize: 0.93,
      builder: (_, controller) => Container(
        decoration: const BoxDecoration(
          color: VoyoColors.paper,
          borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
        ),
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.only(top: 12, bottom: 4),
              child: Container(
                width: 36, height: 4,
                decoration: BoxDecoration(
                    color: VoyoColors.smoke,
                    borderRadius: BorderRadius.circular(2)),
              ),
            ),
            Expanded(
              child: ListView(
                controller: controller,
                padding: const EdgeInsets.fromLTRB(20, 8, 20, 100),
                children: [
                  // Gradient image placeholder
                  Stack(
                    children: [
                      Container(
                        height: 180,
                        decoration: BoxDecoration(
                          borderRadius: BorderRadius.circular(14),
                          gradient: _gradient(),
                        ),
                      ),
                      if (poi.isHiddenGem)
                        Positioned(
                          top: 10, right: 10,
                          child: Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 10, vertical: 4),
                            decoration: BoxDecoration(
                                color: VoyoColors.discovery,
                                borderRadius: BorderRadius.circular(12)),
                            child: Text('Hidden Gem',
                                style: GoogleFonts.instrumentSans(
                                    fontSize: 11,
                                    fontWeight: FontWeight.w600,
                                    color: Colors.white)),
                          ),
                        ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  // Name + verified
                  Text(poi.name,
                      style: GoogleFonts.fraunces(
                          fontSize: 26,
                          fontStyle: FontStyle.italic,
                          color: VoyoColors.ink)),
                  const SizedBox(height: 4),
                  Row(
                    children: [
                      Expanded(
                        child: Text(subtitle,
                            style: GoogleFonts.instrumentSans(
                                fontSize: 13, color: VoyoColors.stone)),
                      ),
                      if (poi.isVerified)
                        Text('✓ Ground Truth Verified',
                            style: GoogleFonts.instrumentSans(
                                fontSize: 11,
                                fontWeight: FontWeight.w600,
                                color: VoyoColors.verified)),
                    ],
                  ),
                  const SizedBox(height: 16),

                  // Confirmed details
                  Text('Confirmed Details',
                      style: GoogleFonts.fraunces(
                          fontSize: 16,
                          fontStyle: FontStyle.italic,
                          color: VoyoColors.ink)),
                  const SizedBox(height: 10),

                  // Ticket price
                  if (poi.ticketPrice != null)
                    _detailRow(
                      Icons.confirmation_number_outlined,
                      'Entry Fee',
                      '${poi.ticketPrice!.toStringAsFixed(0)} ${poi.currency ?? 'EGP'}',
                    ),

                  // Opening hours
                  if (poi.openingHours != null && poi.openingHours!.isNotEmpty)
                    _openingHoursRow(poi.openingHours!),

                  // Visit duration
                  if (poi.averageVisitDuration != null)
                    _detailRow(
                      Icons.schedule_outlined,
                      'Avg. Visit',
                      _formatDuration(poi.averageVisitDuration!),
                    ),

                  // Rating
                  if (poi.averageRating != null)
                    _detailRow(
                      Icons.star_outline,
                      'Rating',
                      '${poi.averageRating!.toStringAsFixed(1)} / 5.0'
                          '${poi.totalReviews != null ? ' (${poi.totalReviews} reviews)' : ''}',
                    ),

                  // Phone
                  if (poi.phoneNumber != null)
                    _detailRow(
                        Icons.phone_outlined, 'Phone', poi.phoneNumber!),

                  // Website
                  if (poi.websiteUrl != null)
                    _detailRow(
                        Icons.language_outlined, 'Website', poi.websiteUrl!),

                  const SizedBox(height: 16),

                  // Historical significance
                  if (poi.historicalSignificance != null) ...[
                    Text('Historical Significance',
                        style: GoogleFonts.fraunces(
                            fontSize: 16,
                            fontStyle: FontStyle.italic,
                            color: VoyoColors.ink)),
                    const SizedBox(height: 8),
                    Text(poi.historicalSignificance!,
                        style: GoogleFonts.instrumentSans(
                            fontSize: 13,
                            color: VoyoColors.stone,
                            height: 1.6)),
                    const SizedBox(height: 16),
                  ],

                  // Cleo's Take
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const CleoOwl(size: 32),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Container(
                          padding: const EdgeInsets.only(left: 12),
                          decoration: const BoxDecoration(
                            border: Border(
                                left: BorderSide(
                                    color: VoyoColors.sky, width: 3)),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('Cleo\'s Take',
                                  style: GoogleFonts.instrumentSans(
                                      fontSize: 10,
                                      fontWeight: FontWeight.w600,
                                      color: VoyoColors.sky,
                                      letterSpacing: 0.3)),
                              const SizedBox(height: 4),
                              Text(
                                'Before 9am is a completely different world from after 11am.',
                                style: GoogleFonts.fraunces(
                                    fontSize: 15,
                                    fontStyle: FontStyle.italic,
                                    color: VoyoColors.ink,
                                    height: 1.5),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                'The tour groups arrive mid-morning and the energy changes entirely. Get there early for the real experience.',
                                style: GoogleFonts.instrumentSans(
                                    fontSize: 13,
                                    color: VoyoColors.stone,
                                    height: 1.6),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            // Sticky footer
            Container(
              padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
              decoration: const BoxDecoration(
                color: VoyoColors.paper,
                border: Border(top: BorderSide(color: VoyoColors.smoke)),
              ),
              child: Row(
                children: [
                  Expanded(
                    child: FilledButton(
                      onPressed: () => Navigator.pop(context),
                      style: FilledButton.styleFrom(
                        backgroundColor: VoyoColors.terra,
                        shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(14)),
                        padding:
                            const EdgeInsets.symmetric(vertical: 14),
                      ),
                      child: Text('+ Add to Itinerary',
                          style: GoogleFonts.instrumentSans(
                              fontSize: 14,
                              fontWeight: FontWeight.w600,
                              color: Colors.white)),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: OutlinedButton(
                      onPressed: onAskCleo,
                      style: OutlinedButton.styleFrom(
                        side: const BorderSide(
                            color: VoyoColors.sky, width: 2),
                        shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(14)),
                        padding:
                            const EdgeInsets.symmetric(vertical: 14),
                      ),
                      child: Text('Ask Cleo',
                          style: GoogleFonts.instrumentSans(
                              fontSize: 14,
                              fontWeight: FontWeight.w600,
                              color: VoyoColors.sky)),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _detailRow(IconData icon, String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, size: 16, color: VoyoColors.stone),
          const SizedBox(width: 8),
          Text('$label  ',
              style: GoogleFonts.instrumentSans(
                  fontSize: 12,
                  fontWeight: FontWeight.w500,
                  color: VoyoColors.stone)),
          Expanded(
            child: Text(value,
                style: GoogleFonts.jetBrainsMono(
                    fontSize: 12,
                    color: VoyoColors.ink)),
          ),
        ],
      ),
    );
  }

  Widget _openingHoursRow(Map<String, dynamic> hours) {
    final today = _todayKey();
    final todayHours = hours[today] as String?;
    final display = todayHours ?? 'See details';
    return _detailRow(
        Icons.access_time_outlined, 'Today', display);
  }

  String _todayKey() {
    const days = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday'];
    return days[DateTime.now().weekday - 1];
  }

  String _formatDuration(int minutes) {
    if (minutes < 60) return '$minutes min';
    final h = minutes ~/ 60;
    final m = minutes % 60;
    return m == 0 ? '${h}h' : '${h}h ${m}m';
  }

  String _sub() {
    final parts = <String>[];
    if (poi.category != null) {
      parts.add(switch (poi.category!) {
        'historical' => 'Historical Site',
        'cultural' => 'Cultural',
        'natural' => 'Nature',
        'entertainment' => 'Entertainment',
        'religious' => 'Religious Site',
        'shopping' => 'Shopping',
        'dining' => 'Dining',
        _ => poi.category![0].toUpperCase() + poi.category!.substring(1),
      });
    }
    if (poi.city != null) parts.add(poi.city!);
    return parts.join(' · ');
  }

  LinearGradient _gradient() {
    return switch (poi.category) {
      'historical' || 'religious' => const LinearGradient(
          colors: [Color(0xFF3D2B1F), Color(0xFFC4622A)],
          begin: Alignment.topLeft, end: Alignment.bottomRight),
      'natural' => const LinearGradient(
          colors: [Color(0xFF1A3A2A), Color(0xFF2A7A50)],
          begin: Alignment.topLeft, end: Alignment.bottomRight),
      'cultural' || 'entertainment' => const LinearGradient(
          colors: [Color(0xFF1A2C40), Color(0xFF1C72B4)],
          begin: Alignment.topLeft, end: Alignment.bottomRight),
      'dining' || 'shopping' => const LinearGradient(
          colors: [Color(0xFF1A2A1A), Color(0xFF2A5A3A)],
          begin: Alignment.topLeft, end: Alignment.bottomRight),
      _ => const LinearGradient(
          colors: [Color(0xFF2C1A2E), Color(0xFF6040B0)],
          begin: Alignment.topLeft, end: Alignment.bottomRight),
    };
  }
}

// ---------------------------------------------------------------------------
// Search Overlay
// ---------------------------------------------------------------------------

class _SearchOverlay extends StatefulWidget {
  final SupabaseService service;
  final void Function(Poi) onSelect;

  const _SearchOverlay({required this.service, required this.onSelect});

  @override
  State<_SearchOverlay> createState() => _SearchOverlayState();
}

class _SearchOverlayState extends State<_SearchOverlay> {
  final _ctrl = TextEditingController();
  List<Poi> _results = [];
  bool _searching = false;

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  Future<void> _onChanged(String q) async {
    final query = q.trim();
    if (query.isEmpty) {
      setState(() { _results = []; _searching = false; });
      return;
    }
    setState(() => _searching = true);
    final results = await widget.service.searchPois(query);
    if (mounted) setState(() { _results = results; _searching = false; });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: VoyoColors.page,
      body: SafeArea(
        child: Column(
          children: [
            Container(
              color: VoyoColors.paper,
              padding: const EdgeInsets.fromLTRB(12, 12, 12, 12),
              child: Row(
                children: [
                  GestureDetector(
                    onTap: () => Navigator.pop(context),
                    child: const Padding(
                      padding: EdgeInsets.only(right: 10),
                      child: Icon(Icons.arrow_back,
                          color: VoyoColors.ink, size: 22),
                    ),
                  ),
                  Expanded(
                    child: TextField(
                      controller: _ctrl,
                      autofocus: true,
                      onChanged: _onChanged,
                      style: GoogleFonts.instrumentSans(
                          color: VoyoColors.ink, fontSize: 15),
                      decoration: InputDecoration(
                        hintText: 'Search places, landmarks…',
                        hintStyle: GoogleFonts.instrumentSans(
                            color: VoyoColors.stone, fontSize: 15),
                        filled: true,
                        fillColor: VoyoColors.vellum,
                        contentPadding: const EdgeInsets.symmetric(
                            horizontal: 16, vertical: 12),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(22),
                          borderSide: BorderSide.none,
                        ),
                        enabledBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(22),
                          borderSide: BorderSide.none,
                        ),
                        focusedBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(22),
                          borderSide: BorderSide.none,
                        ),
                        suffixIcon: _ctrl.text.isNotEmpty
                            ? GestureDetector(
                                onTap: () {
                                  _ctrl.clear();
                                  _onChanged('');
                                },
                                child: const Icon(Icons.close,
                                    color: VoyoColors.stone, size: 18),
                              )
                            : null,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            Divider(color: VoyoColors.smoke, height: 1),
            Expanded(
              child: _searching
                  ? const Center(
                      child: CircularProgressIndicator(
                          color: VoyoColors.expedition, strokeWidth: 2))
                  : _ctrl.text.isEmpty
                      ? Center(
                          child: Text('Type to search Egyptian landmarks',
                              style: GoogleFonts.instrumentSans(
                                  fontSize: 13, color: VoyoColors.stone)))
                      : _results.isEmpty
                          ? Center(
                              child: Column(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  const Icon(Icons.search_off,
                                      size: 40, color: VoyoColors.smoke),
                                  const SizedBox(height: 12),
                                  Text('Nothing quite matches.',
                                      style: GoogleFonts.fraunces(
                                          fontSize: 18,
                                          fontStyle: FontStyle.italic,
                                          color: VoyoColors.stone)),
                                  const SizedBox(height: 4),
                                  Text(
                                      'Try different words, or ask Cleo directly.',
                                      style: GoogleFonts.instrumentSans(
                                          fontSize: 13,
                                          color: VoyoColors.stone)),
                                ],
                              ),
                            )
                          : ListView.separated(
                              padding:
                                  const EdgeInsets.symmetric(vertical: 8),
                              itemCount: _results.length,
                              separatorBuilder: (_, __) =>
                                  Divider(color: VoyoColors.smoke, height: 1),
                              itemBuilder: (_, i) {
                                final poi = _results[i];
                                final subtitle = [
                                  if (poi.category != null) poi.category,
                                  if (poi.city != null) poi.city,
                                ].join(' · ');
                                return ListTile(
                                  leading: Container(
                                    width: 40, height: 40,
                                    decoration: BoxDecoration(
                                      borderRadius:
                                          BorderRadius.circular(10),
                                      gradient: _cardGradient(poi.category),
                                    ),
                                    child: poi.isHiddenGem
                                        ? const Center(
                                            child: Icon(Icons.auto_awesome,
                                                color: Colors.white,
                                                size: 16))
                                        : null,
                                  ),
                                  title: Text(poi.name,
                                      style: GoogleFonts.fraunces(
                                          fontSize: 15,
                                          color: VoyoColors.ink)),
                                  subtitle: Text(subtitle,
                                      style: GoogleFonts.instrumentSans(
                                          fontSize: 12,
                                          color: VoyoColors.stone)),
                                  trailing: poi.isHiddenGem
                                      ? Container(
                                          padding: const EdgeInsets.symmetric(
                                              horizontal: 7, vertical: 3),
                                          decoration: BoxDecoration(
                                              color: VoyoColors.discovery,
                                              borderRadius:
                                                  BorderRadius.circular(8)),
                                          child: Text('Gem',
                                              style: GoogleFonts.instrumentSans(
                                                  fontSize: 9,
                                                  fontWeight: FontWeight.w600,
                                                  color: Colors.white)),
                                        )
                                      : const Icon(Icons.chevron_right,
                                          color: VoyoColors.smoke),
                                  onTap: () {
                                    Navigator.pop(context);
                                    widget.onSelect(poi);
                                  },
                                );
                              },
                            ),
            ),
          ],
        ),
      ),
    );
  }

  LinearGradient _cardGradient(String? category) {
    return switch (category) {
      'historical' || 'religious' => const LinearGradient(
          colors: [Color(0xFF3D2B1F), Color(0xFFC4622A)]),
      'natural' => const LinearGradient(
          colors: [Color(0xFF1A3A2A), Color(0xFF2A7A50)]),
      'cultural' || 'entertainment' => const LinearGradient(
          colors: [Color(0xFF1A2C40), Color(0xFF1C72B4)]),
      _ => const LinearGradient(colors: [Color(0xFF2C1A2E), Color(0xFF6040B0)]),
    };
  }
}
