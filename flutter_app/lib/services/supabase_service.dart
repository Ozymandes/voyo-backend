import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:http/http.dart' as http;
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
    // Canonical column set (same as getFeaturedPois / searchPois) so a POI
    // resolves to the identical enriched record everywhere — Explore,
    // Planner, search, and Map Explore. The previous reduced select
    // (id, name, lat, lng, category, rating, description) starved the map
    // of `narrative`, `image_urls`, `ticket_prices`, `tags`, `city`, and
    // `is_verified`, which is why map geotag cards showed stale legacy
    // copy + gradient placeholders while Planner showed enriched data.
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
      final response = await _client.rpc(
        'get_current_itinerary_pois',
        params: {'p_user_id': userId},
      );
      return (response as List)
          .map((json) => ItineraryPoi.fromJson(json as Map<String, dynamic>))
          .toList();
    } catch (e) {
      debugPrint('Error fetching itinerary POIs: $e');
      return [];
    }
  }

  /// Batch-resolves the canonical (enriched) [Poi] records for a set of
  /// POI IDs. Uses the SAME `_poiColumns` select as [getPoisInView] /
  /// [getFeaturedPois] so an itinerary-stop POI resolves to the identical
  /// enriched record as the same POI shown in Explore / Planner / Details.
  ///
  /// This is the fix for the "stale stop card" bug: the itinerary-stop
  /// markers on the map used to open a separate sheet that fetched images
  /// + copy from Wikipedia by name, which was slow, unreliable, and
  /// inconsistent with the rest of the app. Now we hydrate the canonical
  /// Poi once and reuse the same [MapPoiPreviewCard] as regular POIs.
  ///
  /// Returns a {poi_id: Poi} map for O(1) lookup by callers.
  Future<Map<int, Poi>> getPoisByIds(Iterable<int> ids) async {
    final idList = ids.whereType<int>().toList(growable: false);
    if (idList.isEmpty) return {};
    try {
      final response = await _client
          .from('pois')
          .select(_poiColumns)
          .inFilter('id', idList.map((i) => i.toString()).toList())
          .eq('is_active', true);
      final List data = response as List;
      return {
        for (final json in data)
          (json as Map<String, dynamic>)['id'] as int:
              Poi.fromJson(json),
      };
    } catch (e) {
      debugPrint('Error fetching POIs by IDs: $e');
      return {};
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
      'id, name, latitude, longitude, category, city, average_rating, '
      'total_reviews, description, narrative, ticket_price, currency, '
      'ticket_prices, travel_tips, '
      'is_active, is_verified, popularity_score, '
      'historical_significance, average_visit_duration, '
      'image_urls, address, opening_hours, website_url, phone_number, tags';

  /// Featured POIs ordered by rating. Throws on error so caller can handle.
  Future<List<Poi>> getFeaturedPois({int limit = 30}) async {
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
    int itineraryId,
  ) async {
    try {
      // The joined pois() projection carries everything the planner/journey/
      // add-stop surfaces render. Using `pois(*)` (all columns) so the
      // tappable POI detail sheet opened from the planner stop card gets a
      // fully-hydrated Poi (Poi.fromJson needs id/latitude/longitude as
      // required fields, plus image_urls/average_rating/travel_tips for a
      // rich detail view). `description` + `narrative` feed the per-stop
      // description line (#general-fix) — `narrative` is the canonical
      // LLM-enriched text from enrich_narratives.py, `description` is the
      // shorter seed. Adding columns here is backward-compatible for the
      // other call sites (journey_screen, add_to_itinerary_sheet): they
      // simply ignore the extra fields. `*` on itinerary_items already
      // returns `notes`, which is where Safarny/CLEO persists the per-stop
      // tip (see persistence.save_optimized_itinerary).
      final response = await _client
          .from('itinerary_items')
          .select('*, pois(*)')
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
    final nextSeq =
        existing.isEmpty
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
      final m = t;
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
      final m = t;
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

      final response =
          await _client
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
      return Itinerary.fromJson(response);
    } catch (e) {
      debugPrint('Error creating itinerary: $e');
      rethrow;
    }
  }

  // ── Add-POI feasibility check (Tier 2 honest routing) ────────────────
  // Mirrors the backend `preview_add` verdict. The Flutter flow uses this
  // BEFORE the dumb Supabase insert so VROOM — not a guess — decides whether
  // a POI fits, where it fits best, and whether anything gets displaced.

  Future<FeasibilityVerdict?> previewAdd({
    required int itineraryId,
    required int candidatePoiId,
    int? preferredDay,
    int? days,
  }) async {
    final baseUrl = dotenv.env['CLEO_API_URL'] ?? 'http://10.0.2.2:8000';
    final token = _client.auth.currentSession?.accessToken;
    if (token == null)
      return null; // not signed in — caller falls back gracefully

    final uri = Uri.parse('$baseUrl/api/v1/itinerary/preview-add');
    final body = <String, dynamic>{
      'itinerary_id': itineraryId,
      'candidate_poi_id': candidatePoiId,
      if (preferredDay != null) 'preferred_day': preferredDay,
      if (days != null) 'days': days,
    };
    try {
      final resp = await http
          .post(
            uri,
            headers: {
              'Content-Type': 'application/json',
              'Authorization': 'Bearer $token',
            },
            body: jsonEncode(body),
          )
          .timeout(const Duration(seconds: 30));
      if (resp.statusCode != 200) {
        // CRITICAL (#22): a failed feasibility check is NOT the same as a
        // feasible result. We must surface this to the caller so the UI can
        // render the "route verification unavailable" state instead of the
        // generic clock-slot picker — which previously let users schedule
        // impossible trips whenever the matrix engine returned an error.
        // Returning null here would conflate "engine unreachable" with
        // "user not signed in" and silently re-enable the dangerous fallback.
        final detail =
            resp.statusCode == 503 ? 'route engine unavailable' : 'HTTP ${resp.statusCode}';
        throw PreviewAddUnavailableException(
          'preview-add $detail: ${resp.body}',
          status: resp.statusCode,
        );
      }
      return FeasibilityVerdict.fromJson(
        jsonDecode(utf8.decode(resp.bodyBytes)) as Map<String, dynamic>,
      );
    } on PreviewAddUnavailableException {
      rethrow; // caller decides UI state; never swallow feasibility failures
    } catch (e) {
      // Network/timeout/DNS — also surface as unavailable. Same reason as above:
      // we cannot claim a schedule is feasible if we never verified it.
      throw PreviewAddUnavailableException('preview-add network failure: $e');
    }
  }
}

/// Verdict from the backend ``preview_add`` dry-run. Drives the add-to-trip
/// UX: green (fits), amber (fits elsewhere / displaces), red (won't fit).
class FeasibilityVerdict {
  final bool feasible;
  final bool alreadyOnTrip;
  final int? recommendedDay;
  final int? preferredDay;
  final bool preferredDayFeasible;
  final List<DisplacedPoi> displacedPois;
  final String reason;

  /// Path B: VROOM's deterministic placement for the candidate — the exact
  /// clock slot the optimizer assigned, plus neighbouring stops so the UI
  /// can render "CLEO suggests ~2:00 PM, between X and Y". Null when the
  /// candidate was infeasible, the backend is unreachable, or VROOM didn't
  /// place it.
  final CandidatePlacement? candidatePlacement;

  const FeasibilityVerdict({
    required this.feasible,
    required this.alreadyOnTrip,
    required this.recommendedDay,
    required this.preferredDay,
    required this.preferredDayFeasible,
    required this.displacedPois,
    required this.reason,
    this.candidatePlacement,
  });

  factory FeasibilityVerdict.fromJson(Map<String, dynamic> j) {
    final disp = (j['displaced_pois'] as List? ?? []);
    final placement = j['candidate_placement'];
    return FeasibilityVerdict(
      feasible: j['feasible'] as bool? ?? false,
      alreadyOnTrip: j['already_on_trip'] as bool? ?? false,
      recommendedDay: j['recommended_day'] as int?,
      preferredDay: j['preferred_day'] as int?,
      preferredDayFeasible: j['preferred_day_feasible'] as bool? ?? false,
      displacedPois: disp
          .map((d) => DisplacedPoi.fromJson(d as Map<String, dynamic>))
          .toList(growable: false),
      reason: j['reason'] as String? ?? '',
      candidatePlacement: placement is Map<String, dynamic>
          ? CandidatePlacement.fromJson(placement)
          : null,
    );
  }
}

class DisplacedPoi {
  final int poiId;
  final int dayWas;
  const DisplacedPoi({required this.poiId, required this.dayWas});
  factory DisplacedPoi.fromJson(Map<String, dynamic> j) =>
      DisplacedPoi(poiId: j['poi_id'] as int, dayWas: j['day_was'] as int);
}

/// Thrown when the backend feasibility check itself failed (HTTP 503,
/// network error, timeout). Distinct from `previewAdd` returning `null`,
/// which now means only "user not signed in". This distinction is the
/// keystone of item #22: a *failed* feasibility check must never become a
/// *free* schedule (the old bug), and the only way to tell the two apart is
/// to surface the failure instead of swallowing it into null.
class PreviewAddUnavailableException implements Exception {
  final String message;
  final int? status;
  const PreviewAddUnavailableException(this.message, {this.status});
  @override
  String toString() => 'PreviewAddUnavailableException: $message';
}

/// VROOM's deterministic placement for a candidate POI (Path B).
class CandidatePlacement {
  /// "HH:MM:SS" — VROOM-assigned arrival time on the recommended day.
  final String? arrivalTime;
  final String? departureTime;
  final int? sequence;
  final String? previousName;
  final String? nextName;
  final int? dayStopsCount;

  const CandidatePlacement({
    required this.arrivalTime,
    required this.departureTime,
    required this.sequence,
    required this.previousName,
    required this.nextName,
    required this.dayStopsCount,
  });

  factory CandidatePlacement.fromJson(Map<String, dynamic> j) =>
      CandidatePlacement(
        arrivalTime: j['arrival_time'] as String?,
        departureTime: j['departure_time'] as String?,
        sequence: j['sequence'] as int?,
        previousName: j['previous_name'] as String?,
        nextName: j['next_name'] as String?,
        dayStopsCount: j['day_stops_count'] as int?,
      );
}
