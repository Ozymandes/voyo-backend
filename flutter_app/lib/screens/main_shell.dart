import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../theme.dart';
import '../widgets/cleo_owl.dart';
import 'explore_screen.dart';
import 'chat_screen.dart';
import 'journey_screen.dart';
import 'planner_screen.dart';

class MainShell extends StatefulWidget {
  const MainShell({super.key});

  @override
  State<MainShell> createState() => _MainShellState();
}

class _MainShellState extends State<MainShell> {
  int _navIndex = 0;

  // Maps nav indices (0,1,3,4) to screen indices (0,1,2,3)
  // Nav index 2 = center V button, goes to Explore (screen 0)
  int get _screenIndex => switch (_navIndex) {
        1 => 1,
        3 => 2,
        4 => 3,
        _ => 0,
      };

  void _onNavTap(int navIdx) {
    setState(() => _navIndex = navIdx == 2 ? 0 : navIdx);
  }

  // Screens are fixed — defined once so state is preserved across tab switches.
  late final _screens = [
    ExploreScreen(onSwitchToCleo: () => _onNavTap(3)),
    const PlannerScreen(),
    ChatScreen(onSwitchToPlanner: () => _onNavTap(1)),
    const JourneyScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: VoyoColors.page,
      // Offstage + TickerMode: keeps screens alive but suspends animations
      // and mouse-event subscriptions on inactive screens, which prevents
      // flutter_map from firing mouse_tracker assertions on every click.
      body: Stack(
        children: [
          for (int i = 0; i < _screens.length; i++)
            Offstage(
              offstage: _screenIndex != i,
              child: TickerMode(
                enabled: _screenIndex == i,
                child: _screens[i],
              ),
            ),
        ],
      ),
      floatingActionButton: GestureDetector(
        onTap: () => _onNavTap(2),
        child: Container(
          width: 58,
          height: 58,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            gradient: const LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [Color(0xFFD45028), Color(0xFFB83818)],
            ),
            boxShadow: [
              BoxShadow(
                color: VoyoColors.expedition.withValues(alpha: 0.38),
                blurRadius: 16,
                offset: const Offset(0, 4),
              ),
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.1),
                blurRadius: 6,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: Center(
            child: Text(
              'V',
              style: GoogleFonts.fraunces(
                fontSize: 26,
                fontWeight: FontWeight.w400,
                fontStyle: FontStyle.italic,
                color: Colors.white,
              ),
            ),
          ),
        ),
      ),
      floatingActionButtonLocation: FloatingActionButtonLocation.centerDocked,
      bottomNavigationBar: BottomAppBar(
        notchMargin: 8,
        shape: const CircularNotchedRectangle(),
        color: Colors.white,
        surfaceTintColor: Colors.transparent,
        elevation: 8,
        shadowColor: Colors.black12,
        padding: EdgeInsets.zero,
        child: SizedBox(
          height: 60,
          child: Row(
            children: [
              _NavItem(
                index: 0,
                current: _navIndex,
                icon: Icons.map_outlined,
                activeIcon: Icons.map,
                label: 'Explore',
                activeColor: VoyoColors.expedition,
                onTap: _onNavTap,
              ),
              _NavItem(
                index: 1,
                current: _navIndex,
                icon: Icons.calendar_today_outlined,
                activeIcon: Icons.calendar_today,
                label: 'Planner',
                activeColor: VoyoColors.terra,
                onTap: _onNavTap,
              ),
              const SizedBox(width: 70), // FAB space
              _NavItem(
                index: 3,
                current: _navIndex,
                icon: Icons.chat_bubble_outline,
                activeIcon: Icons.chat_bubble,
                label: 'Cleo',
                activeColor: VoyoColors.sky,
                onTap: _onNavTap,
              ),
              _NavItem(
                index: 4,
                current: _navIndex,
                icon: Icons.photo_album_outlined,
                activeIcon: Icons.photo_album,
                label: 'Journey',
                activeColor: VoyoColors.ink,
                onTap: _onNavTap,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _NavItem extends StatelessWidget {
  final int index;
  final int current;
  final IconData icon;
  final IconData activeIcon;
  final String label;
  final Color activeColor;
  final ValueChanged<int> onTap;

  const _NavItem({
    required this.index,
    required this.current,
    required this.icon,
    required this.activeIcon,
    required this.label,
    required this.activeColor,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final isActive = current == index;
    return Expanded(
      child: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTap: () => onTap(index),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              isActive ? activeIcon : icon,
              color: isActive ? activeColor : VoyoColors.stone,
              size: 22,
            ),
            const SizedBox(height: 3),
            Text(
              label,
              style: GoogleFonts.instrumentSans(
                fontSize: 10,
                fontWeight: isActive ? FontWeight.w700 : FontWeight.w500,
                color: isActive ? activeColor : VoyoColors.stone,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

