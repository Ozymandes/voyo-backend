import 'package:flutter/material.dart';

/// CLEO's avatar — rendered from the brand PNG assets.
///
/// Two variants:
///   • [CleoAvatarVariant.default_] — the resting/chat-window face. Used in
///     the chat app bar, message bubbles, and the empty state.
///   • [CleoAvatarVariant.thinking] — shown while CLEO is parsing a prompt,
///     paired with the animated typing dots and the staged status copy.
///
/// This replaces the prior hand-drawn `CleoOwl` CustomPaint so the product
/// speaks with the real VOYO brand voice. The PNGs are bundled in
/// `assets/cleo/` and declared in pubspec.yaml.
enum CleoAvatarVariant { default_, thinking }

class CleoAvatar extends StatelessWidget {
  final double size;
  final CleoAvatarVariant variant;

  const CleoAvatar({
    super.key,
    this.size = 44,
    this.variant = CleoAvatarVariant.default_,
  });

  static const _paths = {
    CleoAvatarVariant.default_: 'assets/cleo/CLEO_Default.png',
    CleoAvatarVariant.thinking: 'assets/cleo/CLEO_Thinking.png',
  };

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: size,
      height: size,
      child: Image.asset(
        _paths[variant]!,
        fit: BoxFit.contain,
        filterQuality: FilterQuality.high,
        // If the asset ever fails to load, fall back to a quiet brand-tinted
        // circle so the layout never breaks — better than a blank box.
        errorBuilder: (_, _, _) => Container(
          decoration: const BoxDecoration(
            color: Color(0x1AD45028),
            shape: BoxShape.circle,
          ),
        ),
      ),
    );
  }
}
