import 'package:flutter/foundation.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../models/poi.dart';
import '../models/itinerary_poi.dart';
import '../models/itinerary.dart';

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

  /// Returns the POIs from the user's current (active) itinerary for map overlay.
  Future<List<ItineraryPoi>> getCurrentItineraryPois(String userId) async {
    try {
      final response = await _client
          .rpc('get_current_itinerary_pois', params: {'p_user_id': userId});
      return (response as List)
          .map((json) => ItineraryPoi.fromJson(json as Map<String, dynamic>))
          .toList();
    } catch (e) {
      debugPrint('Error fetching itinerary POIs: $e');
      return [];
    }
  }

  /// Returns the user's most recent itinerary with status 'current'.
  Future<Itinerary?> getCurrentItinerary(String userId) async {
    try {
      final response = await _client
          .from('itineraries')
          .select()
          .eq('user_id', userId)
          .eq('status', 'current')
          .order('created_at', ascending: false)
          .limit(1);
      final list = response as List;
      if (list.isEmpty) return null;
      return Itinerary.fromJson(list.first as Map<String, dynamic>);
    } catch (e) {
      debugPrint('Error fetching current itinerary: $e');
      return null;
    }
  }

  /// Returns all items for a given itinerary, ordered by day and sequence.
  Future<List<ItineraryItem>> getItineraryItems(int itineraryId) async {
    try {
      final response = await _client
          .from('itinerary_items')
          .select()
          .eq('itinerary_id', itineraryId)
          .order('day_number')
          .order('sequence_order');
      return (response as List)
          .map((json) => ItineraryItem.fromJson(json as Map<String, dynamic>))
          .toList();
    } catch (e) {
      debugPrint('Error fetching itinerary items: $e');
      return [];
    }
  }
}
