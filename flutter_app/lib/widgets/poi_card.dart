import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../models/poi.dart';
import '../theme.dart';
import 'poi_image.dart';

/// The redesigned POI card for horizontal scrolls (Explore home + discover).
///
/// Image-forward, like the detail panels in github.com/yorkeccak/history: the
/// photograph carries the card, a tonal scrim keeps text legible on any image,
/// and the essential facts (category, location, rating, gem/verified) sit on
/// the surface. 8-point grid throughout. (Sprint item 4.)
class PoiCard extends StatelessWidget {
  final Poi poi;
  final VoidCallback? onTap;
  final double width;
  final double height;

  const PoiCard({
    super.key,
    required this.poi,
    this.onTap,
    this.width = 168,
    this.height = 224,
  });

  @override
  Widget build(BuildContext context) {
    final style = poiCategoryStyle(poi.category);

    return GestureDetector(
      onTap: onTap,
      child: SizedBox(
        width: width,
        height: height,
        child: DecoratedBox(
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: VoyoColors.smoke),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.06),
                blurRadius: 12,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(20),
            child: Stack(
              children: [
                // Photograph fills the card.
                Positioned.fill(
                  child: PoiImage(
                    poi: poi,
                    height: height,
                    borderRadius: BorderRadius.zero,
                  ),
                ),
                // Bottom legibility scrim.
                Positioned(
                  left: 0,
                  right: 0,
                  bottom: 0,
                  height: 136,
                  child: IgnorePointer(
                    child: DecoratedBox(
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          begin: Alignment.topCenter,
                          end: Alignment.bottomCenter,
                          colors: [
                            Colors.transparent,
                            VoyoColors.ink.withValues(alpha: 0.55),
                            VoyoColors.ink.withValues(alpha: 0.82),
                          ],
                          stops: const [0.0, 0.55, 1.0],
                        ),
                      ),
                    ),
                  ),
                ),
                // Top chips: category + (optional) hidden-gem badge.
                Positioned(
                  top: 10,
                  left: 10,
                  right: 10,
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Flexible(
                        fit: FlexFit.loose,
                        child: _CategoryChip(
                          accent: style.accent,
                          label: style.label,
                          icon: style.icon,
                        ),
                      ),
                      if (poi.isHiddenGem) const _GemBadge()
                      else const SizedBox.shrink(),
                    ],
                  ),
                ),
                // Bottom content: name + location/rating row.
                Positioned(
                  left: 12,
                  right: 12,
                  bottom: 12,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        poi.name,
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                        style: GoogleFonts.fraunces(
                          fontSize: 16,
                          height: 1.2,
                          fontWeight: FontWeight.w500,
                          color: Colors.white,
                        ),
                      ),
                      const SizedBox(height: 6),
                      Row(
                        children: [
                          if (poi.city != null) ...[
                            Icon(
                              Icons.place_outlined,
                              size: 12,
                              color: Colors.white.withValues(alpha: 0.82),
                            ),
                            const SizedBox(width: 3),
                            Flexible(
                              child: Text(
                                poi.city!,
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                                style: GoogleFonts.instrumentSans(
                                  fontSize: 11,
                                  color:
                                      Colors.white.withValues(alpha: 0.88),
                                ),
                              ),
                            ),
                          ],
                          if (poi.averageRating != null) ...[
                            if (poi.city != null) const SizedBox(width: 8),
                            Icon(
                              Icons.star_rounded,
                              size: 13,
                              color: VoyoColors.caution,
                            ),
                            const SizedBox(width: 2),
                            Text(
                              poi.averageRating!.toStringAsFixed(1),
                              style: GoogleFonts.jetBrainsMono(
                                fontSize: 11,
                                fontWeight: FontWeight.w700,
                                color: Colors.white,
                              ),
                            ),
                          ],
                          if (poi.isVerified) ...[
                            const SizedBox(width: 6),
                            Icon(
                              Icons.verified_rounded,
                              size: 13,
                              color: VoyoColors.verified,
                            ),
                          ],
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _CategoryChip extends StatelessWidget {
  final Color accent;
  final String label;
  final IconData icon;

  const _CategoryChip({
    required this.accent,
    required this.label,
    required this.icon,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: accent.withValues(alpha: 0.92),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 11, color: Colors.white),
          const SizedBox(width: 4),
          Flexible(
            child: Text(
              label,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: GoogleFonts.instrumentSans(
                fontSize: 10,
                fontWeight: FontWeight.w600,
                color: Colors.white,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _GemBadge extends StatelessWidget {
  const _GemBadge();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: VoyoColors.discovery,
        borderRadius: BorderRadius.circular(8),
        boxShadow: [
          BoxShadow(
            color: VoyoColors.discovery.withValues(alpha: 0.40),
            blurRadius: 6,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.auto_awesome, size: 11, color: Colors.white),
          const SizedBox(width: 4),
          Text(
            'Gem',
            style: GoogleFonts.instrumentSans(
              fontSize: 10,
              fontWeight: FontWeight.w700,
              color: Colors.white,
            ),
          ),
        ],
      ),
    );
  }
}
