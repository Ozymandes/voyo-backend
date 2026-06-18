import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:geolocator/geolocator.dart';
import 'package:http/http.dart' as http;

/// Current-conditions snapshot for the Discovery weather widget.
///
/// Uses OpenWeather (same provider/key as the CLEO backend WeatherTool) so the
/// app and the planner never disagree about weather. GPS is requested per D3:
/// on denial or offline we fall back to Cairo rather than failing — weather is
/// a nicety, not a blocker. Results are cached 10 minutes to stay polite.
class WeatherService {
  WeatherService._();
  static final WeatherService instance = WeatherService._();

  static const _apiKeyEnv = 'WEATHER_API_KEY';
  static const _baseUrl = 'https://api.openweathermap.org/data/2.5';
  static const _cacheTtl = Duration(minutes: 10);
  static const _defaultCity = 'Cairo';

  // Cache keyed by city (or 'gps' for the device-location read).
  final _cache = <String, _Cached>{};
  String? _lastDeniedCity; // remember the fallback city after a GPS denial

  /// Returns current weather for the device location if granted, else Cairo.
  /// Never throws — failures resolve to an [Unavailable] result the UI can
  /// render gracefully.
  Future<WeatherResult> getCurrent() async {
    final key = dotenv.env[_apiKeyEnv];
    if (key == null || key.isEmpty) {
      return const WeatherResult.unavailable('Weather not configured.');
    }

    // 1. Try device GPS once per session; on denial, stick to the fallback.
    if (_lastDeniedCity == null) {
      try {
        final pos = await _readPosition();
        if (pos != null) {
          final cached = _cache['gps'];
          if (cached != null && !cached.isExpired) return cached.result;
          final r = await _fetchByCoord(pos.latitude, pos.longitude, key);
          if (r is CurrentWeather) {
            _cache['gps'] = _Cached(r);
            return r;
          }
        }
      } catch (e) {
        debugPrint('WeatherService: GPS unavailable, falling back to city — $e');
      }
    }

    // 2. Fall back to Cairo (or whatever we settled on).
    final city = _lastDeniedCity ?? _defaultCity;
    final cached = _cache[city];
    if (cached != null && !cached.isExpired) return cached.result;
    try {
      final r = await _fetchByCity(city, key);
      _cache[city] = _Cached(r);
      _lastDeniedCity ??= city;
      return r;
    } catch (e) {
      debugPrint('WeatherService: fetch by city failed — $e');
      return const WeatherResult.unavailable('Weather unavailable right now.');
    }
  }

  Future<Position?> _readPosition() async {
    final service = await Geolocator.isLocationServiceEnabled();
    if (!service) return null;
    var perm = await Geolocator.checkPermission();
    if (perm == LocationPermission.denied) {
      perm = await Geolocator.requestPermission();
    }
    if (perm == LocationPermission.denied ||
        perm == LocationPermission.deniedForever) {
      _lastDeniedCity = _defaultCity;
      return null;
    }
    return Geolocator.getCurrentPosition(
        locationSettings:
            const LocationSettings(accuracy: LocationAccuracy.low));
  }

  Future<WeatherResult> _fetchByCity(String city, String key) async {
    final uri = Uri.parse('$_baseUrl/weather')
        .replace(queryParameters: {'q': '$city,EG', 'appid': key, 'units': 'metric'});
    return _parseCurrent(await http.get(uri, headers: const {
      'User-Agent': 'VOYO/1.0 (Discovery weather widget)'
    }).timeout(const Duration(seconds: 5)));
  }

  Future<WeatherResult> _fetchByCoord(double lat, double lon, String key) async {
    final uri = Uri.parse('$_baseUrl/weather').replace(queryParameters: {
      'lat': lat.toString(),
      'lon': lon.toString(),
      'appid': key,
      'units': 'metric',
    });
    return _parseCurrent(await http.get(uri, headers: const {
      'User-Agent': 'VOYO/1.0 (Discovery weather widget)'
    }).timeout(const Duration(seconds: 5)));
  }

  WeatherResult _parseCurrent(http.Response resp) {
    if (resp.statusCode != 200) {
      return WeatherResult.unavailable(
          'Weather service returned ${resp.statusCode}.');
    }
    final d = jsonDecode(resp.body) as Map<String, dynamic>;
    final weather = (d['weather'] as List).first as Map<String, dynamic>;
    return CurrentWeather(
      city: (d['name'] as String?) ?? _defaultCity,
      tempC: (d['main']['temp'] as num).round(),
      feelsLikeC: (d['main']['feels_like'] as num).round(),
      condition: weather['main'] as String, // e.g. "Clear", "Rain"
      conditionLabel: weather['description'] as String, // e.g. "clear sky"
      icon: weather['icon'] as String,
    );
  }
}

sealed class WeatherResult {
  const WeatherResult();
  const factory WeatherResult.unavailable(String message) = Unavailable;
}

class Unavailable extends WeatherResult {
  final String message;
  const Unavailable(this.message);
}

class CurrentWeather extends WeatherResult {
  final String city;
  final int tempC;
  final int feelsLikeC;
  final String condition; // OpenWeather 'main': Clear / Clouds / Rain / ...
  final String conditionLabel; // human description
  final String icon; // OpenWeather icon code, e.g. '01d'
  const CurrentWeather({
    required this.city,
    required this.tempC,
    required this.feelsLikeC,
    required this.condition,
    required this.conditionLabel,
    required this.icon,
  });
}

class _Cached {
  final WeatherResult result;
  final DateTime at;
  _Cached(this.result) : at = DateTime.now();
  bool get isExpired => DateTime.now().difference(at) > WeatherService._cacheTtl;
}

/// A travel-actionable one-liner derived from the conditions, in VOYO voice.
/// Pure function so it's easy to unit-test and keep consistent with CLEO's
/// WeatherTool.assess_suitability thresholds.
String weatherSuggestion(CurrentWeather w) {
  final t = w.tempC;
  final c = w.condition.toLowerCase();
  if (c.contains('rain') || c.contains('drizzle')) {
    return 'Rainy — a great day for museums and covered bazaars.';
  }
  if (c.contains('sand') || c.contains('dust')) {
    return 'Dusty conditions — favor indoor sights and limit time outside.';
  }
  if (t >= 36) {
    return 'Very hot ($t°C) — explore temples early morning or after sunset.';
  }
  if (t >= 30) {
    return 'Hot ($t°C) — pace yourself, shade and water between stops.';
  }
  if (t <= 12) {
    return 'Cool ($t°C) — a light layer for early starts and evenings.';
  }
  if (c.contains('clear')) {
    return 'Lovely conditions — ideal for walking sights and outdoor cafés.';
  }
  return 'Comfortable conditions — a relaxed day for exploring.';
}
