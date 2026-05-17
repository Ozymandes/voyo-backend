import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'screens/auth/login_screen.dart';
import 'screens/auth/onboarding_screen.dart';
import 'screens/main_shell.dart';
import 'theme.dart';

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
        scaffoldBackgroundColor: VoyoColors.page,
        colorScheme: ColorScheme.fromSeed(
          seedColor: VoyoColors.expedition,
          surface: VoyoColors.page,
        ),
        textTheme: GoogleFonts.instrumentSansTextTheme(),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: VoyoColors.vellum,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: const BorderSide(color: VoyoColors.smoke),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: const BorderSide(color: VoyoColors.smoke),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: const BorderSide(color: VoyoColors.expedition, width: 1.5),
          ),
        ),
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

