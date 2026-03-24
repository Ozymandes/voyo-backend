import 'package:supabase_flutter/supabase_flutter.dart';
import '../models/poi.dart';

class SupabaseService {
  final _client = Supabase.instance.client;

  Future<List<Poi>> getPoisInView({
    required double minLat,
    required double maxLat,
    required double minLng,
    required double maxLng,
  }) async {
    final response = await _client.rpc('get_pois_in_view', params: {
      'min_lat': minLat,
      'max_lat': maxLat,
      'min_lng': minLng,
      'max_lng': maxLng,
    });

    final List data = response as List;
    return data
        .map((json) => Poi.fromJson(json as Map<String, dynamic>))
        .toList();
  }
}
