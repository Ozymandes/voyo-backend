import 'package:flutter/material.dart';

class CleoOwl extends StatelessWidget {
  final double size;
  const CleoOwl({super.key, this.size = 44});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: size,
      height: size,
      child: CustomPaint(painter: _OwlPainter()),
    );
  }
}

class _OwlPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final s = size.width / 44;

    Paint p(Color c) => Paint()..color = c;

    // Outer circle (sky tint bg)
    canvas.drawCircle(Offset(22 * s, 22 * s), 22 * s, p(const Color(0x121C72B4)));

    // Body
    canvas.drawOval(
      Rect.fromCenter(center: Offset(22 * s, 27 * s), width: 20 * s, height: 22 * s),
      p(const Color(0xFF1C72B4)),
    );

    // Head
    canvas.drawCircle(Offset(22 * s, 17 * s), 10 * s, p(const Color(0xFF1C72B4)));

    // Ear tufts
    canvas.drawPath(
      Path()
        ..moveTo(15 * s, 9 * s)
        ..lineTo(13 * s, 4 * s)
        ..lineTo(18 * s, 8 * s)
        ..close(),
      p(const Color(0xFF1C72B4)),
    );
    canvas.drawPath(
      Path()
        ..moveTo(29 * s, 9 * s)
        ..lineTo(31 * s, 4 * s)
        ..lineTo(26 * s, 8 * s)
        ..close(),
      p(const Color(0xFF1C72B4)),
    );

    // Face
    canvas.drawOval(
      Rect.fromCenter(center: Offset(22 * s, 17 * s), width: 15 * s, height: 14 * s),
      p(const Color(0xFFEDE8DC)),
    );

    // Eyes — white
    canvas.drawCircle(Offset(18.5 * s, 16 * s), 3.5 * s, p(Colors.white));
    canvas.drawCircle(Offset(25.5 * s, 16 * s), 3.5 * s, p(Colors.white));

    // Pupils
    canvas.drawCircle(Offset(18.5 * s, 16 * s), 2 * s, p(const Color(0xFF1C1916)));
    canvas.drawCircle(Offset(25.5 * s, 16 * s), 2 * s, p(const Color(0xFF1C1916)));

    // Eye shines
    canvas.drawCircle(Offset(19.2 * s, 15.3 * s), 0.7 * s, p(Colors.white));
    canvas.drawCircle(Offset(26.2 * s, 15.3 * s), 0.7 * s, p(Colors.white));

    // Beak
    canvas.drawPath(
      Path()
        ..moveTo(22 * s, 19 * s)
        ..lineTo(20.2 * s, 21.5 * s)
        ..lineTo(23.8 * s, 21.5 * s)
        ..close(),
      p(const Color(0xFFD48A10)),
    );

    // Chest
    canvas.drawOval(
      Rect.fromCenter(center: Offset(22 * s, 28 * s), width: 10 * s, height: 12 * s),
      Paint()..color = const Color(0xFFEDE8DC).withValues(alpha: 0.5),
    );
  }

  @override
  bool shouldRepaint(_) => false;
}
