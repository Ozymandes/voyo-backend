import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/chat_message.dart';

class ChatSession {
  final String id;
  final List<ChatMessage> messages;
  final DateTime createdAt;

  ChatSession({
    required this.id,
    required this.messages,
    required this.createdAt,
  });

  /// Title shown in the sidebar — first user message, truncated.
  String get title {
    final first = messages.firstWhere(
      (m) => m.isUser,
      orElse: () => messages.first,
    );
    final t = first.text.trim();
    return t.length > 48 ? '${t.substring(0, 48)}…' : t;
  }

  bool get isEmpty => messages.isEmpty;
}

/// Manages per-session chat history stored locally in SharedPreferences.
class ChatHistoryService {
  static const _indexPrefix = 'chat_index_';
  static const _sessionPrefix = 'chat_session_';

  // ── Sessions ──────────────────────────────────────────────────────────────

  Future<List<ChatSession>> loadAllSessions(String userId) async {
    final prefs = await SharedPreferences.getInstance();
    final ids = _getIndex(prefs, userId);
    final sessions = <ChatSession>[];
    for (final id in ids.reversed) {
      final s = _readSession(prefs, userId, id);
      if (s != null && !s.isEmpty) sessions.add(s);
    }
    return sessions;
  }

  Future<ChatSession?> loadSession(String userId, String sessionId) async {
    final prefs = await SharedPreferences.getInstance();
    return _readSession(prefs, userId, sessionId);
  }

  /// Creates a new session and returns its ID. Does NOT save until first append.
  String newSessionId() => DateTime.now().millisecondsSinceEpoch.toString();

  Future<void> appendToSession(
      String userId, String sessionId, ChatMessage msg) async {
    final prefs = await SharedPreferences.getInstance();
    final existing = _readSession(prefs, userId, sessionId);
    final messages = existing?.messages ?? [];
    final createdAt = existing?.createdAt ?? DateTime.now();
    messages.add(msg);

    // Register in index if first message
    if (existing == null) {
      final ids = _getIndex(prefs, userId);
      if (!ids.contains(sessionId)) {
        ids.add(sessionId);
        await prefs.setString('$_indexPrefix$userId', jsonEncode(ids));
      }
    }

    await prefs.setString(
      '$_sessionPrefix${userId}_$sessionId',
      jsonEncode({
        'id': sessionId,
        'created_at': createdAt.toIso8601String(),
        'messages': messages
            .map((m) => {
                  'role': m.role,
                  'text': m.text,
                  'timestamp': m.timestamp.toIso8601String(),
                })
            .toList(),
      }),
    );
  }

  Future<void> deleteSession(String userId, String sessionId) async {
    final prefs = await SharedPreferences.getInstance();
    final ids = _getIndex(prefs, userId)..remove(sessionId);
    await prefs.setString('$_indexPrefix$userId', jsonEncode(ids));
    await prefs.remove('$_sessionPrefix${userId}_$sessionId');
  }

  Future<void> clearAll(String userId) async {
    final prefs = await SharedPreferences.getInstance();
    final ids = _getIndex(prefs, userId);
    for (final id in ids) {
      await prefs.remove('$_sessionPrefix${userId}_$id');
    }
    await prefs.remove('$_indexPrefix$userId');
  }

  // ── Internals ─────────────────────────────────────────────────────────────

  List<String> _getIndex(SharedPreferences prefs, String userId) {
    final raw = prefs.getString('$_indexPrefix$userId');
    if (raw == null) return [];
    try {
      return (jsonDecode(raw) as List).cast<String>();
    } catch (_) {
      return [];
    }
  }

  ChatSession? _readSession(
      SharedPreferences prefs, String userId, String sessionId) {
    final raw = prefs.getString('$_sessionPrefix${userId}_$sessionId');
    if (raw == null) return null;
    try {
      final data = jsonDecode(raw) as Map<String, dynamic>;
      final msgs = (data['messages'] as List).map((e) {
        final m = e as Map<String, dynamic>;
        return ChatMessage(
          role: m['role'] as String,
          text: m['text'] as String,
          timestamp: DateTime.parse(m['timestamp'] as String),
        );
      }).toList();
      return ChatSession(
        id: sessionId,
        messages: msgs,
        createdAt: DateTime.parse(data['created_at'] as String),
      );
    } catch (_) {
      return null;
    }
  }
}
