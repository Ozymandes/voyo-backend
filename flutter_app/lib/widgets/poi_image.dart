import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../models/poi.dart';
import '../theme.dart';

/// Visual style for a POI category: fallback gradient, accent colour, icon, label.
///
/// This is the single source of truth for how a category looks across the app,
/// so cards, sheets, and search results stay consistent. (Sprint item 9.)
class PoiCategoryStyle {
  final LinearGradient gradient;
  final Color accent;
  final IconData icon;
  final String label;

  const PoiCategoryStyle(
    this.gradient,
    this.accent,
    this.icon,
    this.label,
  );
}

/// Resolves a raw category string (e.g. `'historical'`) into its visual style.
PoiCategoryStyle poiCategoryStyle(String? category) {
  switch (category?.toLowerCase()) {
    case 'historical':
      return const PoiCategoryStyle(
        LinearGradient(
          colors: [Color(0xFF3D2B1F), Color(0xFFC4622A)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        VoyoColors.terra,
        Icons.account_balance_outlined,
        'Historical',
      );
    case 'religious':
      return const PoiCategoryStyle(
        LinearGradient(
          colors: [Color(0xFF3D2B1F), Color(0xFFD48A10)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        VoyoColors.caution,
        Icons.church_outlined,
        'Religious',
      );
    case 'natural':
      return const PoiCategoryStyle(
        LinearGradient(
          colors: [Color(0xFF1A3A2A), Color(0xFF2A7A50)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        VoyoColors.verified,
        Icons.terrain_outlined,
        'Nature',
      );
    case 'cultural':
      return const PoiCategoryStyle(
        LinearGradient(
          colors: [Color(0xFF1A2C40), Color(0xFF1C72B4)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        VoyoColors.sky,
        Icons.palette_outlined,
        'Cultural',
      );
    case 'entertainment':
      return const PoiCategoryStyle(
        LinearGradient(
          colors: [Color(0xFF1A2C40), Color(0xFF8860D4)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        VoyoColors.discovery,
        Icons.local_activity_outlined,
        'Entertainment',
      );
    case 'dining':
      return const PoiCategoryStyle(
        LinearGradient(
          colors: [Color(0xFF2A1F12), Color(0xFFD48A10)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        VoyoColors.caution,
        Icons.restaurant_outlined,
        'Dining',
      );
    case 'shopping':
      return const PoiCategoryStyle(
        LinearGradient(
          colors: [Color(0xFF2C1A2E), Color(0xFF8860D4)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        VoyoColors.discovery,
        Icons.shopping_bag_outlined,
        'Shopping',
      );
    case 'accommodation':
      return const PoiCategoryStyle(
        LinearGradient(
          colors: [Color(0xFF1A2C40), Color(0xFF1C72B4)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        VoyoColors.sky,
        Icons.hotel_outlined,
        'Stay',
      );
    default:
      final label = (category == null || category.isEmpty)
          ? 'Place'
          : category[0].toUpperCase() + category.substring(1);
      return PoiCategoryStyle(
        const LinearGradient(
          colors: [Color(0xFF2C1A2E), Color(0xFF6040B0)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        VoyoColors.discovery,
        Icons.place_outlined,
        label,
      );
  }
}

/// HTTP headers sent with every image request. Wikimedia Commons (which
/// hosts our POI and CLEO-response images) rate-limits requests that lack a
/// descriptive User-Agent — without this, image loads fail with HTTP 429.
/// See Wikimedia's User-Agent policy.
const voyoImageHttpHeaders = {
  'User-Agent': 'VOYO-App/1.0 (Egypt travel guide; thesis project)',
};

/// Whether [url] points at an image format Flutter's bundled codec can't
/// decode (SVG needs `flutter_svg`, which we don't bundle). Used to skip
/// doomed network requests that throw "Invalid image data".
bool isUndecodableImage(String url) {
  final path = url.toLowerCase().split('?').first;
  return path.endsWith('.svg');
}

/// A POI image that always resolves to something visible.
///
/// Priority: `poi.imageUrls` (Supabase / Wikimedia) -> category gradient with a
/// faint icon watermark. Network errors and null URLs never throw; they fall
/// back to the gradient, so the UI stays stable when the backend or a CDN is
/// unreachable. (Sprint item 5 wiring + item 9 robustness.)
class PoiImage extends StatelessWidget {
  final Poi poi;
  final double? width;
  final double height;
  final BorderRadius? borderRadius;
  final BoxFit fit;

  /// Show a faint category icon over the gradient fallback.
  final bool showFallbackIcon;

  const PoiImage({
    super.key,
    required this.poi,
    required this.height,
    this.width,
    this.borderRadius,
    this.fit = BoxFit.cover,
    this.showFallbackIcon = true,
  });

  @override
  Widget build(BuildContext context) {
    final style = poiCategoryStyle(poi.category);
    final url = (poi.imageUrls != null && poi.imageUrls!.isNotEmpty)
        ? poi.imageUrls!.first
        : null;
    final hasNoCanonicalImage = url == null;
    // If there IS a url, check whether it's an undecodable format (SVG etc);
    // if there's no url at all, skip the check (we're already in fallback).
    final undecodable = !hasNoCanonicalImage && isUndecodableImage(url);

    Widget content;
    if (hasNoCanonicalImage || undecodable) {
      // Genuine data gap — this POI has no verified image anywhere in the
      // canonical DB. Surfaced honestly as the category gradient + a faint
      // "no photo" chip so it reads as intentional, not a broken card.
      content = _GradientFallback(
          style: style, showIcon: showFallbackIcon, showNoPhotoChip: true);
    } else {
      content = Image.network(
        url,
        fit: fit,
        headers: voyoImageHttpHeaders,
        filterQuality: FilterQuality.high,
        loadingBuilder: (context, image, progress) {
          if (progress == null) return image;
          return _ShimmerBox(borderRadius: borderRadius);
        },
        // Image existed in the DB but failed to load (CDN 403/404/timeout).
        // We log the gap so it's traceable, then show the gradient WITHOUT
        // the "no photo" chip — because a photo DOES exist, it just didn't
        // load this time. The chip is reserved for genuine gaps only.
        errorBuilder: (_, __, ___) {
          debugPrint('VOYO image-load failed for POI ${poi.id} "${poi.name}": '
              '$url  (transient CDN error or stale URL — not a missing image)');
          return _GradientFallback(
              style: style, showIcon: showFallbackIcon, showNoPhotoChip: false);
        },
      );
    }

    // When a parent provides tight constraints (e.g. Positioned.fill inside a
    // card, or StackFit.expand in a hero), they override `height`/`width` and
    // the image fills the available space.
    return ClipRRect(
      borderRadius: borderRadius ?? BorderRadius.zero,
      child: SizedBox(
        width: width ?? double.infinity,
        height: height,
        child: content,
      ),
    );
  }
}

class _GradientFallback extends StatelessWidget {
  final PoiCategoryStyle style;
  final bool showIcon;
  final bool showNoPhotoChip;

  const _GradientFallback({
    required this.style,
    required this.showIcon,
    this.showNoPhotoChip = false,
  });

  @override
  Widget build(BuildContext context) {
    return DecoratedBox(
      decoration: BoxDecoration(gradient: style.gradient),
      child: Stack(
        alignment: Alignment.center,
        children: [
          if (showIcon)
            Icon(
              style.icon,
              size: 36,
              color: Colors.white.withValues(alpha: 0.30),
            ),
          if (showNoPhotoChip)
            Positioned(
              bottom: 6,
              left: 6,
              child: Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: Colors.black.withValues(alpha: 0.45),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  'no photo',
                  style: GoogleFonts.instrumentSans(
                    fontSize: 8.5,
                    fontWeight: FontWeight.w600,
                    color: Colors.white.withValues(alpha: 0.85),
                    letterSpacing: 0.3,
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
}

/// Lightweight loading placeholder built on the animation framework, so it
/// needs no extra dependency (and stays hot-reload safe).
class _ShimmerBox extends StatefulWidget {
  final BorderRadius? borderRadius;
  const _ShimmerBox({this.borderRadius});

  @override
  State<_ShimmerBox> createState() => _ShimmerBoxState();
}

class _ShimmerBoxState extends State<_ShimmerBox>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller = AnimationController(
    vsync: this,
    duration: const Duration(milliseconds: 1200),
  )..repeat();

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, _) {
        final t = _controller.value;
        return Container(
          color: VoyoColors.vellum,
          child: DecoratedBox(
            decoration: BoxDecoration(
              borderRadius: widget.borderRadius,
              gradient: LinearGradient(
                begin: Alignment(-1.0 + 2 * t, 0),
                end: Alignment(1.0 + 2 * t, 0),
                colors: [
                  VoyoColors.smoke,
                  VoyoColors.paper,
                  VoyoColors.smoke,
                ],
              ),
            ),
          ),
        );
      },
    );
  }
}
