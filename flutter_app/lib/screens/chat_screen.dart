import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../models/chat_message.dart';
import '../models/poi.dart';
import '../models/itinerary.dart';
import '../services/cleo_service.dart';
import '../services/chat_history_service.dart';
import '../services/supabase_service.dart';
import '../theme.dart';
import '../widgets/cleo_avatar.dart';
import '../widgets/trip_profile_sheet.dart';

/// Opens CLEO focused on a single POI: pushes [ChatScreen] with the POI id
/// (so the backend receives `poi_id` + `intent: "poi_explain"`) and a preset
/// question that auto-sends on open. Shared entry point for every POI surface.
void openCleoForPoi(BuildContext context, Poi poi) {
  Navigator.push(
    context,
    MaterialPageRoute(
      builder:
          (_) => ChatScreen(
            poiId: poi.id,
            presetMessage: 'Tell me about ${poi.name}',
          ),
    ),
  );
}

class ChatScreen extends StatefulWidget {
  const ChatScreen({
    super.key,
    this.onSwitchToPlanner,
    this.poiId,
    this.presetMessage,
  });

  final VoidCallback? onSwitchToPlanner;

  /// When set, every message carries `poi_id` + `intent: "poi_explain"` so
  /// CLEO answers with place context.
  final int? poiId;

  /// Sent automatically once when the screen opens (e.g. from a POI card).
  final String? presetMessage;

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final _cleoService = CleoService();
  final _historyService = ChatHistoryService();
  final _messages = <ChatMessage>[];
  final _controller = TextEditingController();
  final _scrollController = ScrollController();

  bool _isLoading = false;
  // Intent label for the loading indicator (Tier 1 #2). Drives which status
  // copy the typing indicator cycles while CLEO works.
  String _loadingIntent = 'general';
  bool _sidebarOpen = false;
  bool _didAutoSend = false;

  // Index of the last message that contained [PLANNER]
  int? _plannerPromptIndex;

  // Stops parsed from the last itinerary response
  List<_ParsedStop> _parsedStops = [];

  // The structured trip profile behind the last Plan-a-trip request, if
  // any. Captured in _sendItineraryRequest so the Import sheet can commit
  // it deterministically via /itinerary/plan (Option A safarny tie-in)
  // instead of the legacy fuzzy-keyword path. Null for purely
  // conversational plans → Import falls back to fuzzy match.
  TripProfile? _pendingProfile;

  // Current session — null until user sends first message
  String? _currentSessionId;

  // All sessions shown in sidebar
  List<ChatSession> _sessions = [];

  String? get _userId => Supabase.instance.client.auth.currentUser?.id;

  static const _starterChips = [
    'Best time to visit Luxor?',
    'Hidden gems in Cairo',
    'Cairo to Aswan — best route?',
    'What to eat in Alexandria?',
  ];

  @override
  void initState() {
    super.initState();
    _loadSessions();
    // Auto-send the preset (e.g. "Tell me about {POI}") once on open.
    if (widget.presetMessage != null) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted && !_didAutoSend && _messages.isEmpty && !_isLoading) {
          _didAutoSend = true;
          _send(widget.presetMessage);
        }
      });
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  // ── Data ──────────────────────────────────────────────────────────────────

  Future<void> _loadSessions() async {
    final uid = _userId;
    if (uid == null) return;
    final sessions = await _historyService.loadAllSessions(uid);
    if (mounted) setState(() => _sessions = sessions);
  }

  Future<void> _openSession(ChatSession session) async {
    setState(() {
      _sidebarOpen = false;
      _messages
        ..clear()
        ..addAll(session.messages);
      _currentSessionId = session.id;
    });
    WidgetsBinding.instance.addPostFrameCallback((_) => _scrollToBottom());
  }

  void _newChat() {
    setState(() {
      _sidebarOpen = false;
      _messages.clear();
      _currentSessionId = null;
    });
  }

  Future<void> _deleteSession(ChatSession session) async {
    final uid = _userId;
    if (uid == null) return;
    await _historyService.deleteSession(uid, session.id);
    // If we deleted the active session, start a new chat
    if (_currentSessionId == session.id) _newChat();
    await _loadSessions();
  }

  // ── Messaging ─────────────────────────────────────────────────────────────

  Future<void> _send([String? preset]) async {
    final text = preset ?? _controller.text.trim();
    if (text.isEmpty || _isLoading) return;

    _controller.clear();
    final uid = _userId ?? 'anonymous';

    // Classify the message so the loading indicator can show intent-aware
    // status copy (Tier 1 #2): itinerary prompts cycle through staged
    // planning states, POI prompts hint at DB verification, etc. Purely a
    // UI affordance — the backend classification is independent.
    final intent = _classifyLoadingIntent(text);

    // Create session on first message
    _currentSessionId ??= _historyService.newSessionId();

    final userMsg = ChatMessage(
      role: 'user',
      text: text,
      timestamp: DateTime.now(),
    );
    setState(() {
      _messages.add(userMsg);
      _isLoading = true;
      _loadingIntent = intent;
    });
    _scrollToBottom();
    if (uid != 'anonymous') {
      await _historyService.appendToSession(uid, _currentSessionId!, userMsg);
      await _loadSessions();
    }

    try {
      final result = await _cleoService.sendMessage(
        text,
        userId: uid,
        poiId: widget.poiId,
        intent: widget.poiId != null ? 'poi_explain' : null,
      );
      final raw = result.text;
      final hasPlanner = raw.contains('[PLANNER]');
      final reply = raw.replaceAll('[PLANNER]', '').trimRight();
      final stops = hasPlanner ? _parseItineraryStops(reply) : <_ParsedStop>[];
      final cleoMsg = ChatMessage(
        role: 'assistant',
        text: reply,
        timestamp: DateTime.now(),
        sources: result.sources,
      );
      setState(() {
        _messages.add(cleoMsg);
        if (hasPlanner) {
          _plannerPromptIndex = _messages.length - 1;
          _parsedStops = stops;
        }
        _isLoading = false;
      });
      if (uid != 'anonymous') {
        await _historyService.appendToSession(uid, _currentSessionId!, cleoMsg);
        await _loadSessions();
      }
    } catch (e) {
      setState(() {
        _messages.add(
          ChatMessage(
            role: 'assistant',
            // Never surface raw exception text to the user — backend logs
            // carry the technical detail. (General error-handling req.)
            text:
                'Cleo had trouble with that request. Please try again.',
            timestamp: DateTime.now(),
          ),
        );
        _isLoading = false;
      });
    }
    _scrollToBottom();
  }

  // ── Loading-intent classification (Tier 1 #2) ──────────────────────────
  // Lightweight keyword classifier that picks which staged status messages
  // the typing indicator should cycle while CLEO works. Mirrors the backend
  // itinerary trigger words so the UI feels in sync with what CLEO is doing.
  String _classifyLoadingIntent(String text) {
    final t = text.toLowerCase();
    const itineraryWords = [
      'itinerary',
      'plan',
      'schedule',
      'trip',
      'tour',
      'days',
      'day trip',
      'route',
      'optimize',
    ];
    const routeWords = [
      'route',
      'drive',
      'get there',
      'directions',
      'distance',
    ];
    if (itineraryWords.any((w) => t.contains(w))) return 'itinerary';
    if (routeWords.any((w) => t.contains(w))) return 'route';
    if (widget.poiId != null) return 'poi';
    return 'general';
  }

  /// Converts a structured [TripProfile] (from the Plan-a-trip sheet) into a
  /// natural-language planning prompt and sends it through the normal CLEO
  /// flow. Going through chat (rather than a raw JSON POST) keeps the request
  /// visible in history, lets CLEO ask follow-ups, and reuses the existing
  /// [PLANNER] → import-to-planner pipeline. The profile's structured fields
  /// are listed explicitly so CLEO's curate_itinerary tool receives concrete
  /// constraints to optimize against.
  void _sendItineraryRequest(TripProfile profile) {
    // Option A safarny tie-in: remember the structured profile so the
    // "Save to Planner" sheet can commit it deterministically via
    // /itinerary/plan (persist=true) instead of the legacy fuzzy-keyword
    // path. We still send the natural-language prompt to CLEO so the user
    // sees a conversational preview in chat; Safarny is the authoritative
    // committer on save. Cleared after a successful import.
    _pendingProfile = profile;
    final days = profile.dayCount;
    final buf = StringBuffer();
    if (days > 0) {
      buf.write('Plan a $days-day Egypt itinerary');
      final start = profile.startDate;
      final end = profile.endDate;
      if (start != null && end != null) {
        buf.write(
          ' from ${start.day}/${start.month} to ${end.day}/${end.month}',
        );
      }
      buf.write('. ');
    } else {
      buf.write('Plan an Egypt itinerary. ');
    }
    buf.write(
      '${profile.travelers} traveller'
      '${profile.travelers == 1 ? '' : 's'}, ',
    );
    buf.write('${_budgetLabel(profile.budgetTier)} budget, ');
    buf.write('${_paceLabel(profile.pace)} pace, ');
    buf.write('travelling as ${profile.companions}. ');
    if (profile.interests.isNotEmpty) {
      buf.write('Interests: ${profile.interests.join(', ')}. ');
    }
    if (profile.notes != null && profile.notes!.trim().isNotEmpty) {
      buf.write('Additional notes: ${profile.notes!.trim()} ');
    }
    buf.write(
      'Use real attractions from your database and optimize the '
      'route so the days are geographically realistic.',
    );
    _send(buf.toString());
  }

  static String _budgetLabel(String tier) =>
      const {
        'budget': 'budget-conscious',
        'moderate': 'moderate',
        'luxury': 'luxury',
      }[tier] ??
      'moderate';

  static String _paceLabel(String pace) =>
      const {
        'packed_schedule': 'packed',
        'balanced': 'balanced',
        'slow_flexible': 'relaxed',
      }[pace] ??
      'balanced';

  // ── Itinerary parsing ──────────────────────────────────────────────────────

  List<_ParsedStop> _parseItineraryStops(String text) {
    final stops = <_ParsedStop>[];
    int currentDay = 1;
    String currentTime = '09:00:00';

    // Imperative verbs that start tips/guidelines, not place names
    const tipVerbs = {
      'wear',
      'pack',
      'avoid',
      'stay',
      'drink',
      'bring',
      'book',
      'check',
      'note',
      'consider',
      'remember',
      'tip',
      'tips',
      'try',
      'use',
      'take',
      'get',
      'be',
      'make',
      'do',
      "don't",
      'always',
      'never',
      'ensure',
      'plan',
      'hire',
      'head',
      'walk',
      'go',
      'start',
      'stop',
      'keep',
      'carry',
      'watch',
      'ask',
      'buy',
      'eat',
      'have',
      'grab',
      'spend',
      'enjoy',
      'relax',
      'explore',
      'return',
      'end',
      'finish',
      'begin',
      'continue',
      'haggle',
      'bargain',
      'negotiate',
      'dress',
      'cover',
      'respect',
      'travel',
      'learn',
      'visit',
      'see',
      'find',
      'follow',
      'opt',
      'choose',
      'select',
      'pick',
      'arrange',
      'prepare',
    };

    // Words that indicate dining/food rather than a site
    const skipWords = [
      'restaurant',
      'dinner',
      'lunch',
      'breakfast',
      'café',
      'cafe',
      'street food',
      'rooftop bar',
      'hotel restaurant',
      "ta'meya",
      'ful ',
      'shawarma',
      'koshary',
      'koshari',
    ];

    for (final raw in text.split('\n')) {
      final line = raw.trim();

      // Day header: Day 1, **Day 1**, Day 1 —
      final dayMatch = RegExp(r'\bDay (\d+)\b').firstMatch(line);
      if (dayMatch != null) {
        currentDay = int.parse(dayMatch.group(1)!);
        currentTime = '09:00:00';
        continue;
      }

      // Time slot
      final lower = line.toLowerCase();
      if (lower.contains('morning')) {
        currentTime = '09:00:00';
      } else if (lower.contains('lunch')) {
        currentTime = '12:30:00';
      } else if (lower.contains('afternoon')) {
        currentTime = '13:00:00';
      } else if (lower.contains('evening')) {
        currentTime = '18:30:00';
      }

      // Bullet point only — require a space after * so **Bold Headers** are not matched
      final isBullet =
          line.startsWith('• ') ||
          line.startsWith('- ') ||
          line.startsWith('* ') ||
          line.startsWith('• ');
      if (!isBullet) {
        continue;
      }

      final withoutBullet = line.replaceFirst(RegExp(r'^[•\-\*]\s*'), '');
      // Strip all asterisks and hashes (markdown bold/header remnants)
      final clean = withoutBullet.replaceAll(RegExp(r'[\*#]'), '');
      // Take only text before em-dash, en-dash, colon, or parenthesis
      final dashIdx = clean.indexOf(RegExp(r'[—–:(]'));
      final name = (dashIdx > 0 ? clean.substring(0, dashIdx) : clean).trim();

      if (name.length <= 3) {
        continue;
      }

      // Must contain at least one capital letter — place names always do;
      // tip sentences that slipped through are usually all-lowercase.
      if (!name.contains(RegExp(r'[A-Z]'))) {
        continue;
      }

      // Skip section labels like "Travel Tips", "Important Notes", "General Tips"
      final nameLower = name.toLowerCase();
      if (nameLower.contains('tip') ||
          nameLower.contains('note') ||
          nameLower.contains('guideline') ||
          nameLower.contains('advice') ||
          nameLower.contains('reminder') ||
          nameLower.contains('warning')) {
        continue;
      }

      // Skip if first word is a tip/action verb
      final firstWord = name
          .split(RegExp(r'\s+'))
          .first
          .toLowerCase()
          .replaceAll(RegExp(r"[^a-z']"), '');
      if (tipVerbs.contains(firstWord)) {
        continue;
      }

      // Skip dining/food entries
      if (skipWords.any((w) => name.toLowerCase().contains(w))) {
        continue;
      }

      stops.add(_ParsedStop(day: currentDay, name: name, time: currentTime));
    }
    return stops;
  }

  // ── Import sheet ───────────────────────────────────────────────────────────

  void _showImportSheet() {
    if (_parsedStops.isEmpty) {
      widget.onSwitchToPlanner?.call();
      return;
    }
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder:
          (_) => _ImportStopsSheet(
            stops: _parsedStops,
            userId: _userId ?? '',
            profile: _pendingProfile,
            onImported: () {
              // Clear the pending profile only after a successful import —
              // so a failed save can retry the deterministic path.
              if (_pendingProfile != null) {
                _pendingProfile = null;
              }
              widget.onSwitchToPlanner?.call();
            },
          ),
    );
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  // ── Build ─────────────────────────────────────────────────────────────────

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: VoyoColors.page,
      body: Stack(
        children: [
          // ── Main chat area ──
          Column(
            children: [
              _buildAppBar(),
              Expanded(
                child:
                    _messages.isEmpty
                        ? _buildEmptyState()
                        : _buildMessageList(),
              ),
              if (_isLoading) _TypingIndicator(intent: _loadingIntent),
              if (_messages.length < 3) _buildStarterChips(),
              _buildInputBar(),
            ],
          ),

          // ── Sidebar barrier ──
          AnimatedOpacity(
            opacity: _sidebarOpen ? 1.0 : 0.0,
            duration: const Duration(milliseconds: 220),
            child: IgnorePointer(
              ignoring: !_sidebarOpen,
              child: GestureDetector(
                onTap: () => setState(() => _sidebarOpen = false),
                child: Container(color: Colors.black.withValues(alpha: 0.5)),
              ),
            ),
          ),

          // ── Sidebar ──
          Align(
            alignment: Alignment.centerLeft,
            child: AnimatedSlide(
              offset: _sidebarOpen ? Offset.zero : const Offset(-1, 0),
              duration: const Duration(milliseconds: 280),
              curve: Curves.easeInOut,
              child: _buildSidebar(),
            ),
          ),
        ],
      ),
    );
  }

  // ── AppBar ────────────────────────────────────────────────────────────────

  Widget _buildAppBar() {
    final canPop = Navigator.of(context).canPop();
    return SafeArea(
      bottom: false,
      child: Container(
        height: 56,
        color: VoyoColors.paper,
        child: Column(
          children: [
            Expanded(
              child: Row(
                children: [
                  // Sidebar toggle — or back arrow when pushed over another screen
                  GestureDetector(
                    onTap: () {
                      if (canPop) {
                        Navigator.of(context).maybePop();
                      } else {
                        setState(() => _sidebarOpen = true);
                      }
                    },
                    child: Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      child: Icon(
                        canPop ? Icons.arrow_back : Icons.menu,
                        color: VoyoColors.ink,
                        size: 22,
                      ),
                    ),
                  ),
                  const CleoAvatar(size: 30),
                  const SizedBox(width: 8),
                  Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Cleo',
                        style: GoogleFonts.fraunces(
                          fontSize: 19,
                          fontStyle: FontStyle.italic,
                          color: VoyoColors.ink,
                        ),
                      ),
                      Text(
                        'AI Guide · Egypt Expert',
                        style: GoogleFonts.instrumentSans(
                          fontSize: 10,
                          color: VoyoColors.stone,
                        ),
                      ),
                    ],
                  ),
                  const Spacer(),
                  // New chat
                  GestureDetector(
                    onTap: _newChat,
                    child: Container(
                      margin: const EdgeInsets.only(right: 14),
                      width: 32,
                      height: 32,
                      decoration: BoxDecoration(
                        color: VoyoColors.expedition,
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(
                        Icons.add,
                        color: Colors.white,
                        size: 18,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            Container(height: 1, color: VoyoColors.smoke),
          ],
        ),
      ),
    );
  }

  // ── Sidebar ───────────────────────────────────────────────────────────────

  Widget _buildSidebar() {
    // Group sessions by date bucket
    final now = DateTime.now();
    final today = <ChatSession>[];
    final yesterday = <ChatSession>[];
    final week = <ChatSession>[];
    final older = <ChatSession>[];

    for (final s in _sessions) {
      final diff = now.difference(s.createdAt).inDays;
      if (diff == 0) {
        today.add(s);
      } else if (diff == 1) {
        yesterday.add(s);
      } else if (diff <= 7) {
        week.add(s);
      } else {
        older.add(s);
      }
    }

    return SizedBox(
      width: 285,
      height: double.infinity,
      child: Material(
        color: const Color(0xFF1A1714), // ink
        child: SafeArea(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 16, 12, 12),
                child: Row(
                  children: [
                    const CleoAvatar(size: 28),
                    const SizedBox(width: 10),
                    Text(
                      'Cleo',
                      style: GoogleFonts.fraunces(
                        fontSize: 20,
                        fontStyle: FontStyle.italic,
                        color: Colors.white,
                      ),
                    ),
                    const Spacer(),
                    GestureDetector(
                      onTap: () => setState(() => _sidebarOpen = false),
                      child: const Icon(
                        Icons.close,
                        color: Color(0xFF6A6058),
                        size: 20,
                      ),
                    ),
                  ],
                ),
              ),

              // New Chat button
              Padding(
                padding: const EdgeInsets.fromLTRB(12, 0, 12, 12),
                child: GestureDetector(
                  onTap: _newChat,
                  child: Container(
                    width: double.infinity,
                    padding: const EdgeInsets.symmetric(vertical: 11),
                    decoration: BoxDecoration(
                      color: VoyoColors.expedition,
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(Icons.add, color: Colors.white, size: 16),
                        const SizedBox(width: 6),
                        Text(
                          'New Chat',
                          style: GoogleFonts.instrumentSans(
                            fontSize: 13,
                            fontWeight: FontWeight.w600,
                            color: Colors.white,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),

              // Session list
              Expanded(
                child:
                    _sessions.isEmpty
                        ? Center(
                          child: Text(
                            'No conversations yet.',
                            style: GoogleFonts.instrumentSans(
                              fontSize: 13,
                              color: const Color(0xFF6A6058),
                            ),
                          ),
                        )
                        : ListView(
                          padding: const EdgeInsets.only(bottom: 16),
                          children: [
                            if (today.isNotEmpty) ...[
                              _sectionLabel('Today'),
                              ...today.map(_sessionTile),
                            ],
                            if (yesterday.isNotEmpty) ...[
                              _sectionLabel('Yesterday'),
                              ...yesterday.map(_sessionTile),
                            ],
                            if (week.isNotEmpty) ...[
                              _sectionLabel('Last 7 days'),
                              ...week.map(_sessionTile),
                            ],
                            if (older.isNotEmpty) ...[
                              _sectionLabel('Older'),
                              ...older.map(_sessionTile),
                            ],
                          ],
                        ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _sectionLabel(String label) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 14, 16, 4),
      child: Text(
        label,
        style: GoogleFonts.instrumentSans(
          fontSize: 11,
          fontWeight: FontWeight.w600,
          color: const Color(0xFF4A4440),
          letterSpacing: 0.5,
        ),
      ),
    );
  }

  Widget _sessionTile(ChatSession session) {
    final isActive = session.id == _currentSessionId;
    return GestureDetector(
      onTap: () => _openSession(session),
      child: Container(
        margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 1),
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 10),
        decoration: BoxDecoration(
          color: isActive ? const Color(0xFF2A2420) : Colors.transparent,
          borderRadius: BorderRadius.circular(8),
        ),
        child: Row(
          children: [
            Expanded(
              child: Text(
                session.title,
                style: GoogleFonts.instrumentSans(
                  fontSize: 13,
                  color: isActive ? Colors.white : const Color(0xFFB0A898),
                  fontWeight: isActive ? FontWeight.w500 : FontWeight.w400,
                ),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
            ),
            const SizedBox(width: 6),
            GestureDetector(
              onTap: () => _deleteSession(session),
              child: const Icon(
                Icons.close,
                size: 14,
                color: Color(0xFF4A4440),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ── Chat UI ───────────────────────────────────────────────────────────────

  Widget _buildEmptyState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const CleoAvatar(size: 80),
            const SizedBox(height: 20),
            Text(
              'Your itinerary is waiting.',
              style: GoogleFonts.fraunces(
                fontSize: 26,
                fontStyle: FontStyle.italic,
                color: VoyoColors.ink,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 8),
            Text(
              'Ask me anything about Egypt — attractions, history, what to eat, when to go.',
              style: GoogleFonts.instrumentSans(
                fontSize: 14,
                color: VoyoColors.stone,
                height: 1.5,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),
            // Primary CTA: opens the trip-profile sheet so CLEO can generate a
            // grounded, route-optimized itinerary from structured inputs
            // (dates, budget, style, pace) rather than a vague chat prompt.
            FilledButton.icon(
              onPressed: () async {
                final profile = await showTripProfileSheet(context);
                if (profile == null || !mounted) return;
                _sendItineraryRequest(profile);
              },
              style: FilledButton.styleFrom(
                backgroundColor: VoyoColors.expedition,
                padding: const EdgeInsets.symmetric(
                  horizontal: 22,
                  vertical: 14,
                ),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(14),
                ),
              ),
              icon: const Icon(
                Icons.auto_awesome_rounded,
                size: 18,
                color: Colors.white,
              ),
              label: Text(
                'Plan a trip',
                style: GoogleFonts.instrumentSans(
                  fontSize: 15,
                  fontWeight: FontWeight.w700,
                  color: Colors.white,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMessageList() {
    return ListView.builder(
      controller: _scrollController,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      itemCount: _messages.length,
      itemBuilder: (_, i) => _buildMessage(_messages[i]),
    );
  }

  Widget _buildMessage(ChatMessage msg) {
    if (msg.isUser) {
      return Align(
        alignment: Alignment.centerRight,
        child: Container(
          margin: const EdgeInsets.only(top: 12, left: 48),
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          decoration: BoxDecoration(
            color: VoyoColors.vellum,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: VoyoColors.smoke),
          ),
          child: Text(
            msg.text,
            style: GoogleFonts.instrumentSans(
              fontSize: 14,
              color: VoyoColors.ink,
              height: 1.5,
            ),
          ),
        ),
      );
    }

    final (followUps, withoutJson) = _extractFollowUps(msg.text);
    final cleanedText = _stripImages(withoutJson);
    final (first, rest) = _splitFirstSentence(cleanedText);
    final msgIndex = _messages.indexOf(msg);
    // Show the planner CTA only on the message that produced an actual
    // [PLANNER] token. The token itself is stripped from msg.text before
    // storage (see _sendMessage), so we gate purely on the index —
    // _plannerPromptIndex is only ever assigned when hasPlanner was true.
    // (P0 #2: "Open Planner" appearing on every response.)
    final showPlannerButton =
        msgIndex != -1 && msgIndex == _plannerPromptIndex;

    return Padding(
      padding: const EdgeInsets.only(top: 16, bottom: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const CleoAvatar(size: 32),
          const SizedBox(width: 11),
          Expanded(
            child: Container(
              padding: const EdgeInsets.only(left: 14),
              decoration: const BoxDecoration(
                border: Border(
                  left: BorderSide(color: VoyoColors.sky, width: 3),
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildInlineMarkdown(
                    first,
                    GoogleFonts.fraunces(
                      fontSize: 16,
                      fontStyle: FontStyle.italic,
                      color: VoyoColors.ink,
                      height: 1.55,
                    ),
                  ),
                  if (rest.isNotEmpty) ...[
                    const SizedBox(height: 6),
                    MarkdownBody(
                      data: rest,
                      shrinkWrap: true,
                      styleSheet: _cleoMarkdownStyle,
                    ),
                  ],
                  if (showPlannerButton) ...[
                    const SizedBox(height: 14),
                    FilledButton.icon(
                      onPressed: _showImportSheet,
                      style: FilledButton.styleFrom(
                        backgroundColor: VoyoColors.terra,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(10),
                        ),
                        padding: const EdgeInsets.symmetric(
                          horizontal: 16,
                          vertical: 10,
                        ),
                      ),
                      icon: const Icon(
                        Icons.calendar_today_rounded,
                        size: 15,
                        color: Colors.white,
                      ),
                      label: Text(
                        'Open Planner',
                        style: GoogleFonts.instrumentSans(
                          fontSize: 13,
                          fontWeight: FontWeight.w600,
                          color: Colors.white,
                        ),
                      ),
                    ),
                  ],
                  if (msg.sources.isNotEmpty) ...[
                    const SizedBox(height: 12),
                    _buildSourcePills(msg.sources),
                  ],
                  if (followUps.isNotEmpty) ...[
                    const SizedBox(height: 12),
                    _buildFollowUpChips(followUps),
                  ],
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  /// Provenance pills shown under a grounded CLEO answer (Tier 2 #3).
  ///
  /// Each pill reflects a tool/source that actually fed the answer — DB rows
  /// (named POIs or "VOYO verified database"), live weather, or web search.
  /// This is what makes CLEO's "verified" claim honest: the user can see the
  /// basis. Empty for chitchat. The kind drives the icon + accent colour.
  Widget _buildSourcePills(List<SourcePill> sources) {
    return Wrap(
      spacing: 6,
      runSpacing: 6,
      crossAxisAlignment: WrapCrossAlignment.center,
      children: [
        Text(
          'Sources',
          style: GoogleFonts.instrumentSans(
            fontSize: 10,
            fontWeight: FontWeight.w600,
            color: VoyoColors.stone,
            letterSpacing: 0.4,
          ),
        ),
        ...sources.map(_sourcePill),
      ],
    );
  }

  Widget _sourcePill(SourcePill s) {
    final (icon, accent) = _sourceStyle(s.kind);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: accent.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: accent.withValues(alpha: 0.35)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 11, color: accent),
          const SizedBox(width: 4),
          Text(
            s.label,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: GoogleFonts.instrumentSans(
              fontSize: 11,
              fontWeight: FontWeight.w500,
              color: VoyoColors.ink,
            ),
          ),
        ],
      ),
    );
  }

  (IconData, Color) _sourceStyle(String kind) {
    switch (kind) {
      case 'database':
        return (Icons.verified_rounded, VoyoColors.verified);
      case 'weather':
        return (Icons.cloud_outlined, VoyoColors.sky);
      case 'web':
        return (Icons.language_rounded, VoyoColors.discovery);
      case 'image':
        return (Icons.image_outlined, VoyoColors.caution);
      default:
        return (Icons.source_outlined, VoyoColors.stone);
    }
  }

  /// Renders a single line with **bold** spans, stripping header prefixes.
  /// Used for the italic hook sentence so bold still shows inside Fraunces italic.
  Widget _buildInlineMarkdown(String text, TextStyle base) {
    final cleaned =
        text.replaceAll(RegExp(r'^#+\s*', multiLine: true), '').trim();
    final spans = <InlineSpan>[];
    final boldRe = RegExp(r'\*\*(.+?)\*\*');
    int cursor = 0;
    for (final m in boldRe.allMatches(cleaned)) {
      if (m.start > cursor) {
        spans.add(
          TextSpan(text: cleaned.substring(cursor, m.start), style: base),
        );
      }
      spans.add(
        TextSpan(
          text: m.group(1),
          style: base.copyWith(fontWeight: FontWeight.w700),
        ),
      );
      cursor = m.end;
    }
    if (cursor < cleaned.length) {
      spans.add(TextSpan(text: cleaned.substring(cursor), style: base));
    }
    return RichText(text: TextSpan(children: spans));
  }

  /// Splits a trailing ```json {"follow_ups":[...]} ``` block off an assistant
  /// message, returning the chip labels and the markdown body with it removed.
  (List<String>, String) _extractFollowUps(String text) {
    final re = RegExp(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```\s*$');
    final m = re.firstMatch(text);
    if (m == null) return (<String>[], text);
    try {
      final obj = jsonDecode(m.group(1)!) as Map<String, dynamic>;
      final raw = obj['follow_ups'];
      if (raw is List) {
        final ups =
            raw
                .map((e) => e.toString().trim())
                .where((s) => s.isNotEmpty)
                .toList();
        if (ups.isEmpty) return (<String>[], text);
        return (ups, text.substring(0, m.start).trimRight());
      }
    } catch (_) {}
    return (<String>[], text);
  }

  /// Strips markdown image syntax (`![alt](url)`) from a CLEO response so no
  /// network image requests are triggered on render. Wikimedia Commons
  /// rate-limits (HTTP 429) bulk image fetches — and CLEO's RAG responses can
  /// reference dozens at once — so we render text only. Reference images are
  /// out of scope until image hosting is reliable.
  String _stripImages(String text) {
    // Match `![…](…)` image markdown. Alt text is matched non-greedily up to
    // the final `](` so alt text containing brackets is still stripped.
    return text
        .replaceAll(RegExp(r'!\[[^\]]*(?:\][^\]]*)*\]\([^)]+\)'), '')
        .replaceAll(RegExp(r'\n{3,}'), '\n\n')
        .trim();
  }

  Widget _buildFollowUpChips(List<String> followUps) {
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: [
        for (final up in followUps)
          GestureDetector(
            onTap: _isLoading ? null : () => _send(up),
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 7),
              decoration: BoxDecoration(
                color: VoyoColors.paper,
                borderRadius: BorderRadius.circular(20),
                border: Border.all(
                  color: VoyoColors.sky.withValues(alpha: 0.4),
                ),
              ),
              child: Text(
                up,
                style: GoogleFonts.instrumentSans(
                  fontSize: 12,
                  color: VoyoColors.sky,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
          ),
      ],
    );
  }

  static final _bodyStyle = GoogleFonts.instrumentSans(
    fontSize: 14,
    color: VoyoColors.stone,
    height: 1.65,
  );

  /// Shared MarkdownStyleSheet for all CLEO body text.
  /// Headers are the same size as body — only bold weight distinguishes them.
  static final _cleoMarkdownStyle = MarkdownStyleSheet(
    p: _bodyStyle,
    strong: _bodyStyle.copyWith(
      fontWeight: FontWeight.w700,
      color: VoyoColors.ink,
    ),
    em: _bodyStyle.copyWith(fontStyle: FontStyle.italic),
    // Headers same size as body — just bold, no visual hierarchy of sizes
    h1: _bodyStyle.copyWith(fontWeight: FontWeight.w700, color: VoyoColors.ink),
    h2: _bodyStyle.copyWith(fontWeight: FontWeight.w700, color: VoyoColors.ink),
    h3: _bodyStyle.copyWith(fontWeight: FontWeight.w600, color: VoyoColors.ink),
    h4: _bodyStyle.copyWith(fontWeight: FontWeight.w600, color: VoyoColors.ink),
    listBullet: _bodyStyle,
    blockSpacing: 6,
    listIndent: 16,
    pPadding: const EdgeInsets.only(bottom: 2),
    h1Padding: const EdgeInsets.only(top: 8, bottom: 2),
    h2Padding: const EdgeInsets.only(top: 6, bottom: 2),
    h3Padding: const EdgeInsets.only(top: 4, bottom: 2),
  );

  Widget _buildStarterChips() {
    return Container(
      color: VoyoColors.page,
      padding: const EdgeInsets.fromLTRB(12, 8, 12, 0),
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: Row(
          children:
              _starterChips.map((chip) {
                return Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: GestureDetector(
                    onTap: () => _send(chip),
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 14,
                        vertical: 8,
                      ),
                      decoration: BoxDecoration(
                        color: VoyoColors.paper,
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(
                          color: VoyoColors.sky.withValues(alpha: 0.4),
                        ),
                      ),
                      child: Text(
                        chip,
                        style: GoogleFonts.instrumentSans(
                          fontSize: 13,
                          color: VoyoColors.sky,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ),
                  ),
                );
              }).toList(),
        ),
      ),
    );
  }

  Widget _buildInputBar() {
    return Container(
      color: VoyoColors.paper,
      padding: const EdgeInsets.fromLTRB(12, 10, 12, 10),
      child: SafeArea(
        top: false,
        child: Row(
          children: [
            Expanded(
              child: TextField(
                controller: _controller,
                textInputAction: TextInputAction.send,
                onSubmitted: (_) => _send(),
                style: GoogleFonts.instrumentSans(
                  color: VoyoColors.ink,
                  fontSize: 14,
                ),
                decoration: InputDecoration(
                  hintText: 'Ask Cleo anything…',
                  hintStyle: GoogleFonts.instrumentSans(
                    color: VoyoColors.stone,
                    fontSize: 14,
                  ),
                  filled: true,
                  fillColor: VoyoColors.vellum,
                  contentPadding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 12,
                  ),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(24),
                    borderSide: BorderSide.none,
                  ),
                  enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(24),
                    borderSide: BorderSide.none,
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(24),
                    borderSide: const BorderSide(
                      color: VoyoColors.sky,
                      width: 1.5,
                    ),
                  ),
                ),
              ),
            ),
            const SizedBox(width: 8),
            ValueListenableBuilder<TextEditingValue>(
              valueListenable: _controller,
              builder: (_, value, _) {
                final hasText = value.text.trim().isNotEmpty;
                return GestureDetector(
                  onTap: _isLoading ? null : _send,
                  child: AnimatedContainer(
                    duration: const Duration(milliseconds: 200),
                    width: 42,
                    height: 42,
                    decoration: BoxDecoration(
                      color: hasText ? VoyoColors.sky : VoyoColors.smoke,
                      shape: BoxShape.circle,
                    ),
                    child: Icon(
                      Icons.arrow_upward_rounded,
                      color: hasText ? Colors.white : VoyoColors.stone,
                      size: 20,
                    ),
                  ),
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}

// ── Helpers ───────────────────────────────────────────────────────────────

(String, String) _splitFirstSentence(String text) {
  for (final sep in ['. ', '! ', '? ', '.\n']) {
    final idx = text.indexOf(sep);
    if (idx != -1 && idx < 160) {
      return (
        text.substring(0, idx + 1),
        text.substring(idx + sep.length).trim(),
      );
    }
  }
  return (text, '');
}

// ── Parsed stop model ─────────────────────────────────────────────────────

class _ParsedStop {
  final int day;
  final String name;
  final String time; // "HH:MM:00"

  const _ParsedStop({
    required this.day,
    required this.name,
    required this.time,
  });
}

// ── Import stops sheet ────────────────────────────────────────────────────

class _ImportStopsSheet extends StatefulWidget {
  final List<_ParsedStop> stops;
  final String userId;
  final VoidCallback onImported;
  // Option A safarny tie-in: when present, _save() commits the
  // deterministic plan via /itinerary/plan instead of the fuzzy path.
  // Null = purely conversational plan → legacy fuzzy match (kept as a
  // fallback so a chat-only plan still imports).
  final TripProfile? profile;

  const _ImportStopsSheet({
    required this.stops,
    required this.userId,
    required this.onImported,
    this.profile,
  });

  @override
  State<_ImportStopsSheet> createState() => _ImportStopsSheetState();
}

class _ImportStopsSheetState extends State<_ImportStopsSheet> {
  final _service = SupabaseService();
  late final TextEditingController _titleCtrl;
  bool _saving = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    final days =
        widget.stops.isEmpty
            ? 0
            : widget.stops.map((s) => s.day).reduce((a, b) => a > b ? a : b);
    _titleCtrl = TextEditingController(text: '$days-Day Egypt Trip');
  }

  @override
  void dispose() {
    _titleCtrl.dispose();
    super.dispose();
  }

  Map<int, List<_ParsedStop>> get _byDay {
    final map = <int, List<_ParsedStop>>{};
    for (final s in widget.stops) {
      map.putIfAbsent(s.day, () => []).add(s);
    }
    return map;
  }

  String _fmt(String time) {
    final parts = time.split(':');
    final h = int.parse(parts[0]);
    final m = parts[1];
    final period = h >= 12 ? 'PM' : 'AM';
    final disp = h > 12 ? h - 12 : (h == 0 ? 12 : h);
    return '$disp:$m $period';
  }

  // Try to match a stop name to a POI in the DB.
  // First tries the full name, then falls back to individual keywords.
  Future<int?> _findPoiId(String name) async {
    final full = await _service.searchPois(name);
    if (full.isNotEmpty) return full.first.id as int?;

    const stopWords = {
      'the',
      'of',
      'el',
      'al',
      'in',
      'at',
      'and',
      'a',
      'an',
      'to',
    };
    final words =
        name
            .split(RegExp(r'\s+'))
            .where((w) => w.length > 3 && !stopWords.contains(w.toLowerCase()))
            .toList();

    for (final word in words) {
      final results = await _service.searchPois(word);
      if (results.isNotEmpty) return results.first.id as int?;
    }
    return null;
  }

  Future<void> _save() async {
    setState(() {
      _saving = true;
      _error = null;
    });
    // Capture the user-entered title up-front — both the profile path
    // and the legacy path should respect it. (Demo fix: user typed
    // 'MY ISLAMIC CAIRO' but the saved itinerary showed '2-day Egypt Trip'
    // because the profile path ignored _titleCtrl and fell back to
    // profile.title ?? default.)
    final userTitle = _titleCtrl.text.trim();
    print('[IMPORT-SAVE] start  profile=${widget.profile != null}  '
        'stops=${widget.stops.length}  title=${userTitle.isEmpty ? "(empty)" : userTitle}');
    try {
      // Option A safarny tie-in: if this plan came from a structured
      // TripProfile (the "Plan a trip" sheet), commit it via the
      // deterministic /itinerary/plan endpoint with persist=true. Safarny
      // selects POIs from the recommendation pool, VROOM assigns real
      // times, and tips land in itinerary_items.notes — so the planner
      // page renders the real plan, not a lossy parse of CLEO's chat reply.
      // CLEO's displayed stops become a conversational preview; Safarny is
      // the authoritative committer. The two may differ slightly (both draw
      // from the same candidate pool) — that is the thesis-aligned tradeoff.
      if (widget.profile != null) {
        // Override the profile's title with whatever the user entered in
        // the import sheet — the user's explicit choice wins over the
        // auto-generated profile title. (Demo fix: user typed
        // 'MY ISLAMIC CAIRO' but saved itinerary showed '2-day Egypt Trip'.)
        final profile = userTitle.isEmpty
            ? widget.profile!
            : TripProfile(
                title: userTitle,
                startDate: widget.profile!.startDate,
                endDate: widget.profile!.endDate,
                travelers: widget.profile!.travelers,
                budgetTier: widget.profile!.budgetTier,
                pace: widget.profile!.pace,
                companions: widget.profile!.companions,
                interests: widget.profile!.interests,
                notes: widget.profile!.notes,
              );
        print('[IMPORT-SAVE] profile path → /itinerary/plan  title=${profile.title}');
        final id = await _service.planAndSaveItinerary(
          userId: widget.userId,
          profile: profile,
        );
        if (id == null) {
          throw Exception(
            'Not signed in — could not commit the plan. Please sign in and try again.',
          );
        }
        print('[IMPORT-SAVE] profile path OK  id=$id');
        if (mounted) {
          Navigator.pop(context);
          widget.onImported();
        }
        return;
      }

      // Legacy path: purely conversational plan (no structured profile).
      // Kept as a fallback so a chat-only itinerary still imports. Creates
      // a bare itinerary + fuzzy-matches POI names. Tips/VROOM times are
      // NOT written here — that gap is what the profile path above fixes.
      final title =
          userTitle.isEmpty
              ? '${widget.stops.map((s) => s.day).reduce((a, b) => a > b ? a : b)}-Day Egypt Trip'
              : userTitle;
      print('[IMPORT-SAVE] legacy path  title=$title');
      Itinerary? itinerary = await _service.createItinerary(
        userId: widget.userId,
        title: title,
      );
      if (itinerary == null) throw Exception('Could not create itinerary');
      print('[IMPORT-SAVE] itinerary created id=${itinerary.id}');

      // Add each stop, using fuzzy keyword fallback to find a matching POI
      for (final stop in widget.stops) {
        final poiId = await _findPoiId(stop.name);
        print('[IMPORT-SAVE]   stop="${stop.name}" day=${stop.day} → poiId=$poiId');

        await _service.addItineraryItem(
          itineraryId: itinerary.id,
          poiId: poiId,
          customTitle: poiId == null ? stop.name : null,
          dayNumber: stop.day,
          startTime: stop.time,
        );
      }
      print('[IMPORT-SAVE] legacy path OK');

      if (mounted) {
        Navigator.pop(context);
        widget.onImported();
      }
    } catch (e) {
      if (mounted)
        setState(() {
          // User-safe message, but include the exception type + first
          // 120 chars in DEBUG builds so demo-night failures are
          // diagnosable without a debugger attached. (Temporary —
          // once the save path is stable, drop to the polished message.)
          final raw = e.toString();
          String safe;
          if (raw.contains('HTTP 401') || raw.contains('HTTP 403')) {
            safe = 'Please sign in again to save your plan.';
          } else if (raw.contains('foreign key')) {
            safe = 'Account setup incomplete. Try signing out and back in.';
          } else {
            // Include the real error so we can see tonight what failed.
            safe = 'Could not save: $raw'.substring(0, (raw.length > 120 ? 120 : raw.length));
          }
          _error = safe;
          _saving = false;
        });
    }
  }

  @override
  Widget build(BuildContext context) {
    final byDay = _byDay;
    final days = byDay.keys.toList()..sort();
    final screenH = MediaQuery.of(context).size.height;

    return Container(
      height: screenH * 0.85,
      decoration: const BoxDecoration(
        color: VoyoColors.page,
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      child: Column(
        children: [
          // Handle
          Padding(
            padding: const EdgeInsets.only(top: 12, bottom: 4),
            child: Container(
              width: 36,
              height: 4,
              decoration: BoxDecoration(
                color: VoyoColors.smoke,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),
          // Header
          Padding(
            padding: const EdgeInsets.fromLTRB(20, 8, 16, 12),
            child: Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Save to Planner',
                        style: GoogleFonts.fraunces(
                          fontSize: 22,
                          fontStyle: FontStyle.italic,
                          color: VoyoColors.ink,
                        ),
                      ),
                    ],
                  ),
                ),
                GestureDetector(
                  onTap: () => Navigator.pop(context),
                  child: const Icon(
                    Icons.close,
                    size: 20,
                    color: VoyoColors.stone,
                  ),
                ),
              ],
            ),
          ),
          Container(height: 1, color: VoyoColors.smoke),
          // Trip name field
          Padding(
            padding: const EdgeInsets.fromLTRB(20, 14, 20, 4),
            child: TextField(
              controller: _titleCtrl,
              style: GoogleFonts.instrumentSans(
                color: VoyoColors.ink,
                fontSize: 14,
              ),
              decoration: InputDecoration(
                labelText: 'Trip name',
                labelStyle: GoogleFonts.instrumentSans(
                  fontSize: 12,
                  color: VoyoColors.stone,
                ),
                prefixIcon: const Icon(
                  Icons.luggage_outlined,
                  color: VoyoColors.stone,
                  size: 18,
                ),
                filled: true,
                fillColor: VoyoColors.vellum,
                contentPadding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 12,
                ),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide.none,
                ),
                enabledBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide.none,
                ),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: const BorderSide(
                    color: VoyoColors.terra,
                    width: 1.5,
                  ),
                ),
              ),
            ),
          ),
          Padding(
            padding: const EdgeInsets.fromLTRB(20, 2, 20, 8),
            child: Align(
              alignment: Alignment.centerLeft,
              child: Text(
                '${widget.stops.length} stops across ${_byDay.keys.length} days',
                style: GoogleFonts.instrumentSans(
                  fontSize: 12,
                  color: VoyoColors.stone,
                ),
              ),
            ),
          ),
          Container(height: 1, color: VoyoColors.smoke),
          // Stop list
          Expanded(
            child: ListView(
              padding: const EdgeInsets.symmetric(vertical: 8),
              children: [
                for (final day in days) ...[
                  Padding(
                    padding: const EdgeInsets.fromLTRB(20, 14, 20, 6),
                    child: Text(
                      'Day $day',
                      style: GoogleFonts.instrumentSans(
                        fontSize: 12,
                        fontWeight: FontWeight.w700,
                        color: VoyoColors.terra,
                        letterSpacing: 0.5,
                      ),
                    ),
                  ),
                  for (final stop in byDay[day]!)
                    Padding(
                      padding: const EdgeInsets.fromLTRB(20, 0, 20, 6),
                      child: Row(
                        children: [
                          Container(
                            width: 8,
                            height: 8,
                            decoration: const BoxDecoration(
                              color: VoyoColors.sky,
                              shape: BoxShape.circle,
                            ),
                          ),
                          const SizedBox(width: 10),
                          Expanded(
                            child: Text(
                              stop.name,
                              style: GoogleFonts.instrumentSans(
                                fontSize: 14,
                                color: VoyoColors.ink,
                              ),
                            ),
                          ),
                          Text(
                            _fmt(stop.time),
                            style: GoogleFonts.jetBrainsMono(
                              fontSize: 11,
                              color: VoyoColors.stone,
                            ),
                          ),
                        ],
                      ),
                    ),
                ],
              ],
            ),
          ),
          // Error
          if (_error != null)
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 0, 20, 4),
              child: Text(
                _error!,
                style: GoogleFonts.instrumentSans(
                  fontSize: 12,
                  color: VoyoColors.expedition,
                ),
              ),
            ),
          // Save button
          Padding(
            padding: const EdgeInsets.fromLTRB(20, 8, 20, 24),
            child: SizedBox(
              width: double.infinity,
              height: 52,
              child: FilledButton(
                onPressed: _saving ? null : _save,
                style: FilledButton.styleFrom(
                  backgroundColor: VoyoColors.terra,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14),
                  ),
                ),
                child:
                    _saving
                        ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            color: Colors.white,
                          ),
                        )
                        : Text(
                          'Save ${widget.stops.length} Stops to Planner',
                          style: GoogleFonts.instrumentSans(
                            fontSize: 15,
                            fontWeight: FontWeight.w600,
                            color: Colors.white,
                          ),
                        ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// ── Typing indicator ──────────────────────────────────────────────────────

class _TypingIndicator extends StatefulWidget {
  final String intent; // 'general' | 'poi' | 'itinerary' | 'route'
  const _TypingIndicator({this.intent = 'general'});

  @override
  State<_TypingIndicator> createState() => _TypingIndicatorState();
}

class _TypingIndicatorState extends State<_TypingIndicator>
    with SingleTickerProviderStateMixin {
  late final AnimationController _ctrl;
  int _statusIndex = 0;

  // Staged status copy per intent. Calm/premium, not technical. Replaced by
  // real backend `progress` events once streaming lands (Tier 2 #1a).
  static const _statusByIntent = {
    'general': [
      'Thinking…',
      'Checking VOYO places…',
      'Looking for verified details…',
    ],
    'poi': [
      'Checking VOYO places…',
      'Looking for verified details…',
      'Preparing answer…',
    ],
    'itinerary': [
      'Checking VOYO places…',
      'Building itinerary…',
      'Checking the weather…',
      'Optimizing route…',
      'Preparing answer…',
    ],
    'route': ['Checking the route…', 'Optimizing…', 'Preparing answer…'],
  };

  List<String> get _statuses =>
      _statusByIntent[widget.intent] ?? _statusByIntent['general']!;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    )..repeat();
    // Cycle status copy every ~1.6s — slow enough to read, fast enough to
    // feel alive. Stops at the last message so it doesn't loop noisily.
    Future.delayed(const Duration(milliseconds: 1600), _advanceStatus);
  }

  void _advanceStatus() {
    if (!mounted) return;
    if (_statusIndex < _statuses.length - 1) {
      setState(() => _statusIndex += 1);
      Future.delayed(const Duration(milliseconds: 1600), _advanceStatus);
    }
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 8, 0, 4),
      child: Row(
        children: [
          const CleoAvatar(size: 24, variant: CleoAvatarVariant.thinking),
          const SizedBox(width: 10),
          AnimatedBuilder(
            animation: _ctrl,
            builder:
                (_, _) => Row(
                  children: List.generate(3, (i) {
                    final offset = Tween<double>(begin: 0, end: -5).animate(
                      CurvedAnimation(
                        parent: _ctrl,
                        curve: Interval(
                          i * 0.15,
                          0.5 + i * 0.15,
                          curve: Curves.easeInOut,
                        ),
                      ),
                    );
                    return Transform.translate(
                      offset: Offset(0, offset.value),
                      child: Container(
                        width: 7,
                        height: 7,
                        margin: const EdgeInsets.symmetric(horizontal: 2),
                        decoration: const BoxDecoration(
                          color: VoyoColors.sky,
                          shape: BoxShape.circle,
                        ),
                      ),
                    );
                  }),
                ),
          ),
          const SizedBox(width: 10),
          AnimatedSwitcher(
            duration: const Duration(milliseconds: 220),
            child: Text(
              _statuses[_statusIndex],
              key: ValueKey(_statusIndex),
              style: GoogleFonts.instrumentSans(
                fontSize: 12,
                color: VoyoColors.stone,
                fontStyle: FontStyle.italic,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
