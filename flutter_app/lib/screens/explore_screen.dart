import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:latlong2/latlong.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../models/poi.dart';
import '../services/recommendation_service.dart';
import '../services/supabase_service.dart';
import '../services/weather_service.dart';
import '../theme.dart';
import '../widgets/add_to_itinerary_sheet.dart';
import '../widgets/poi_card.dart';
import '../widgets/poi_detail_sheet.dart';
import '../widgets/voyo_brand.dart';
import 'map_screen.dart';
import 'chat_screen.dart';
import 'recommendations_screen.dart';
import 'settings_sheets.dart';

// Categories are derived from the data (see _buildCategoryRow) so the row
// never silently drops categories that exist in the DB (it previously missed
// Entertainment + Cultural because it was hardcoded). 'All' and 'Hidden Gems'
// are synthetic and always present.

// Display label -> canonical DB category enum value.
const _categoryEnum = {
  'Historical': 'historical',
  'Cultural': 'cultural',
  'Religious': 'religious',
  'Nature': 'natural',
  'Entertainment': 'entertainment',
  'Dining': 'dining',
  'Shopping': 'shopping',
};

// Human-readable label for a raw category enum value (reverse map).
String? _categoryLabel(String? cat) {
  if (cat == null) return null;
  for (final e in _categoryEnum.entries) {
    if (e.value == cat.toLowerCase()) return e.key;
  }
  return null;
}

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
  String? _poisError;

  // Discovery weather widget (D3/D6): current conditions for the device
  // location (or Cairo fallback). Null = still loading.
  WeatherResult? _weather;

  final _recService = RecommendationService();
  List<Poi> _recommendations = [];

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    final userId = _supabase.auth.currentUser?.id;

    // Load POIs from Supabase. There is intentionally NO mock fallback —
    // stale seed data caused 'Discover Egypt' to show fabricated POIs while
    // 'Your Destinations' showed real enriched ones. On failure we surface an
    // honest error/empty state instead of inventing data.
    try {
      final pois = await _supabaseService.getFeaturedPois(limit: 500);
      if (mounted) {
        setState(() {
          _pois = pois;
          _poisError = null;
          _loadingPois = false;
        });
      }
    } catch (e) {
      debugPrint('ExploreScreen: POI load failed — $e');
      if (mounted) {
        setState(() {
          _pois = [];
          _poisError = e.toString();
          _loadingPois = false;
        });
      }
    }

    // Recommendations power 'Your Destinations'. When signed out the API
    // returns nothing, so we fall back to the already-loaded POIs (same
    // canonical source — no second stale dataset).
    await _loadRecommendations();
    if (_recommendations.isEmpty) _recommendations = _pois;
    if (mounted) setState(() {});

    // Discovery weather widget (D3/D6) — fire-and-forget; failure resolves to
    // an Unavailable result the widget renders gracefully.
    _loadWeather();

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
    final cat = _categoryEnum[_selectedCategory] ?? _selectedCategory.toLowerCase();
    return _pois.where((p) => p.category?.toLowerCase() == cat).toList();
  }

  /// Category chips: always lead with All + Hidden Gems, then every category
  /// that actually has at least one active POI in the loaded data. Derived
  /// from data so we never silently hide Entertainment/Cultural/etc.
  List<String> get _categoryChips {
    final present = <String, int>{};
    for (final p in _pois) {
      final label = _categoryLabel(p.category);
      if (label != null) present[label] = (present[label] ?? 0) + 1;
    }
    final ordered = present.keys.toList()..sort();
    return ['All', ...ordered, 'Hidden Gems'];
  }

  Future<void> _loadRecommendations() async {
    if (!mounted) return;
    final recs = await _recService.getRecommendations(limit: 24);
    if (mounted) setState(() => _recommendations = recs);
  }

  Future<void> _loadWeather() async {
    final w = await WeatherService.instance.getCurrent();
    if (mounted) setState(() => _weather = w);
  }

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
              SliverToBoxAdapter(child: _buildWeatherWidget()),
              SliverToBoxAdapter(child: _buildMapZone()),
              SliverToBoxAdapter(child: _buildCategoryRow()),
              SliverToBoxAdapter(child: _buildDiscoverSection()),
              SliverToBoxAdapter(child: _buildYourDestinations()),
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

  // ── Discovery weather widget (D3/D6) ─────────────────────────────────────
  // Travel-actionable current conditions in VOYO voice. Collapses to a slim
  // skeleton while loading and a graceful note on failure — weather is a
  // nicety, never blocks the rest of the screen.
  Widget _buildWeatherWidget() {
    final w = _weather;
    final body = switch (w) {
      null => Row(children: [
          _weatherIconPlaceholder(),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                    width: 90, height: 12,
                    color: VoyoColors.vellum),
                const SizedBox(height: 6),
                Container(
                    width: 160, height: 10,
                    color: VoyoColors.vellum),
              ],
            ),
          ),
        ]),
      Unavailable() => Row(children: [
          Icon(Icons.cloud_off_outlined,
              size: 20, color: VoyoColors.stone.withValues(alpha: 0.6)),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
                'Weather unavailable — check back later.',
                style: GoogleFonts.instrumentSans(
                    fontSize: 12, color: VoyoColors.stone)),
          ),
        ]),
      CurrentWeather() => _weatherContent(w),
    };

    return Container(
      margin: const EdgeInsets.fromLTRB(16, 4, 16, 8),
      padding: const EdgeInsets.fromLTRB(14, 12, 14, 12),
      decoration: BoxDecoration(
        color: VoyoColors.paper,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: VoyoColors.smoke),
      ),
      child: body,
    );
  }

  Widget _weatherIconPlaceholder() =>
      Container(width: 28, height: 28, decoration: const BoxDecoration(
          color: VoyoColors.vellum, shape: BoxShape.circle));

  Widget _weatherContent(CurrentWeather w) {
    return Row(
      children: [
        Text(_weatherEmoji(w),
            style: const TextStyle(fontSize: 22)),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                '${w.city} now · ${w.tempC}°C · ${_titleCase(w.conditionLabel)}',
                style: GoogleFonts.fraunces(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: VoyoColors.ink),
              ),
              const SizedBox(height: 3),
              Text(
                weatherSuggestion(w),
                style: GoogleFonts.instrumentSans(
                    fontSize: 12, color: VoyoColors.stone, height: 1.4),
              ),
            ],
          ),
        ),
      ],
    );
  }

  String _weatherEmoji(CurrentWeather w) {
    final icon = w.icon;
    // OpenWeather icon codes: 01=clear, 02-04=clouds, 09/10=rain,
    // 11=thunder, 13=snow, 50=mist/dust.
    if (icon.startsWith('01')) return '☀️';
    if (icon.startsWith('02') || icon.startsWith('03')) return '⛅';
    if (icon.startsWith('04')) return '☁️';
    if (icon.startsWith('09') || icon.startsWith('10')) return '🌧️';
    if (icon.startsWith('11')) return '⛈️';
    if (icon.startsWith('13')) return '❄️';
    return '🌫️'; // 50:* mist / dust / haze
  }

  static String _titleCase(String s) {
    if (s.isEmpty) return s;
    return s[0].toUpperCase() + s.substring(1);
  }

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
                  const VoyoWordmark(height: 22),
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
    final chips = _categoryChips;
    return SizedBox(
      height: 44,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        itemCount: chips.length,
        separatorBuilder: (_, __) => const SizedBox(width: 8),
        itemBuilder: (_, i) {
          final cat = chips[i];
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
        if (_loadingPois)
          const Padding(
            padding: EdgeInsets.symmetric(vertical: 40),
            child: Center(
              child: CircularProgressIndicator(
                  color: VoyoColors.expedition, strokeWidth: 2),
            ),
          )
        else if (_poisError != null && _pois.isEmpty)
          // Honest error state: the DB/refresh fetch failed AND we have no
          // cached POIs. We never substitute mock data — the user needs to
          // know the real source is unreachable.
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 8, 16, 16),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(Icons.cloud_off_outlined,
                    size: 16, color: VoyoColors.caution),
                const SizedBox(width: 8),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Couldn\'t load places right now.',
                          style: GoogleFonts.instrumentSans(
                              fontSize: 13,
                              fontWeight: FontWeight.w600,
                              color: VoyoColors.ink)),
                      const SizedBox(height: 4),
                      Text(
                          'Check your connection and pull down to retry.\nDetails: $_poisError',
                          style: GoogleFonts.instrumentSans(
                              fontSize: 11, color: VoyoColors.stone)),
                    ],
                  ),
                ),
                GestureDetector(
                  onTap: _loadData,
                  child: Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                    decoration: BoxDecoration(
                      color: VoyoColors.expedition,
                      borderRadius: BorderRadius.circular(14),
                    ),
                    child: Text('Retry',
                        style: GoogleFonts.instrumentSans(
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                            color: Colors.white)),
                  ),
                ),
              ],
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
            height: 224,
            child: ListView.separated(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(horizontal: 16),
              itemCount: pois.length,
              separatorBuilder: (_, __) => const SizedBox(width: 12),
              itemBuilder: (_, i) => PoiCard(
                poi: pois[i],
                onTap: () => _showPoiSheet(pois[i]),
              ),
            ),
          ),
      ],
    );
  }

  // ── POI Sheet ─────────────────────────────────────────────────────────────

  void _showPoiSheet(Poi poi) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => PoiDetailSheet(
        poi: poi,
        onAskCleo: () {
          Navigator.pop(context);
          openCleoForPoi(context, poi);
        },
        onAddToTrip: () {
          Navigator.pop(context);
          _addPoiToItinerary(poi);
        },
      ),
    );
  }

  Future<void> _addPoiToItinerary(Poi poi) async {
    final userId = _supabase.auth.currentUser?.id;
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
      builder: (_) => AddToItineraryFlow(
        poi: poi,
        service: _supabaseService,
        userId: userId,
      ),
    );
    if (added == true && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        content: Text('${poi.name} added to your itinerary!'),
        backgroundColor: VoyoColors.terra,
        duration: const Duration(seconds: 2),
      ));
    }
  }

  // ── Your Destinations ─────────────────────────────────────────────────────

  Widget _buildYourDestinations() {
    if (_loadingPois) return const SizedBox.shrink();

    // Prefer personalised recs from the API; fall back to loaded POIs.
    final source = _recommendations.isNotEmpty ? _recommendations : _pois;
    if (source.isEmpty) return const SizedBox.shrink();

    final topPicks = source.take(8).toList();
    final historyPicks = source
        .where((p) =>
            p.category == 'historical' ||
            p.category == 'religious' ||
            p.category == 'cultural')
        .take(6)
        .toList();
    final gemPicks = source.where((p) => p.isHiddenGem).take(6).toList();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 24, 16, 4),
          child: Text('Your Destinations',
              style: GoogleFonts.fraunces(fontSize: 24, color: VoyoColors.ink)),
        ),
        _buildRecPanel('Top picks for you', topPicks,
            accent: VoyoColors.expedition),
        if (historyPicks.isNotEmpty)
          _buildRecPanel('Because you love history', historyPicks,
              accent: VoyoColors.terra),
        if (gemPicks.isNotEmpty)
          _buildRecPanel('Hidden gems for you', gemPicks,
              accent: VoyoColors.discovery),
      ],
    );
  }

  Widget _buildRecPanel(String title, List<Poi> pois,
      {Color accent = VoyoColors.expedition}) {
    if (pois.isEmpty) return const SizedBox.shrink();
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
          child: Row(children: [
            Container(
                width: 6,
                height: 6,
                decoration: BoxDecoration(color: accent, shape: BoxShape.circle)),
            const SizedBox(width: 8),
            Text(title,
                style:
                    GoogleFonts.fraunces(fontSize: 16, color: VoyoColors.ink)),
            const Spacer(),
            GestureDetector(
              onTap: () => Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => RecommendationsScreen(
                    title: title,
                    pois: pois,
                    onSwitchToCleo: widget.onSwitchToCleo,
                  ),
                ),
              ),
              child: Text('See more',
                  style: GoogleFonts.instrumentSans(
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                      color: VoyoColors.stone)),
            ),
          ]),
        ),
        SizedBox(
          height: 224,
          child: ListView.separated(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 16),
            itemCount: pois.length,
            separatorBuilder: (_, __) => const SizedBox(width: 12),
            itemBuilder: (_, i) => PoiCard(
              poi: pois[i],
              onTap: () => _showPoiSheet(pois[i]),
            ),
          ),
        ),
      ],
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
                              separatorBuilder: (_, i) =>
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
