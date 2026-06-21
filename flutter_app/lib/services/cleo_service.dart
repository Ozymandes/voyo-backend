import 'dart:convert';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:http/http.dart' as http;
import '../models/chat_message.dart';

/// Enriched CLEO reply: the answer text plus optional provenance pills and a
/// coarse confidence label. Older callers that only need the text use `.text`.
/// `SourcePill` is imported from chat_message.dart (shared model layer).
class CleoReply {
  final String text;
  final List<SourcePill> sources;
  final String? confidence; // "high" | "medium" | "low" | null
  const CleoReply({
    required this.text,
    this.sources = const [],
    this.confidence,
  });
}

class CleoService {
  final String _baseUrl;

  CleoService()
      : _baseUrl = dotenv.env['CLEO_API_URL'] ?? 'http://10.0.2.2:8000';

  /// Send a message to CLEO and return the assistant's reply with provenance.
  ///
  /// [poiId] + [intent] ("poi_explain") are sent when the message originates
  /// from a POI "Ask Cleo" entry point, giving the agent place context per the
  /// MASTER_PLAN chat contract.
  Future<CleoReply> sendMessage(
    String message, {
    String? userId,
    int? poiId,
    String? intent,
  }) async {
    // Dev affordance: render rich sample responses (image + follow-ups) so the
    // chat UI is testable before the CLEO `poi_explain` path ships. Enable by
    // setting CLEO_STUB=1 in flutter_app/.env. Off → real network call.
    if (dotenv.env['CLEO_STUB'] == '1') {
      return CleoReply(text: _stubResponse(message, poiId: poiId, intent: intent));
    }

    final uri = Uri.parse('$_baseUrl/api/v1/chat');
    final body = <String, dynamic>{'message': message};
    if (userId != null) body['user_id'] = userId;
    if (poiId != null) body['poi_id'] = poiId;
    if (intent != null) body['intent'] = intent;

    final response = await http.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(body),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(utf8.decode(response.bodyBytes));
      final rawSources = data['sources'] as List<dynamic>?;
      return CleoReply(
        text: data['response'] as String,
        sources: rawSources == null
            ? const []
            : rawSources
                .map((s) => SourcePill.fromJson(s as Map<String, dynamic>))
                .toList(growable: false),
        confidence: data['confidence'] as String?,
      );
    } else {
      throw Exception('CLEO API error ${response.statusCode}: ${response.body}');
    }
  }

  /// Sample responses for the `CLEO_STUB` dev toggle. Exercises the markdown
  /// image styling and the trailing `follow_ups` chip parsing so the UI is
  /// testable without the backend. Not used in production (toggle is off).
  String _stubResponse(String message, {int? poiId, String? intent}) {
    if (intent == 'poi_explain') {
      final nameMatch =
          RegExp(r'about\s+(.+)$', caseSensitive: false).firstMatch(message);
      final place = (nameMatch?.group(1) ?? 'this place')
          .trim()
          .replaceAll(RegExp(r'[?.!]'), '');
      return '''**$place** is one of those sites that rewards a slow visit. Its scale reveals itself gradually, so give yourself a few hours and arrive early, before the tour groups settle in.

The stonework photographs best in the soft light of early morning and late afternoon. Carry water and shade, and wear comfortable shoes — there is always more walking than you expect.

```json
{"follow_ups": ["What is the best time of day to visit?", "How much are tickets and where do I buy them?", "How do I get there and back?", "What should I wear or bring?"]}
```''';
    }
    return '''Great question. Here is how I would approach it.

For most travellers the sweet spot is to start early, break during the midday heat, and head out again in the late afternoon. That rhythm dodges both the sun and the biggest crowds.

```json
{"follow_ups": ["Can you turn this into an itinerary?", "What should I pack?", "Any hidden gems nearby?"]}
```''';
  }

  /// Load past conversation history for a user (persisted on backend).
  Future<List<ChatMessage>> loadHistory(String userId, {int limit = 30}) async {
    final uri = Uri.parse(
      '$_baseUrl/api/v1/conversation/history/$userId?limit=$limit',
    );

    final response = await http.get(uri);

    if (response.statusCode == 200) {
      final data = jsonDecode(utf8.decode(response.bodyBytes));
      final history = data['history'] as List<dynamic>? ?? [];
      return history.map((item) {
        final map = item as Map<String, dynamic>;
        return ChatMessage(
          role: map['role'] as String,
          text: map['content'] as String,
          timestamp: DateTime.tryParse(map['timestamp'] as String? ?? '') ??
              DateTime.now(),
        );
      }).toList();
    } else if (response.statusCode == 404) {
      return []; // No history yet — not an error
    } else {
      throw Exception(
          'History load error ${response.statusCode}: ${response.body}');
    }
  }

  /// Clear all conversation history for a user.
  Future<void> clearHistory(String userId) async {
    final uri = Uri.parse('$_baseUrl/api/v1/conversation/history/$userId');
    final response = await http.delete(uri);
    if (response.statusCode != 200) {
      throw Exception(
          'Clear history error ${response.statusCode}: ${response.body}');
    }
  }
}
