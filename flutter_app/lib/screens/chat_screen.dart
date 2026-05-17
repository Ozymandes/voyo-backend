import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../models/chat_message.dart';
import '../services/cleo_service.dart';
import '../services/chat_history_service.dart';
import '../theme.dart';
import '../widgets/cleo_owl.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

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
      final reply = await _cleoService.sendMessage(text, userId: uid);
      final cleoMsg =
          ChatMessage(role: 'assistant', text: reply, timestamp: DateTime.now());
      setState(() {
        _messages.add(cleoMsg);
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
                  Text(
                    first,
                    style: GoogleFonts.fraunces(
                      fontSize: 16,
                      fontStyle: FontStyle.italic,
                      color: VoyoColors.ink,
                      height: 1.55,
                    ),
                  ),
                  if (rest.isNotEmpty) ...[
                    const SizedBox(height: 6),
                    Text(
                      rest,
                      style: GoogleFonts.instrumentSans(
                        fontSize: 14,
                        color: VoyoColors.stone,
                        height: 1.65,
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
              builder: (_, value, __) {
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
            builder: (_, __) => Row(
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
