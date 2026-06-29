import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:url_launcher/url_launcher.dart';
import '../models/poi.dart';
import '../theme.dart';
import 'poi_image.dart';

/// The redesigned POI detail sheet — the rich "tap a place" panel.
///
/// Echoes the immersive detail panels of github.com/yorkeccak/history: a
/// full-bleed hero photograph with a tonal scrim carrying the title, clean
/// quick-fact pills, then progressive disclosure of description, significance,
/// and a data-derived "Good to know" block. No fabricated content and no
/// side-stripe accents. (Sprint items 4 + 9.)
class PoiDetailSheet extends StatelessWidget {
  final Poi poi;

  /// Opens CLEO chat preloaded with context about this POI. When null, the
  /// "Ask Cleo" action is hidden (e.g. on the full-map screen).
  final VoidCallback? onAskCleo;

  /// Adds the POI to the current itinerary. Defaults to dismissing the sheet,
  /// matching the previous behaviour.
  final VoidCallback? onAddToTrip;

  const PoiDetailSheet({
    super.key,
    required this.poi,
    this.onAskCleo,
    this.onAddToTrip,
  });

  @override
  Widget build(BuildContext context) {
    return DraggableScrollableSheet(
      initialChildSize: 0.9,
      minChildSize: 0.5,
      maxChildSize: 0.96,
      builder: (context, scrollController) {
        return Container(
          decoration: const BoxDecoration(
            color: VoyoColors.paper,
            borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
          ),
          child: ClipRRect(
            borderRadius:
                const BorderRadius.vertical(top: Radius.circular(24)),
            child: Stack(
              children: [
                CustomScrollView(
                  controller: scrollController,
                  slivers: [
                    SliverToBoxAdapter(child: _Hero(poi: poi)),
                    SliverPadding(
                      padding: const EdgeInsets.fromLTRB(20, 16, 20, 96),
                      sliver: SliverList(
                        delegate: SliverChildListDelegate(_body(context)),
                      ),
                    ),
                  ],
                ),
                Positioned(
                  top: 12,
                  right: 12,
                  child: _CloseButton(onTap: () => Navigator.of(context).pop()),
                ),
                Positioned(
                  left: 0,
                  right: 0,
                  bottom: 0,
                  child: _Footer(
                    poi: poi,
                    onAskCleo: onAskCleo,
                    onAddToTrip: onAddToTrip,
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  List<Widget> _body(BuildContext context) {
    // ── DIAGNOSTIC GUARD (temporary): the body renders grey on Windows
    // release. Release-mode ErrorWidget is a grey box, so a build exception
    // in the body sliver produces exactly that symptom. This guard catches
    // it, logs the full stack to the console, and renders a visible error
    // chip so we can read the cause from a screenshot/log instead of a
    // featureless grey rectangle. Remove once the throw site is fixed.
    //
    // NOTE: uses print() not debugPrint() so logs survive in --release.
    try {
      final built = _bodyInner(context);
      print(
        'VOYO-PDIAG poi=${poi.id} "${poi.name}" bodySections=${built.length} '
        'narrative=${poi.narrative?.length ?? 'null'} '
        'desc=${poi.description?.length ?? 'null'} '
        'sig=${poi.historicalSignificance?.length ?? 'null'} '
        'tips=${poi.travelTips?.length ?? 'null'} '
        'tags=${poi.tags?.length ?? 'null'} '
        'imgs=${poi.imageUrls?.length ?? 'null'}',
      );
      return built;
    } catch (e, st) {
      print('VOYO-PDIAG ===== _body THREW =====');
      print('VOYO-PDIAG poi=${poi.id} "${poi.name}"');
      print('VOYO-PDIAG exception: $e');
      print('VOYO-PDIAG stack:\n$st');
      return [
        Padding(
          padding: const EdgeInsets.all(20),
          child: Text(
            'PDIAG body-build threw:\n$e\n\n$st',
            style: const TextStyle(color: Colors.red, fontSize: 11),
          ),
        ),
      ];
    }
  }

  List<Widget> _bodyInner(BuildContext context) {
    final children = <Widget>[];

    // Quick facts (only the ones we actually have data for).
    final facts = _factPills();
    if (facts.isNotEmpty) {
      children.add(Row(children: facts));
    }

    // Prefer LLM-enriched narrative; fall back to raw description.
    final aboutText = (poi.narrative?.trim().isNotEmpty == true)
        ? poi.narrative!
        : poi.description;
    if (aboutText != null && aboutText.trim().isNotEmpty) {
      children.addAll(_section('About', aboutText));
    }

    if (poi.historicalSignificance != null &&
        poi.historicalSignificance!.trim().isNotEmpty) {
      children.addAll(
          _section(_significanceLabel(), poi.historicalSignificance!));
    }

    final tips = _goodToKnowTips();
    if (tips.isNotEmpty) {
      children.add(const SizedBox(height: 20));
      children.add(_label('Good to know'));
      children.add(const SizedBox(height: 10));
      children.add(_TipsCard(tips: tips));
    }

    if (poi.tags != null && poi.tags!.isNotEmpty) {
      children.add(const SizedBox(height: 20));
      children.add(_label('Tags'));
      children.add(const SizedBox(height: 10));
      children.add(_TagWrap(tags: poi.tags!));
    }

    // Contact information (website and phone) - only show when present
    final contactRows = _contactRows(context);
    if (contactRows.isNotEmpty) {
      children.add(const SizedBox(height: 20));
      children.add(_label('Contact'));
      children.add(const SizedBox(height: 10));
      children.addAll(contactRows);
    }

    children.add(const SizedBox(height: 8));
    return children;
  }

  /// Builds the quick-fact pills as [Expanded, gap, Expanded, gap, Expanded]...
  List<Widget> _factPills() {
    final pills = <Widget>[];
    if (poi.averageVisitDuration != null) {
      pills.add(_FactPill(
        icon: Icons.schedule_outlined,
        value: _formatDuration(poi.averageVisitDuration!),
        label: 'Visit',
      ));
    }
    // Dual-tier pricing: when the structured ticket_prices field is
    // populated, show both Egyptian and foreigner rates. Fall back to the
    // single legacy ticket_price otherwise. When neither is known, render an
    // explicit 'Not available' pill rather than silently omitting entry info
    // (so missing data is never confused with free entry).
    //
    // Free logic: egyptian==0 AND foreigner==0 means genuinely free.
    // Asymmetric zeros (one tier free, one paid) render the real numbers.
    final tp = poi.ticketPrices;
    final hasTp = tp != null &&
        tp['egyptian'] is num &&
        tp['foreigner'] is num;
    if (hasTp) {
      final e = (tp['egyptian'] as num).toDouble();
      final f = (tp['foreigner'] as num).toDouble();
      final bothFree = e == 0 && f == 0;
      pills.add(_FactPill(
        icon: Icons.confirmation_number_outlined,
        value: bothFree
            ? 'Free'
            : 'Egyptian ${e.toStringAsFixed(0)} EGP\nForeigner ${f.toStringAsFixed(0)} EGP',
        label: 'Entry',
        // maxLines 4 (not 2): each pill shares ~1/3 of the row width, so at
        // the dual-tier font size 'Egyptian 100 EGP' can wrap across two
        // lines and push 'Foreigner 1000 EGP' past the old maxLines:2 ceiling,
        // where ellipsis clipped it entirely. 4 guarantees both tiers render.
        valueMaxLines: bothFree ? 1 : 4,
        valueFontSize: bothFree ? 16 : 13,
      ));
    } else if (poi.ticketPrice != null) {
      final free = poi.ticketPrice == 0;
      pills.add(_FactPill(
        icon: Icons.confirmation_number_outlined,
        value: free ? 'Free' : '${poi.ticketPrice!.toStringAsFixed(0)} ${poi.currency ?? 'EGP'}',
        label: 'Entry',
      ));
    } else {
      // Neither structured nor legacy price known. Honest 'Not available' so
      // the absence of data isn't misread as free entry. (Many POIs are
      // genuinely free, but we can't assert that without a source.)
      pills.add(_FactPill(
        icon: Icons.confirmation_number_outlined,
        value: 'Not available',
        label: 'Entry',
        valueMaxLines: 1,
        valueFontSize: 13,
      ));
    }
    if (poi.averageRating != null) {
      pills.add(_FactPill(
        icon: Icons.star_rounded,
        value: poi.averageRating!.toStringAsFixed(1),
        label: poi.totalReviews != null
            ? '${_compact(poi.totalReviews!)} reviews'
            : 'Rating',
      ));
    }

    // Interleave Expanded pills with gaps so they share the row evenly.
    final out = <Widget>[];
    for (var i = 0; i < pills.length; i++) {
      out.add(Expanded(child: pills[i]));
      if (i < pills.length - 1) out.add(const SizedBox(width: 8));
    }
    return out;
  }

  /// Honest, data-derived practical notes — replaces a previously hardcoded
  /// "Cleo's Take" anecdote that was identical for every POI. Expert guidance
  /// from the enriched `travel_tips` field is shown first (highest value);
  /// mechanical data-derived tips follow.
  List<(IconData, String)> _goodToKnowTips() {
    final tips = <(IconData, String)>[];
    // Enrichment-sourced expert tips (take up to 4 so the card stays scannable).
    if (poi.travelTips != null && poi.travelTips!.isNotEmpty) {
      for (final t in poi.travelTips!.take(4)) {
        if (t.trim().isNotEmpty) {
          tips.add((Icons.tips_and_updates_outlined, t.trim()));
        }
      }
    }
    if (poi.averageVisitDuration != null) {
      tips.add((
        Icons.schedule_outlined,
        'Most visitors spend about ${_formatDuration(poi.averageVisitDuration!)} here.'
      ));
    }
    final today = _todayHours(poi.openingHours);
    if (today != null) {
      tips.add((Icons.access_time_outlined, 'Open today: $today'));
    }
    if (poi.isHiddenGem) {
      tips.add((
        Icons.auto_awesome_outlined,
        'A quieter, lesser-visited spot — often uncrowded.'
      ));
    }
    if (poi.isVerified) {
      tips.add((
        Icons.verified_outlined,
        'Details cross-checked against official sources.'
      ));
    }
    return tips;
  }

  List<Widget> _section(String title, String body) {
    return [
      const SizedBox(height: 20),
      _label(title),
      const SizedBox(height: 8),
      Text(
        body,
        style: GoogleFonts.instrumentSans(
          fontSize: 14,
          color: VoyoColors.stone,
          height: 1.65,
        ),
      ),
    ];
  }

  /// Category-aware label for the significance section, so reefs, mosques
  /// and bazaars no longer read as "Historical Significance".
  String _significanceLabel() {
    switch (poi.category?.toLowerCase()) {
      case 'historical':
        return 'Historical significance';
      case 'natural':
        return 'What makes it special';
      case 'religious':
        return 'Spiritual context';
      case 'cultural':
        return 'Cultural context';
      case 'entertainment':
        return "Why it's worth a visit";
      case 'dining':
      case 'shopping':
        return 'What to expect';
      default:
        return 'Significance';
    }
  }

  Widget _label(String text) {
    return Text(
      text,
      style: GoogleFonts.fraunces(
        fontSize: 16,
        fontStyle: FontStyle.italic,
        color: VoyoColors.ink,
      ),
    );
  }

  /// Builds contact information rows (website and phone).
  /// Returns a list of widgets, only for fields that have non-null values.
  List<Widget> _contactRows(BuildContext context) {
    final rows = <Widget>[];
    
    if (poi.websiteUrl != null) {
      rows.add(_ContactRow(
        icon: Icons.language_outlined,
        label: 'Website',
        value: _shortUrl(poi.websiteUrl!),
        onTap: () async {
          final uri = Uri.parse(poi.websiteUrl!);
          if (await canLaunchUrl(uri)) {
            await launchUrl(uri, mode: LaunchMode.externalApplication);
          }
        },
      ));
      rows.add(const SizedBox(height: 8));
    }
    
    if (poi.phoneNumber != null) {
      rows.add(_ContactRow(
        icon: Icons.phone_outlined,
        label: 'Phone',
        value: poi.phoneNumber!,
        onTap: () async {
          final uri = Uri.parse('tel:${poi.phoneNumber!}');
          if (await canLaunchUrl(uri)) {
            await launchUrl(uri);
          }
        },
      ));
      rows.add(const SizedBox(height: 8));
    }
    
    return rows;
  }

  /// Shortens a URL for display by removing protocol and common prefixes.
  static String _shortUrl(String url) {
    // Remove protocol
    var short = url.replaceFirst(RegExp(r'^https?://'), '');
    // Remove www.
    short = short.replaceFirst(RegExp(r'^www\.'), '');
    // Truncate if still too long
    if (short.length > 28) {
      short = '${short.substring(0, 25)}...';
    }
    return short;
  }

  // ── Helpers ───────────────────────────────────────────────────────────────

  static String _formatDuration(int minutes) {
    if (minutes < 60) return '$minutes min';
    final h = minutes ~/ 60;
    final m = minutes % 60;
    return m == 0 ? '${h}h' : '${h}h ${m}m';
  }

  static String _compact(int n) {
    if (n >= 1000) {
      final k = (n / 1000).toStringAsFixed(n % 1000 == 0 ? 0 : 1);
      return '${k}k';
    }
    return '$n';
  }

  static String? _todayHours(Map<String, dynamic>? hours) {
    if (hours == null || hours.isEmpty) return null;
    
    // Handle legacy weekday_text format: {"weekday_text": ["Monday: 8:00 AM – 6:00 PM", ...]}
    // Google's weekday_text has index 0 = Sunday
    final weekdayText = hours['weekday_text'];
    if (weekdayText is List && weekdayText.isNotEmpty) {
      // Map DateTime weekday (1=Monday, 7=Sunday) to weekday_text index (0=Sunday, 1=Monday, ...)
      final weekday = DateTime.now().weekday;
      final index = weekday == 7 ? 0 : weekday; // Sunday -> 0, Monday -> 1, etc.
      
      if (index >= 0 && index < weekdayText.length) {
        final entry = weekdayText[index];
        if (entry is String && entry.isNotEmpty) {
          // Parse "Day: Hours" format to extract just the hours
          final colonIndex = entry.indexOf(':');
          if (colonIndex != -1 && colonIndex < entry.length - 2) {
            // Check if there's a space after the colon (day name separator)
            if (entry.length > colonIndex + 1 && entry[colonIndex + 1] == ' ') {
              return entry.substring(colonIndex + 2).trim();
            } else {
              // No space, might be hours format like "8:00 AM" (unlikely in this context)
              return entry;
            }
          }
          return entry;
        }
      }
      return null;
    }
    
    // Handle new day-keyed format: {"monday": "8:00 AM – 6:00 PM", ...}
    const days = [
      'monday',
      'tuesday',
      'wednesday',
      'thursday',
      'friday',
      'saturday',
      'sunday',
    ];
    final key = days[DateTime.now().weekday - 1];
    final v = hours[key];
    return v is String && v.isNotEmpty ? v : null;
  }
}

// ---------------------------------------------------------------------------
// Hero
// ---------------------------------------------------------------------------

class _Hero extends StatefulWidget {
  final Poi poi;
  const _Hero({required this.poi});

  @override
  State<_Hero> createState() => _HeroState();
}

class _HeroState extends State<_Hero> {
  int _page = 0;

  @override
  Widget build(BuildContext context) {
    final poi = widget.poi;
    final style = poiCategoryStyle(poi.category);
    final images = (poi.imageUrls ?? const <String>[])
        .where((u) => !isUndecodableImage(u))
        .toList(growable: false);
    final hasCarousel = images.length > 1;

    // Category-tinted scrim: blend the POI's category colour into the ink base
    // so the bottom of the hero carries a hint of the category hue while
    // staying dark enough for the white title to stay legible.
    final categoryColor = style.gradient.colors.last;
    final scrim = Color.lerp(VoyoColors.ink, categoryColor, 0.4)!;

    return SizedBox(
      height: 312,
      width: double.infinity,
      child: Stack(
        fit: StackFit.expand,
        children: [
          // Image layer: horizontal carousel, single image, or gradient
          // fallback (0 images). Top corners stay rounded via the parent
          // ClipRRect.
          if (images.length > 1)
            PageView.builder(
              itemCount: images.length,
              onPageChanged: (i) => setState(() => _page = i),
              itemBuilder: (context, i) => _CarouselImage(
                url: images[i],
                style: style,
              ),
            )
          else if (images.length == 1)
            _CarouselImage(url: images.first, style: style)
          else
            _HeroGradientFallback(style: style),
          // Category-tinted bottom scrim for title legibility.
          Positioned(
            left: 0,
            right: 0,
            bottom: 0,
            height: 196,
            child: IgnorePointer(
              child: DecoratedBox(
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topCenter,
                    end: Alignment.bottomCenter,
                    colors: [
                      Colors.transparent,
                      scrim.withValues(alpha: 0.55),
                      scrim.withValues(alpha: 0.88),
                    ],
                    stops: const [0.0, 0.6, 1.0],
                  ),
                ),
              ),
            ),
          ),
          // Drag handle.
          Positioned(
            top: 10,
            left: 0,
            right: 0,
            child: Center(
              child: Container(
                width: 36,
                height: 4,
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.55),
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
          ),
          // Title block, with page-indicator dots above it when carousel.
          Positioned(
            left: 20,
            right: 20,
            bottom: 20,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                if (hasCarousel) ...[
                  _PageDots(count: images.length, current: _page),
                  const SizedBox(height: 10),
                ],
                Wrap(
                  spacing: 8,
                  runSpacing: 6,
                  children: [
                    _HeroChip(
                      color: style.accent,
                      icon: style.icon,
                      label: style.label,
                    ),
                    if (poi.isVerified)
                      const _HeroChip(
                        color: VoyoColors.verified,
                        icon: Icons.verified_rounded,
                        label: 'Verified',
                      ),
                  ],
                ),
                const SizedBox(height: 10),
                Text(
                  poi.name,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: GoogleFonts.fraunces(
                    fontSize: 28,
                    fontStyle: FontStyle.italic,
                    height: 1.15,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    if (poi.city != null) ...[
                      Icon(
                        Icons.place_outlined,
                        size: 13,
                        color: Colors.white.withValues(alpha: 0.85),
                      ),
                      const SizedBox(width: 4),
                      Flexible(
                        child: Text(
                          poi.city!,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: GoogleFonts.instrumentSans(
                            fontSize: 13,
                            color: Colors.white.withValues(alpha: 0.92),
                          ),
                        ),
                      ),
                    ],
                    if (poi.city != null && poi.averageRating != null)
                      const SizedBox(width: 8),
                    if (poi.averageRating != null) ...[
                      Icon(
                        Icons.star_rounded,
                        size: 14,
                        color: VoyoColors.caution,
                      ),
                      const SizedBox(width: 3),
                      Text(
                        poi.averageRating!.toStringAsFixed(1),
                        style: GoogleFonts.jetBrainsMono(
                          fontSize: 13,
                          fontWeight: FontWeight.w700,
                          color: Colors.white,
                        ),
                      ),
                    ],
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

/// A single network image in the hero carousel. Falls back to the category
/// gradient on load error or while loading, mirroring [PoiImage]'s
/// robustness so the UI never throws on a bad URL.
class _CarouselImage extends StatelessWidget {
  final String url;
  final PoiCategoryStyle style;

  const _CarouselImage({required this.url, required this.style});

  @override
  Widget build(BuildContext context) {
    return Image.network(
      url,
      fit: BoxFit.cover,
      headers: voyoImageHttpHeaders,
      filterQuality: FilterQuality.high,
      loadingBuilder: (context, image, progress) {
        if (progress == null) return image;
        return _HeroGradientFallback(style: style);
      },
      errorBuilder: (_, __, ___) => _HeroGradientFallback(style: style),
    );
  }
}

/// Gradient fallback for the hero (0 images, or an image that failed to
/// load). Mirrors [PoiImage]'s fallback so the empty state stays on-brand.
class _HeroGradientFallback extends StatelessWidget {
  final PoiCategoryStyle style;
  const _HeroGradientFallback({required this.style});

  @override
  Widget build(BuildContext context) {
    return DecoratedBox(
      decoration: BoxDecoration(gradient: style.gradient),
      child: Center(
        child: Icon(
          style.icon,
          size: 36,
          color: Colors.white.withValues(alpha: 0.30),
        ),
      ),
    );
  }
}

/// Expanding-dot page indicator for the hero carousel. Only rendered when
/// more than one image is present.
class _PageDots extends StatelessWidget {
  final int count;
  final int current;
  const _PageDots({required this.count, required this.current});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        for (var i = 0; i < count; i++) ...[
          if (i > 0) const SizedBox(width: 6),
          AnimatedContainer(
            duration: const Duration(milliseconds: 200),
            curve: Curves.easeOutCubic,
            width: i == current ? 16 : 6,
            height: 6,
            decoration: BoxDecoration(
              color: i == current
                  ? Colors.white
                  : Colors.white.withValues(alpha: 0.45),
              borderRadius: BorderRadius.circular(3),
            ),
          ),
        ],
      ],
    );
  }
}

class _HeroChip extends StatelessWidget {
  final Color color;
  final IconData icon;
  final String label;

  const _HeroChip({
    required this.color,
    required this.icon,
    required this.label,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.92),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 12, color: Colors.white),
          const SizedBox(width: 4),
          Text(
            label,
            style: GoogleFonts.instrumentSans(
              fontSize: 11,
              fontWeight: FontWeight.w600,
              color: Colors.white,
            ),
          ),
        ],
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Body pieces
// ---------------------------------------------------------------------------

class _FactPill extends StatelessWidget {
  final IconData icon;
  final String value;
  final String label;
  final int valueMaxLines;
  final double valueFontSize;

  const _FactPill({
    required this.icon,
    required this.value,
    required this.label,
    this.valueMaxLines = 1,
    this.valueFontSize = 16,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
      decoration: BoxDecoration(
        color: VoyoColors.vellum,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: VoyoColors.smoke),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, size: 18, color: VoyoColors.stone),
          const SizedBox(height: 8),
          Text(
            value,
            maxLines: valueMaxLines,
            overflow: TextOverflow.ellipsis,
            style: GoogleFonts.fraunces(
              fontSize: valueFontSize,
              fontWeight: FontWeight.w600,
              color: VoyoColors.ink,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            label,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: GoogleFonts.instrumentSans(
              fontSize: 11,
              color: VoyoColors.stone,
            ),
          ),
        ],
      ),
    );
  }
}

class _TipsCard extends StatelessWidget {
  final List<(IconData, String)> tips;
  const _TipsCard({required this.tips});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: VoyoColors.sky.withValues(alpha: 0.06),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: VoyoColors.sky.withValues(alpha: 0.18)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          for (var i = 0; i < tips.length; i++) ...[
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(tips[i].$1, size: 16, color: VoyoColors.sky),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    tips[i].$2,
                    style: GoogleFonts.instrumentSans(
                      fontSize: 13,
                      color: VoyoColors.ink.withValues(alpha: 0.82),
                      height: 1.5,
                    ),
                  ),
                ),
              ],
            ),
            if (i < tips.length - 1) const SizedBox(height: 10),
          ],
        ],
      ),
    );
  }
}

class _TagWrap extends StatelessWidget {
  final List<String> tags;
  const _TagWrap({required this.tags});

  @override
  Widget build(BuildContext context) {
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: [
        for (final tag in tags.take(12))
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
            decoration: BoxDecoration(
              color: VoyoColors.vellum,
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: VoyoColors.smoke),
            ),
            child: Text(
              tag,
              style: GoogleFonts.instrumentSans(
                fontSize: 11,
                fontWeight: FontWeight.w500,
                color: VoyoColors.stone,
              ),
            ),
          ),
      ],
    );
  }
}

// ---------------------------------------------------------------------------
// Contact row widget
// ---------------------------------------------------------------------------

class _ContactRow extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final VoidCallback onTap;

  const _ContactRow({
    required this.icon,
    required this.label,
    required this.value,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
        decoration: BoxDecoration(
          color: VoyoColors.vellum,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: VoyoColors.smoke),
        ),
        child: Row(
          children: [
            Icon(icon, size: 18, color: VoyoColors.sky),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    label,
                    style: GoogleFonts.instrumentSans(
                      fontSize: 11,
                      color: VoyoColors.stone,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    value,
                    style: GoogleFonts.instrumentSans(
                      fontSize: 14,
                      color: VoyoColors.ink,
                      fontWeight: FontWeight.w600,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            ),
            Icon(
              Icons.chevron_right_rounded,
              size: 20,
              color: VoyoColors.stone.withValues(alpha: 0.6),
            ),
          ],
        ),
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Chrome: close button + footer
// ---------------------------------------------------------------------------

class _CloseButton extends StatelessWidget {
  final VoidCallback onTap;
  const _CloseButton({required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 36,
        height: 36,
        decoration: BoxDecoration(
          color: Colors.white.withValues(alpha: 0.22),
          shape: BoxShape.circle,
          border: Border.all(color: Colors.white.withValues(alpha: 0.35)),
        ),
        child: const Icon(Icons.close_rounded, size: 18, color: Colors.white),
      ),
    );
  }
}

class _Footer extends StatelessWidget {
  final Poi poi;
  final VoidCallback? onAskCleo;
  final VoidCallback? onAddToTrip;

  const _Footer({
    required this.poi,
    required this.onAskCleo,
    required this.onAddToTrip,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 16),
      decoration: BoxDecoration(
        color: VoyoColors.paper,
        border: Border(top: BorderSide(color: VoyoColors.smoke)),
      ),
      child: SafeArea(
        top: false,
        child: Row(
          children: [
            if (onAskCleo != null) ...[
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: onAskCleo,
                  style: OutlinedButton.styleFrom(
                    foregroundColor: VoyoColors.sky,
                    side: const BorderSide(color: VoyoColors.sky, width: 1.5),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(14),
                    ),
                    padding: const EdgeInsets.symmetric(vertical: 14),
                  ),
                  icon: const Icon(Icons.chat_bubble_outline_rounded, size: 18),
                  label: Text(
                    'Ask Cleo',
                    style: GoogleFonts.instrumentSans(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                      color: VoyoColors.sky,
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 10),
            ],
            Expanded(
              child: FilledButton.icon(
                onPressed: () {
                  if (onAddToTrip != null) {
                    onAddToTrip!();
                  } else {
                    Navigator.of(context).pop();
                  }
                },
                style: FilledButton.styleFrom(
                  backgroundColor: VoyoColors.terra,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14),
                  ),
                  padding: const EdgeInsets.symmetric(vertical: 14),
                ),
                icon: const Icon(Icons.add_rounded, size: 18, color: Colors.white),
                label: Text(
                  'Add to Trip',
                  style: GoogleFonts.instrumentSans(
                    fontSize: 14,
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
}
