import 'package:flutter/material.dart';
import '../core/theme.dart';
import '../services/copilot_service.dart';

class CopilotChatScreen extends StatefulWidget {
  const CopilotChatScreen({super.key});

  @override
  State<CopilotChatScreen> createState() => _CopilotChatScreenState();
}

class _CopilotChatScreenState extends State<CopilotChatScreen> {
  final _controller = TextEditingController();
  final _service = CopilotService();
  String _language = 'en';

  late List<Map<String, String>> _messages;

  final List<String> _chipsEn = [
    '💊 My medication schedule',
    '📅 When is my next appointment?',
    '📋 Missing diagnostic reports?',
    '🚨 Emergency medical summary',
    '🤝 Who are my caregivers?',
  ];

  final List<String> _chipsHi = [
    '💊 मेरी दवाइयों का समय',
    '📅 अगली डॉक्टर विज़िट कब है?',
    '📋 क्या कोई रिपोर्ट बाकी है?',
    '🚨 इमरजेंसी मेडिकल सारांश',
    '🤝 मेरे देखभालकर्ता कौन हैं?',
  ];

  bool _loading = false;

  @override
  void initState() {
    super.initState();
    _resetMessages();
  }

  void _resetMessages() {
    _messages = [
      {
        'sender': 'ai',
        'text': _language == 'hi'
            ? 'नमस्ते! मैं आपका CareBridge स्वास्थ्य सहायक हूँ। आज मैं आपकी दवाओं, डॉक्टर अपॉइंटमेंट या रिकवरी में कैसे मदद कर सकता हूँ?'
            : 'Hello! I am your CareBridge Health Assistant. Ask me anything about your prescriptions, appointment times, or recovery tasks.',
      }
    ];
  }

  void _toggleLanguage(String lang) {
    if (_language == lang) return;
    setState(() {
      _language = lang;
      _resetMessages();
    });
  }

  Future<void> _sendMessage([String? textToSend]) async {
    final text = textToSend ?? _controller.text.trim();
    if (text.isEmpty || _loading) return;

    _controller.clear();
    setState(() {
      _messages.add({'sender': 'user', 'text': text});
      _loading = true;
    });

    try {
      final answer = await _service.askCopilot(text, language: _language);
      if (mounted) {
        setState(() {
          _messages.add({'sender': 'ai', 'text': answer});
          _loading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _messages.add({'sender': 'ai', 'text': 'Unable to connect to assistant: $e'});
          _loading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final chips = _language == 'hi' ? _chipsHi : _chipsEn;

    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: const [
            Icon(Icons.auto_awesome, color: AppColors.primary, size: 20),
            SizedBox(width: 8),
            Text('CareBridge Copilot', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
          ],
        ),
        actions: [
          // Language Switcher Buttons
          Container(
            margin: const EdgeInsets.only(right: 12),
            padding: const EdgeInsets.all(2),
            decoration: BoxDecoration(
              color: const Color(0xFFF1F5F9),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                GestureDetector(
                  onTap: () => _toggleLanguage('en'),
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: _language == 'en' ? AppColors.primary : Colors.transparent,
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: Text(
                      'EN',
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.bold,
                        color: _language == 'en' ? Colors.white : AppColors.textMuted,
                      ),
                    ),
                  ),
                ),
                GestureDetector(
                  onTap: () => _toggleLanguage('hi'),
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: _language == 'hi' ? AppColors.primary : Colors.transparent,
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: Text(
                      'हिंदी',
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.bold,
                        color: _language == 'hi' ? Colors.white : AppColors.textMuted,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
      body: SafeArea(
        child: Column(
          children: [
            // Quick suggestion chips
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: Row(
                children: chips.map((chip) => Padding(
                      padding: const EdgeInsets.only(right: 8),
                      child: ActionChip(
                        label: Text(chip, style: const TextStyle(fontSize: 12)),
                        backgroundColor: Colors.white,
                        side: const BorderSide(color: AppColors.border),
                        onPressed: () => _sendMessage(chip),
                      ),
                    )).toList(),
              ),
            ),
            const Divider(height: 1, color: AppColors.border),

            // Messages Stream
            Expanded(
              child: ListView.builder(
                padding: const EdgeInsets.all(16),
                itemCount: _messages.length,
                itemBuilder: (context, idx) {
                  final msg = _messages[idx];
                  final isUser = msg['sender'] == 'user';

                  return Align(
                    alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
                    child: Container(
                      margin: const EdgeInsets.only(bottom: 12),
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                      constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.8),
                      decoration: BoxDecoration(
                        color: isUser ? AppColors.primary : Colors.white,
                        borderRadius: BorderRadius.only(
                          topLeft: const Radius.circular(16),
                          topRight: const Radius.circular(16),
                          bottomLeft: Radius.circular(isUser ? 16 : 4),
                          bottomRight: Radius.circular(isUser ? 4 : 16),
                        ),
                        border: isUser ? null : Border.all(color: AppColors.border),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withValues(alpha: 0.03),
                            blurRadius: 4,
                            offset: const Offset(0, 2),
                          )
                        ],
                      ),
                      child: Text(
                        msg['text']!,
                        style: TextStyle(
                          color: isUser ? Colors.white : AppColors.textDark,
                          fontSize: 13.5,
                          height: 1.45,
                        ),
                      ),
                    ),
                  );
                },
              ),
            ),

            if (_loading)
              Padding(
                padding: const EdgeInsets.all(12),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: const [
                    SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2)),
                    SizedBox(width: 10),
                    Text('CareBridge is thinking…', style: TextStyle(fontSize: 12, color: AppColors.textMuted)),
                  ],
                ),
              ),

            // Input Bar
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              decoration: const BoxDecoration(
                color: Colors.white,
                border: Border(top: BorderSide(color: AppColors.border)),
              ),
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _controller,
                      decoration: InputDecoration(
                        hintText: _language == 'hi'
                            ? 'दवा, अपॉइंटमेंट या रिपोर्ट के बारे में पूछें...'
                            : 'Ask about medicines, reports, appointments...',
                        hintStyle: const TextStyle(fontSize: 13, color: AppColors.textMuted),
                        contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(24),
                          borderSide: const BorderSide(color: AppColors.border),
                        ),
                        enabledBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(24),
                          borderSide: const BorderSide(color: AppColors.border),
                        ),
                        focusedBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(24),
                          borderSide: const BorderSide(color: AppColors.primary),
                        ),
                      ),
                      onSubmitted: (_) => _sendMessage(),
                    ),
                  ),
                  const SizedBox(width: 8),
                  IconButton(
                    onPressed: _loading ? null : () => _sendMessage(),
                    icon: const Icon(Icons.send_rounded, color: AppColors.primary),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
