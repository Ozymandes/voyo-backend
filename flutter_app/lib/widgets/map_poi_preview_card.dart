import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../models/poi.dart';
import '../theme.dart';
import 'poi_image.dart';

/// Compact map-preview card shown when a user taps a POI geotag on Map Explore.
///
/// Single source of truth: this reads the SAME canonical enriched `Poi` record
/// the Planner and Explore cards use (see `SupabaseService._poiColumns`), so a
/// given POI ID resolves to identical title, image, category, rating, ticket,
/// and description data everywhere. Only the *presentation* differs — this is
/// the truncated, action-forward preview; `PoiDetailSheet` is the full modal.
///
/// Layout (per the Map-Explore card spec):
///   image (with category + verified badges) · name · city·rating · entry pill
///   · 1–2 line truncated enriched description · [View details] [Add to trip]
class MapPoiPreviewCard extends StatelessWidget {
  final Poi poi;
  final VoidCallback onViewDetails;
  final VoidCallback onAddToTrip;
  /// Itinerary context for this card. When the POI is part of the active
  /// itinerary (tapped via a stop marker), passing [itineraryDay] +
  /// [itineraryStop] renders a compact "Day N · Stop M" badge — restoring
  /// the label the pre-revamp card showed. Both default to null (plain map
  /// POI tap), in which case no itinerary badge is shown.
  final int? itineraryDay;
  final int? itineraryStop;

  const MapPoiPreviewCard({
    super.key,
    required this.poi,
    required this.onViewDetails,
    required this.onAddToTrip,
    this.itineraryDay,
    this.itineraryStop,
  });

  /// Whether the itinerary-stop badge should render. Requires BOTH fields —
  /// a partial day-only or stop-only label would be ambiguous, so we omit.
  bool get _showItineraryLabel =>
      itineraryDay != null && itineraryStop != null;

  @override
  Widget build(BuildContext context) {
    final style = poiCategoryStyle(poi.category);
    final desc = _previewDescription(poi);

    return Padding(
      padding: const EdgeInsets.fromLTRB(12, 0, 12, 12),
      child: Material(
        color: VoyoColors.paper,
        borderRadius: BorderRadius.circular(20),
        clipBehavior: Clip.antiAlias,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // ── Image + overlaid badges ───────────────────────────────────
            SizedBox(
              height: 150,
              child: Stack(
                fit: StackFit.expand,
                children: [
                  PoiImage(
                    poi: poi,
                    height: 150,
                    borderRadius: BorderRadius.zero,
                  ),
                  // Top legibility scrim for the badges only (kept light so
                  // the photograph still carries the card).
                  Positioned(
                    top: 0,
                    left: 0,
                    right: 0,
                    height: 56,
                    child: IgnorePointer(
                      child: DecoratedBox(
                        decoration: BoxDecoration(
                          gradient: LinearGradient(
                            begin: Alignment.topCenter,
                            end: Alignment.bottomCenter,
                            colors: [
                              VoyoColors.ink.withValues(alpha: 0.45),
                              Colors.transparent,
                            ],
                          ),
                        ),
                      ),
                    ),
                  ),
                  Positioned(
                    top: 10,
                    left: 10,
                    right: 10,
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Flexible(
                          child: _Badge(
                            color: style.accent.withValues(alpha: 0.92),
                            icon: style.icon,
                            label: style.label,
                          ),
                        ),
                        if (poi.isVerified)
                          const _Badge(
                            color: VoyoColors.verified,
                            icon: Icons.verified_rounded,
                            label: 'Verified',
                          ),
                      ],
                    ),
                  ),
                ],
              ),
            ),

            // ── Text body ─────────────────────────────────────────────────
            Padding(
              padding: const EdgeInsets.fromLTRB(14, 12, 14, 4),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  // #1: itinerary stop label. Restored here on the revamped
                  // card — the pre-revamp stop sheet showed "Day 6 · Stop 2"
                  // and the rewrite dropped it. Rendered compactly above the
                  // title so the canonical image/description/rating layout
                  // below is unchanged. Hidden for plain map-POI taps.
                  if (_showItineraryLabel) ...[
                    _ItineraryStopLabel(
                      day: itineraryDay!,
                      stop: itineraryStop!,
                    ),
                    const SizedBox(height: 6),
                  ],
                  Text(
                    poi.name,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: GoogleFonts.fraunces(
                      fontSize: 18,
                      fontWeight: FontWeight.w600,
                      height: 1.2,
                      color: VoyoColors.ink,
                    ),
                  ),
                  const SizedBox(height: 6),
                  _MetaRow(poi: poi),
                  const SizedBox(height: 8),
                  // Truncated enriched description — same field priority as
                  // PoiDetailSheet (narrative → description), preview-length.
                  Text(
                    desc,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: GoogleFonts.instrumentSans(
                      fontSize: 13,
                      height: 1.45,
                      color: VoyoColors.stone,
                    ),
                  ),
                ],
              ),
            ),

            // ── Actions ───────────────────────────────────────────────────
            Padding(
              padding: const EdgeInsets.fromLTRB(14, 10, 14, 14),
              child: Row(
                children: [
                  Expanded(
                    child: FilledButton.icon(
                      onPressed: onViewDetails,
                      icon: const Icon(Icons.read_more_rounded, size: 18),
                      label: const Text('View details'),
                      style: FilledButton.styleFrom(
                        backgroundColor: VoyoColors.ink,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 12),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                        textStyle: GoogleFonts.instrumentSans(
                          fontSize: 14,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: onAddToTrip,
                      icon: const Icon(
                        Icons.add_location_alt_outlined,
                        size: 18,
                      ),
                      label: const Text('Add to trip'),
                      style: OutlinedButton.styleFrom(
                        foregroundColor: VoyoColors.ink,
                        side: BorderSide(color: VoyoColors.smoke),
                        padding: const EdgeInsets.symmetric(vertical: 12),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                        textStyle: GoogleFonts.instrumentSans(
                          fontSize: 14,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
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
}

// ── Helpers ────────────────────────────────────────────────────────────────

/// Compact "Day N · Stop M" label for the itinerary-stop variant of the
/// preview card. Uses the VOYO expedtion accent so it reads as a planner-
/// originated tag, not a category badge. Sits above the title; the category
/// badge stays on the image (its canonical home).
class _ItineraryStopLabel extends StatelessWidget {
  final int day;
  final int stop;
  const _ItineraryStopLabel({required this.day, required this.stop});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: VoyoColors.expedition.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(6),
      ),
      child: Text(
        'Day $day · Stop $stop',
        style: GoogleFonts.instrumentSans(
          fontSize: 11,
          fontWeight: FontWeight.w700,
          letterSpacing: 0.3,
          color: VoyoColors.expedition,
        ),
      ),
    );
  }
}

/// One-line location + rating + entry summary, VOYO-style.
class _MetaRow extends StatelessWidget {
  final Poi poi;
  const _MetaRow({required this.poi});

  @override
  Widget build(BuildContext context) {
    final children = <Widget>[];
    if (poi.city != null) {
      children.addAll([
        Icon(Icons.place_outlined, size: 14, color: VoyoColors.stone),
        const SizedBox(width: 3),
        Flexible(
          child: Text(
            poi.city!,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: GoogleFonts.instrumentSans(
              fontSize: 12,
              color: VoyoColors.stone,
            ),
          ),
        ),
      ]);
    }
    if (poi.averageRating != null) {
      if (children.isNotEmpty) children.add(_dot());
      children.addAll([
        Icon(Icons.star_rounded, size: 15, color: VoyoColors.caution),
        const SizedBox(width: 2),
        Text(
          poi.averageRating!.toStringAsFixed(1),
          style: GoogleFonts.jetBrainsMono(
            fontSize: 12,
            fontWeight: FontWeight.w700,
            color: VoyoColors.ink,
          ),
        ),
      ]);
    }
    final entry = _entrySummary(poi);
    if (entry != null) {
      if (children.isNotEmpty) children.add(_dot());
      children.addAll([
        Icon(
          Icons.confirmation_number_outlined,
          size: 14,
          color: VoyoColors.stone,
        ),
        const SizedBox(width: 3),
        Text(
          entry,
          style: GoogleFonts.instrumentSans(
            fontSize: 12,
            color: VoyoColors.stone,
          ),
        ),
      ]);
    }
    if (children.isEmpty) return const SizedBox.shrink();
    return Wrap(
      crossAxisAlignment: WrapCrossAlignment.center,
      children: children,
    );
  }

  Widget _dot() => Padding(
    padding: const EdgeInsets.symmetric(horizontal: 6),
    child: Text(
      '·',
      style: GoogleFonts.instrumentSans(fontSize: 12, color: VoyoColors.smoke),
    ),
  );
}

class _Badge extends StatelessWidget {
  final Color color;
  final IconData icon;
  final String label;
  const _Badge({required this.color, required this.icon, required this.label});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 11, color: Colors.white),
          const SizedBox(width: 4),
          Text(
            label,
            style: GoogleFonts.instrumentSans(
              fontSize: 10,
              fontWeight: FontWeight.w600,
              color: Colors.white,
            ),
          ),
        ],
      ),
    );
  }
}

/// Truncated enriched description for the preview.
///
/// Priority mirrors `PoiDetailSheet`: enriched `narrative` first, then legacy
/// `description`. When neither exists we surface an honest "Details coming
/// soon" AND log the POI as a data gap (per the spec's audit requirement) so
/// missing enriched copy is visible in dev logs rather than silently faked.
String _previewDescription(Poi poi) {
  const max = 165;
  final n = poi.narrative?.trim();
  if (n != null && n.isNotEmpty) return _truncate(n, max);
  final d = poi.description?.trim();
  if (d != null && d.isNotEmpty) return _truncate(d, max);
  debugPrint(
    '[VOYO data-gap] POI ${poi.id} "${poi.name}" has no enriched narrative '
    'or description for map preview.',
  );
  return 'Details coming soon.';
}

String _truncate(String s, int max) {
  if (s.length <= max) return s;
  var cut = s.lastIndexOf(' ', max);
  if (cut <= 0) cut = max;
  return '${s.substring(0, cut).trim()}…';
}

/// Compact single-line entry summary, consistent with the dual-tier logic in
/// `PoiDetailSheet` but flattened for the preview row. Returns null when no
/// pricing is known (the meta row then simply omits the entry chip).
String? _entrySummary(Poi poi) {
  final tp = poi.ticketPrices;
  final hasTp = tp != null && tp['egyptian'] is num && tp['foreigner'] is num;
  if (hasTp) {
    final e = (tp['egyptian'] as num).toDouble();
    final f = (tp['foreigner'] as num).toDouble();
    if (e == 0 && f == 0) return 'Free entry';
    // Show the foreigner tier in the preview (most relevant to visitors);
    // the full sheet breaks out both.
    return 'from ${f.toStringAsFixed(0)} EGP';
  }
  if (poi.ticketPrice != null) {
    if (poi.ticketPrice == 0) return 'Free entry';
    return '${poi.ticketPrice!.toStringAsFixed(0)} ${poi.currency ?? 'EGP'}';
  }
  return null; // unknown — omit rather than imply free
}
