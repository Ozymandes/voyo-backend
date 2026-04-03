import 'dart:convert';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:http/http.dart' as http;

class CleoService {
  final String _baseUrl;

  CleoService()
      : _baseUrl = dotenv.env['CLEO_API_URL'] ?? 'http://10.0.2.2:8000';

  /// Send a message to CLEO and return the assistant's response text.
  /// [userId] is optional — pass a seeded test UUID to get personalized responses.
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
      throw Exception(
        'CLEO API error ${response.statusCode}: ${response.body}',
      );
    }
  }
}
