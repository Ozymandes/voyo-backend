import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:http/http.dart' as http;
import 'package:supabase_flutter/supabase_flutter.dart';
import '../models/poi.dart';

class RecommendationService {
  final String _baseUrl;
  final _supabase = Supabase.instance.client;

  RecommendationService()
      : _baseUrl = dotenv.env['CLEO_API_URL'] ?? 'http://10.0.2.2:8000';

  Future<List<Poi>> getRecommendations({int limit = 20}) async {
    final session = _supabase.auth.currentSession;
    if (session == null) return [];

    final uri = Uri.parse('$_baseUrl/api/v1/recommendations')
        .replace(queryParameters: {'limit': limit.toString()});

    try {
      final resp = await http
          .get(uri, headers: {'Authorization': 'Bearer ${session.accessToken}'})
          .timeout(const Duration(seconds: 10));

      if (resp.statusCode != 200) {
        debugPrint('Recommendations API ${resp.statusCode}: ${resp.body}');
        return [];
      }

      final data = jsonDecode(resp.body) as Map<String, dynamic>;
      final recs = data['recommendations'] as List? ?? [];
      return recs.map((r) => Poi.fromJson(r as Map<String, dynamic>)).toList();
    } catch (e) {
      debugPrint('RecommendationService: $e');
      return [];
    }
  }
}
