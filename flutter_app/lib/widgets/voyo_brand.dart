import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';

/// The VOYO wordmark — the typographic logo lockup.
///
/// Rendered from `assets/brand/VOYO_wordmark.svg` so it scales crisply at
/// any size. Use in app bars / headers where the brand name should appear
/// (replaces the prior `Text('VOYO')` placeholder). For square brand-mark
/// only contexts (favicons, tiny chips) use [VoyoBrandmark] instead.
class VoyoWordmark extends StatelessWidget {
  final double height;
  final Color? colorFilter;

  const VoyoWordmark({super.key, this.height = 22, this.colorFilter});

  @override
  Widget build(BuildContext context) {
    return SvgPicture.asset(
      'assets/brand/VOYO_wordmark.svg',
      height: height,
      fit: BoxFit.contain,
      // The SVG ships with its own brand-orange fill; only override when a
      // caller explicitly passes a colorFilter (e.g. for dark backgrounds).
      colorFilter: colorFilter == null
          ? null
          : ColorFilter.mode(colorFilter!, BlendMode.srcIn),
      placeholderBuilder: (_) => SizedBox(
        height: height,
        width: height * 4.14, // matches the SVG's 866×208 aspect ratio
      ),
    );
  }
}

/// The VOYO brandmark — the square icon portion of the logo.
class VoyoBrandmark extends StatelessWidget {
  final double size;
  final Color? colorFilter;

  const VoyoBrandmark({super.key, this.size = 32, this.colorFilter});

  @override
  Widget build(BuildContext context) {
    return SvgPicture.asset(
      'assets/brand/VOYO_Brandmark.svg',
      width: size,
      height: size,
      fit: BoxFit.contain,
      colorFilter: colorFilter == null
          ? null
          : ColorFilter.mode(colorFilter!, BlendMode.srcIn),
    );
  }
}
