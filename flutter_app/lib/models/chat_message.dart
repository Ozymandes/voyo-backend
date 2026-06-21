/// A single provenance pill shown under CLEO's answer (Tier 2 #3).
/// Mirrors the backend `SourceItem` {label, kind}. Lives in the model layer
/// so both `ChatMessage` and `CleoService` can reference it without a cycle.
class SourcePill {
  final String label; // e.g. "Karnak Temple", "OpenWeather (Luxor)"
  final String kind;   // "database" | "weather" | "web" | "image"
  const SourcePill({required this.label, required this.kind});

  factory SourcePill.fromJson(Map<String, dynamic> j) =>
      SourcePill(label: j['label'] as String, kind: j['kind'] as String);
}

class ChatMessage {
  final String role; // 'user' or 'assistant'
  final String text;
  final DateTime timestamp;
  // Provenance pills (Tier 2 #3). Only assistant messages grounded in tools
  // carry these; user messages and chitchat replies have an empty list.
  final List<SourcePill> sources;

  ChatMessage({
    required this.role,
    required this.text,
    required this.timestamp,
    this.sources = const [],
  });

  bool get isUser => role == 'user';
}
