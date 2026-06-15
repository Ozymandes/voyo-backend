import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../models/poi.dart';
import '../services/supabase_service.dart';
import '../theme.dart';
import '../widgets/add_to_itinerary_sheet.dart';
import '../widgets/poi_card.dart';
import '../widgets/poi_detail_sheet.dart';

class RecommendationsScreen extends StatefulWidget {
  final String title;
  final List<Poi> pois;
  final VoidCallback? onSwitchToCleo;

  const RecommendationsScreen({
    super.key,
    required this.title,
    required this.pois,
    this.onSwitchToCleo,
  });

  @override
  State<RecommendationsScreen> createState() => _RecommendationsScreenState();
}

class _RecommendationsScreenState extends State<RecommendationsScreen> {
  final _supabase = Supabase.instance.client;
  final _supabaseService = SupabaseService();

  void _showSheet(Poi poi) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => PoiDetailSheet(
        poi: poi,
        onAskCleo: () {
          Navigator.pop(context);
          Navigator.pop(context);
          widget.onSwitchToCleo?.call();
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

  @override
  Widget build(BuildContext context) {
    final top = MediaQuery.of(context).padding.top;
    return Scaffold(
      backgroundColor: VoyoColors.page,
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _Header(top: top, title: widget.title, count: widget.pois.length),
          const Divider(color: VoyoColors.smoke, height: 1),
          Expanded(
            child: GridView.builder(
              padding: const EdgeInsets.all(16),
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 2,
                crossAxisSpacing: 12,
                mainAxisSpacing: 12,
                childAspectRatio: 168 / 224,
              ),
              itemCount: widget.pois.length,
              itemBuilder: (_, i) => PoiCard(
                poi: widget.pois[i],
                onTap: () => _showSheet(widget.pois[i]),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _Header extends StatelessWidget {
  final double top;
  final String title;
  final int count;

  const _Header({required this.top, required this.title, required this.count});

  @override
  Widget build(BuildContext context) {
    return Container(
      color: VoyoColors.paper,
      padding: EdgeInsets.fromLTRB(16, top + 12, 16, 16),
      child: Row(
        children: [
          GestureDetector(
            onTap: () => Navigator.pop(context),
            child: Container(
              width: 36,
              height: 36,
              decoration: BoxDecoration(
                color: VoyoColors.vellum,
                shape: BoxShape.circle,
                border: Border.all(color: VoyoColors.smoke),
              ),
              child: const Icon(Icons.arrow_back,
                  size: 18, color: VoyoColors.ink),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              title,
              style: GoogleFonts.fraunces(
                fontSize: 20,
                fontStyle: FontStyle.italic,
                color: VoyoColors.ink,
              ),
            ),
          ),
          Container(
            padding:
                const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: VoyoColors.vellum,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: VoyoColors.smoke),
            ),
            child: Text(
              '$count places',
              style: GoogleFonts.instrumentSans(
                fontSize: 11,
                fontWeight: FontWeight.w600,
                color: VoyoColors.stone,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
