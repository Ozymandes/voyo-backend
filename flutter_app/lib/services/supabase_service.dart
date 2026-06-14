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
    final response = await _client
        .from('pois')
        .select(_poiColumns)
        .gte('latitude', minLat)
        .lte('latitude', maxLat)
        .gte('longitude', minLng)
        .lte('longitude', maxLng)
        .eq('is_active', true);

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

  // Only columns guaranteed to exist in the base schema.
  // Optional columns (opening_hours, phone_number, etc.) are fetched
  // separately when viewing POI details.
  static const _poiColumns =
      'id, name, latitude, longitude, category, average_rating, '
      'total_reviews, description, ticket_price, currency, '
      'is_active, is_verified, popularity_score, '
      'historical_significance, average_visit_duration, '
      'image_urls, tags, address, opening_hours, website_url';

  /// Featured POIs ordered by rating. Throws on error so caller can handle.
  Future<List<Poi>> getFeaturedPois({int limit = 500}) async {
    final response = await _client
        .from('pois')
        .select(_poiColumns)
        .eq('is_active', true)
        .order('popularity_score', ascending: false)
        .limit(limit);
    return (response as List)
        .map((json) => Poi.fromJson(json as Map<String, dynamic>))
        .toList();
  }

  /// Full-text search on POI name. Throws on error so caller can handle.
  Future<List<Poi>> searchPois(String query) async {
    final response = await _client
        .from('pois')
        .select(_poiColumns)
        .eq('is_active', true)
        .ilike('name', '%$query%')
        .order('popularity_score', ascending: false)
        .limit(20);
    return (response as List)
        .map((json) => Poi.fromJson(json as Map<String, dynamic>))
        .toList();
  }

  /// Returns all items for a given itinerary joined with POI name/category.
  Future<List<Map<String, dynamic>>> getItineraryItemsWithPois(
      int itineraryId) async {
    try {
      final response = await _client
          .from('itinerary_items')
          .select('*, pois(name, category)')
          .eq('itinerary_id', itineraryId)
          .order('day_number')
          .order('sequence_order');
      return (response as List).cast<Map<String, dynamic>>();
    } catch (e) {
      debugPrint('Error fetching itinerary items: $e');
      return [];
    }
  }

  /// Adds a POI or custom stop to an itinerary day.
  Future<void> addItineraryItem({
    required int itineraryId,
    int? poiId,
    String? customTitle,
    required int dayNumber,
    required String startTime, // "HH:MM:00"
  }) async {
    // Get next sequence order for this day
    final existing = await _client
        .from('itinerary_items')
        .select('sequence_order')
        .eq('itinerary_id', itineraryId)
        .eq('day_number', dayNumber)
        .order('sequence_order', ascending: false)
        .limit(1);
    final nextSeq = existing.isEmpty
        ? 1
        : ((existing.first as Map)['sequence_order'] as int) + 1;

    await _client.from('itinerary_items').insert({
      'itinerary_id': itineraryId,
      if (poiId != null) 'poi_id': poiId,
      if (customTitle != null) 'custom_title': customTitle,
      'day_number': dayNumber,
      'sequence_order': nextSeq,
      'start_time': startTime,
      'agent_suggested': false,
    });
  }

  /// Returns all past itineraries (non-current) with a stop count each.
  Future<List<Map<String, dynamic>>> getPastItineraries(String userId) async {
    final trips = await _client
        .from('itineraries')
        .select()
        .eq('user_id', userId)
        .neq('status', 'current')
        .order('created_at', ascending: false);

    if (trips.isEmpty) return [];

    final ids = trips.map((t) => (t as Map)['id'] as int).toList();
    final items = await _client
        .from('itinerary_items')
        .select('itinerary_id')
        .inFilter('itinerary_id', ids);

    final counts = <int, int>{};
    for (final item in items) {
      final id = (item as Map)['itinerary_id'] as int;
      counts[id] = (counts[id] ?? 0) + 1;
    }

    return trips.map((t) {
      final m = t as Map<String, dynamic>;
      return {...m, 'stop_count': counts[m['id'] as int] ?? 0};
    }).toList();
  }

  /// Returns ALL itineraries for a user (current + past) with stop counts.
  Future<List<Map<String, dynamic>>> getAllItineraries(String userId) async {
    final trips = await _client
        .from('itineraries')
        .select()
        .eq('user_id', userId)
        .order('created_at', ascending: false);

    if (trips.isEmpty) return [];

    final ids = trips.map((t) => (t as Map)['id'] as int).toList();
    final items = await _client
        .from('itinerary_items')
        .select('itinerary_id')
        .inFilter('itinerary_id', ids);

    final counts = <int, int>{};
    for (final item in items) {
      final id = (item as Map)['itinerary_id'] as int;
      counts[id] = (counts[id] ?? 0) + 1;
    }

    return trips.map((t) {
      final m = t as Map<String, dynamic>;
      return {...m, 'stop_count': counts[m['id'] as int] ?? 0};
    }).toList();
  }

  /// Deletes an itinerary and all its items.
  Future<void> deleteItinerary(int itineraryId) async {
    await _client
        .from('itinerary_items')
        .delete()
        .eq('itinerary_id', itineraryId);
    await _client.from('itineraries').delete().eq('id', itineraryId);
  }

  /// Deletes a single itinerary item by its row id.
  Future<void> deleteItineraryItem(int itemId) async {
    await _client.from('itinerary_items').delete().eq('id', itemId);
  }

  /// Switches the active itinerary to [itineraryId].
  /// All other itineraries for the user are demoted to 'draft'.
  Future<void> setActiveItinerary({
    required String userId,
    required int itineraryId,
  }) async {
    await _client
        .from('itineraries')
        .update({'status': 'draft'})
        .eq('user_id', userId);
    await _client
        .from('itineraries')
        .update({'status': 'current'})
        .eq('id', itineraryId);
  }

  /// Creates a new itinerary for the user with status 'current'.
  /// Any previously current itinerary is set to 'draft' first.
  Future<Itinerary?> createItinerary({
    required String userId,
    required String title,
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    try {
      // Demote any existing current itinerary
      await _client
          .from('itineraries')
          .update({'status': 'draft'})
          .eq('user_id', userId)
          .eq('status', 'current');

      final response = await _client
          .from('itineraries')
          .insert({
            'user_id': userId,
            'title': title,
            'status': 'current',
            if (startDate != null)
              'start_date': startDate.toIso8601String().split('T').first,
            if (endDate != null)
              'end_date': endDate.toIso8601String().split('T').first,
          })
          .select()
          .single();
      return Itinerary.fromJson(response as Map<String, dynamic>);
    } catch (e) {
      debugPrint('Error creating itinerary: $e');
      rethrow;
    }
  }
}
