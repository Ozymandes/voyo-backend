import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'screens/map_screen.dart';
import 'screens/chat_screen.dart';
import 'screens/auth/login_screen.dart';
import 'screens/auth/onboarding_screen.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  await dotenv.load();

  await Supabase.initialize(
    url: dotenv.env['SUPABASE_URL']!,
    anonKey: dotenv.env['SUPABASE_ANON_KEY']!,
  );

  runApp(const VoyoApp());
}

final _supabase = Supabase.instance.client;

/// Returns true if the user has not completed onboarding yet.
/// The trigger creates a user_profiles row but leaves full_name null —
/// once the onboarding form saves a name, this returns false.
Future<bool> _needsOnboarding(String userId) async {
  try {
    final row = await _supabase
        .from('user_profiles')
        .select('full_name')
        .eq('user_id', userId)
        .maybeSingle();
    return row == null || row['full_name'] == null;
  } catch (_) {
    return false;
  }
}

class VoyoApp extends StatelessWidget {
  const VoyoApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        scaffoldBackgroundColor: Colors.white,
        colorSchemeSeed: Colors.deepOrange,
      ),
      home: StreamBuilder<AuthState>(
        stream: _supabase.auth.onAuthStateChange,
        builder: (context, snapshot) {
          final session = _supabase.auth.currentSession;

          if (session == null) {
            return const LoginScreen();
          }

          return FutureBuilder<bool>(
            future: _needsOnboarding(session.user.id),
            builder: (context, onboardingSnapshot) {
              if (onboardingSnapshot.connectionState ==
                  ConnectionState.waiting) {
                return const Scaffold(
                  body: Center(child: CircularProgressIndicator()),
                );
              }
              if (onboardingSnapshot.data == true) {
                return const OnboardingScreen();
              }
              return const MainShell();
            },
          );
        },
      ),
    );
  }
}

class MainShell extends StatefulWidget {
  const MainShell({super.key});

  @override
  State<MainShell> createState() => _MainShellState();
}

class _MainShellState extends State<MainShell> {
  int _currentIndex = 0;

  // Keep screens alive so the map doesn't reload when switching tabs
  static const _screens = [
    MapScreen(),
    ChatScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(
        index: _currentIndex,
        children: _screens,
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (i) => setState(() => _currentIndex = i),
        selectedItemColor: Colors.deepOrange,
        unselectedItemColor: Colors.grey,
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.map_outlined),
            activeIcon: Icon(Icons.map),
            label: 'Explore',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.chat_bubble_outline),
            activeIcon: Icon(Icons.chat_bubble),
            label: 'CLEO',
          ),
        ],
      ),
    );
  }
}
