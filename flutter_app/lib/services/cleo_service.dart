import 'dart:convert';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:http/http.dart' as http;
import '../models/chat_message.dart';

class CleoService {
  final String _baseUrl;

  CleoService()
      : _baseUrl = dotenv.env['CLEO_API_URL'] ?? 'http://10.0.2.2:8000';

  /// Send a message to CLEO and return the assistant's response text.
  Future<String> sendMessage(String message, {String? userId}) async {
    final uri = Uri.parse('$_baseUrl/api/v1/chat');
    final body = <String, dynamic>{'message': message};
    if (userId != null) body['user_id'] = userId;

    final response = await http.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(body),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(utf8.decode(response.bodyBytes));
      return data['response'] as String;
    } else {
      throw Exception('CLEO API error ${response.statusCode}: ${response.body}');
    }
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
