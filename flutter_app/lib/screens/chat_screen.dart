import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../models/chat_message.dart';
import '../models/itinerary.dart';
import '../services/cleo_service.dart';
import '../services/chat_history_service.dart';
import '../services/supabase_service.dart';
import '../theme.dart';
import '../widgets/cleo_owl.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key, this.onSwitchToPlanner});

  final VoidCallback? onSwitchToPlanner;

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
  bool _sidebarOpen = false;

  // Index of the last message that contained [PLANNER]
  int? _plannerPromptIndex;

  // Stops parsed from the last itinerary response
  List<_ParsedStop> _parsedStops = [];

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

    // Create session on first message
    _currentSessionId ??= _historyService.newSessionId();

    final userMsg =
        ChatMessage(role: 'user', text: text, timestamp: DateTime.now());
    setState(() {
      _messages.add(userMsg);
      _isLoading = true;
    });
    _scrollToBottom();
    if (uid != 'anonymous') {
      await _historyService.appendToSession(uid, _currentSessionId!, userMsg);
      await _loadSessions();
    }

    try {
      final raw = await _cleoService.sendMessage(text, userId: uid);
      final hasPlanner = raw.contains('[PLANNER]');
      final reply = raw.replaceAll('[PLANNER]', '').trimRight();
      final stops = hasPlanner ? _parseItineraryStops(reply) : <_ParsedStop>[];
      final cleoMsg =
          ChatMessage(role: 'assistant', text: reply, timestamp: DateTime.now());
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
        _messages.add(ChatMessage(
          role: 'assistant',
          text: 'Cleo is taking a moment. Is the backend running?\n\nError: $e',
          timestamp: DateTime.now(),
        ));
        _isLoading = false;
      });
    }
    _scrollToBottom();
  }

  // ── Itinerary parsing ──────────────────────────────────────────────────────

  List<_ParsedStop> _parseItineraryStops(String text) {
    final stops = <_ParsedStop>[];
    int currentDay = 1;
    String currentTime = '09:00:00';

    // Imperative verbs that start tips/guidelines, not place names
    const tipVerbs = {
      'wear', 'pack', 'avoid', 'stay', 'drink', 'bring', 'book', 'check',
      'note', 'consider', 'remember', 'tip', 'tips', 'try', 'use', 'take',
      'get', 'be', 'make', 'do', "don't", 'always', 'never', 'ensure',
      'plan', 'hire', 'head', 'walk', 'go', 'start', 'stop', 'keep',
      'carry', 'watch', 'ask', 'buy', 'eat', 'have', 'grab', 'spend',
      'enjoy', 'relax', 'explore', 'return', 'end', 'finish', 'begin',
      'continue', 'haggle', 'bargain', 'negotiate', 'dress', 'cover',
      'respect', 'travel', 'learn', 'visit', 'see', 'find', 'follow',
      'opt', 'choose', 'select', 'pick', 'arrange', 'prepare',
    };

    // Words that indicate dining/food rather than a site
    const skipWords = [
      'restaurant', 'dinner', 'lunch', 'breakfast', 'café', 'cafe',
      'street food', 'rooftop bar', 'hotel restaurant',
      "ta'meya", 'ful ', 'shawarma', 'koshary', 'koshari',
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
      if (lower.contains('morning'))        { currentTime = '09:00:00'; }
      else if (lower.contains('lunch'))     { currentTime = '12:30:00'; }
      else if (lower.contains('afternoon')) { currentTime = '13:00:00'; }
      else if (lower.contains('evening'))   { currentTime = '18:30:00'; }

      // Bullet point only — require a space after * so **Bold Headers** are not matched
      final isBullet = line.startsWith('• ') ||
          line.startsWith('- ') ||
          line.startsWith('* ') ||
          line.startsWith('• ');
      if (!isBullet) { continue; }

      final withoutBullet = line.replaceFirst(RegExp(r'^[•\-\*]\s*'), '');
      // Strip all asterisks and hashes (markdown bold/header remnants)
      final clean = withoutBullet.replaceAll(RegExp(r'[\*#]'), '');
      // Take only text before em-dash, en-dash, colon, or parenthesis
      final dashIdx = clean.indexOf(RegExp(r'[—–:(]'));
      final name = (dashIdx > 0 ? clean.substring(0, dashIdx) : clean).trim();

      if (name.length <= 3) { continue; }

      // Must contain at least one capital letter — place names always do;
      // tip sentences that slipped through are usually all-lowercase.
      if (!name.contains(RegExp(r'[A-Z]'))) { continue; }

      // Skip section labels like "Travel Tips", "Important Notes", "General Tips"
      final nameLower = name.toLowerCase();
      if (nameLower.contains('tip') || nameLower.contains('note') ||
          nameLower.contains('guideline') || nameLower.contains('advice') ||
          nameLower.contains('reminder') || nameLower.contains('warning')) {
        continue;
      }

      // Skip if first word is a tip/action verb
      final firstWord = name
          .split(RegExp(r'\s+'))
          .first
          .toLowerCase()
          .replaceAll(RegExp(r"[^a-z']"), '');
      if (tipVerbs.contains(firstWord)) { continue; }

      // Skip dining/food entries
      if (skipWords.any((w) => name.toLowerCase().contains(w))) { continue; }

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
      builder: (_) => _ImportStopsSheet(
        stops: _parsedStops,
        userId: _userId ?? '',
        onImported: () => widget.onSwitchToPlanner?.call(),
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
                child: _messages.isEmpty
                    ? _buildEmptyState()
                    : _buildMessageList(),
              ),
              if (_isLoading) const _TypingIndicator(),
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
                  // Sidebar toggle
                  GestureDetector(
                    onTap: () => setState(() => _sidebarOpen = true),
                    child: const Padding(
                      padding: EdgeInsets.symmetric(horizontal: 16),
                      child: Icon(Icons.menu, color: VoyoColors.ink, size: 22),
                    ),
                  ),
                  const CleoOwl(size: 30),
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
                      child: const Icon(Icons.add,
                          color: Colors.white, size: 18),
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
                    const CleoOwl(size: 28),
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
                      child: const Icon(Icons.close,
                          color: Color(0xFF6A6058), size: 20),
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
                child: _sessions.isEmpty
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
          color: isActive
              ? const Color(0xFF2A2420)
              : Colors.transparent,
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
                  fontWeight:
                      isActive ? FontWeight.w500 : FontWeight.w400,
                ),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
            ),
            const SizedBox(width: 6),
            GestureDetector(
              onTap: () => _deleteSession(session),
              child: const Icon(Icons.close,
                  size: 14, color: Color(0xFF4A4440)),
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
            const CleoOwl(size: 80),
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
          padding:
              const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
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

    final (first, rest) = _splitFirstSentence(msg.text);
    final msgIndex = _messages.indexOf(msg);
    final showPlannerButton = msgIndex != -1 && msgIndex == _plannerPromptIndex;

    return Padding(
      padding: const EdgeInsets.only(top: 16, bottom: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const CleoOwl(size: 32),
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
                            borderRadius: BorderRadius.circular(10)),
                        padding: const EdgeInsets.symmetric(
                            horizontal: 16, vertical: 10),
                      ),
                      icon: const Icon(Icons.calendar_today_rounded,
                          size: 15, color: Colors.white),
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
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  /// Renders a single line with **bold** spans, stripping header prefixes.
  /// Used for the italic hook sentence so bold still shows inside Fraunces italic.
  Widget _buildInlineMarkdown(String text, TextStyle base) {
    final cleaned = text
        .replaceAll(RegExp(r'^#+\s*', multiLine: true), '')
        .trim();
    final spans = <InlineSpan>[];
    final boldRe = RegExp(r'\*\*(.+?)\*\*');
    int cursor = 0;
    for (final m in boldRe.allMatches(cleaned)) {
      if (m.start > cursor) {
        spans.add(TextSpan(text: cleaned.substring(cursor, m.start), style: base));
      }
      spans.add(TextSpan(
        text: m.group(1),
        style: base.copyWith(fontWeight: FontWeight.w700),
      ));
      cursor = m.end;
    }
    if (cursor < cleaned.length) {
      spans.add(TextSpan(text: cleaned.substring(cursor), style: base));
    }
    return RichText(text: TextSpan(children: spans));
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
    strong: _bodyStyle.copyWith(fontWeight: FontWeight.w700, color: VoyoColors.ink),
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
          children: _starterChips.map((chip) {
            return Padding(
              padding: const EdgeInsets.only(right: 8),
              child: GestureDetector(
                onTap: () => _send(chip),
                child: Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: 14, vertical: 8),
                  decoration: BoxDecoration(
                    color: VoyoColors.paper,
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(
                        color: VoyoColors.sky.withValues(alpha: 0.4)),
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
                    color: VoyoColors.ink, fontSize: 14),
                decoration: InputDecoration(
                  hintText: 'Ask Cleo anything…',
                  hintStyle: GoogleFonts.instrumentSans(
                      color: VoyoColors.stone, fontSize: 14),
                  filled: true,
                  fillColor: VoyoColors.vellum,
                  contentPadding: const EdgeInsets.symmetric(
                      horizontal: 16, vertical: 12),
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
                    borderSide:
                        const BorderSide(color: VoyoColors.sky, width: 1.5),
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
        text.substring(idx + sep.length).trim()
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

  const _ParsedStop({required this.day, required this.name, required this.time});
}

// ── Import stops sheet ────────────────────────────────────────────────────

class _ImportStopsSheet extends StatefulWidget {
  final List<_ParsedStop> stops;
  final String userId;
  final VoidCallback onImported;

  const _ImportStopsSheet({
    required this.stops,
    required this.userId,
    required this.onImported,
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
    final days = widget.stops.isEmpty ? 0
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

    const stopWords = {'the', 'of', 'el', 'al', 'in', 'at', 'and', 'a', 'an', 'to'};
    final words = name
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
    setState(() { _saving = true; _error = null; });
    try {
      // Always create a new itinerary with the user-supplied name
      final title = _titleCtrl.text.trim().isEmpty
          ? '${widget.stops.map((s) => s.day).reduce((a, b) => a > b ? a : b)}-Day Egypt Trip'
          : _titleCtrl.text.trim();
      Itinerary? itinerary = await _service.createItinerary(
        userId: widget.userId,
        title: title,
      );
      if (itinerary == null) throw Exception('Could not create itinerary');

      // Add each stop, using fuzzy keyword fallback to find a matching POI
      for (final stop in widget.stops) {
        final poiId = await _findPoiId(stop.name);

        await _service.addItineraryItem(
          itineraryId: itinerary.id,
          poiId: poiId,
          customTitle: poiId == null ? stop.name : null,
          dayNumber: stop.day,
          startTime: stop.time,
        );
      }

      if (mounted) {
        Navigator.pop(context);
        widget.onImported();
      }
    } catch (e) {
      if (mounted) setState(() { _error = e.toString(); _saving = false; });
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
              width: 36, height: 4,
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
                  child: const Icon(Icons.close, size: 20, color: VoyoColors.stone),
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
              style: GoogleFonts.instrumentSans(color: VoyoColors.ink, fontSize: 14),
              decoration: InputDecoration(
                labelText: 'Trip name',
                labelStyle: GoogleFonts.instrumentSans(
                    fontSize: 12, color: VoyoColors.stone),
                prefixIcon: const Icon(Icons.luggage_outlined,
                    color: VoyoColors.stone, size: 18),
                filled: true,
                fillColor: VoyoColors.vellum,
                contentPadding:
                    const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide.none),
                enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide.none),
                focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide:
                        const BorderSide(color: VoyoColors.terra, width: 1.5)),
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
                    fontSize: 12, color: VoyoColors.stone),
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
                            width: 8, height: 8,
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
                                fontSize: 14, color: VoyoColors.ink),
                            ),
                          ),
                          Text(
                            _fmt(stop.time),
                            style: GoogleFonts.jetBrainsMono(
                              fontSize: 11, color: VoyoColors.stone),
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
              child: Text(_error!,
                  style: GoogleFonts.instrumentSans(
                      fontSize: 12, color: VoyoColors.expedition)),
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
                      borderRadius: BorderRadius.circular(14)),
                ),
                child: _saving
                    ? const SizedBox(
                        width: 20, height: 20,
                        child: CircularProgressIndicator(
                            strokeWidth: 2, color: Colors.white))
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
  const _TypingIndicator();

  @override
  State<_TypingIndicator> createState() => _TypingIndicatorState();
}

class _TypingIndicatorState extends State<_TypingIndicator>
    with SingleTickerProviderStateMixin {
  late final AnimationController _ctrl;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    )..repeat();
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
          const CleoOwl(size: 24),
          const SizedBox(width: 10),
          AnimatedBuilder(
            animation: _ctrl,
            builder: (_, _) => Row(
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
        ],
      ),
    );
  }
}
