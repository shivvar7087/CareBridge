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
  final List<Map<String, String>> _messages = [
    {
      'sender': 'ai',
      'text': 'Hello! I am your CareBridge AI Health Assistant. Ask me anything about your prescriptions, appointment times, or recovery tasks.',
    }
  ];

  final List<String> _chips = [
    '💊 My medication schedule',
    '📅 When is my next appointment?',
    '📋 Missing diagnostic reports?',
    '🚨 Emergency medical summary',
  ];

  bool _loading = false;

  Future<void> _sendMessage([String? textToSend]) async {
    final text = textToSend ?? _controller.text.trim();
    if (text.isEmpty || _loading) return;

    _controller.clear();
    setState(() {
      _messages.add({'sender': 'user', 'text': text});
      _loading = true;
    });

    try {
      final answer = await _service.askCopilot(text);
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
    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: const [
            Icon(Icons.auto_awesome, color: AppColors.primary, size: 20),
            SizedBox(width: 8),
            Text('CareBridge AI Copilot', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 17)),
          ],
        ),
      ),
      body: SafeArea(
        child: Column(
          children: [
            // Quick suggestion chips
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: Row(
                children: _chips.map((chip) => Padding(
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
                      constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.8),
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                      decoration: BoxDecoration(
                        color: isUser ? AppColors.primary : Colors.white,
                        border: isUser ? null : Border.all(color: AppColors.border),
                        borderRadius: BorderRadius.circular(16).copyWith(
                          bottomRight: isUser ? const Radius.circular(2) : const Radius.circular(16),
                          bottomLeft: !isUser ? const Radius.circular(2) : const Radius.circular(16),
                        ),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.04),
                            blurRadius: 4,
                            offset: const Offset(0, 2),
                          ),
                        ],
                      ),
                      child: Text(
                        msg['text'] ?? '',
                        style: TextStyle(
                          color: isUser ? Colors.white : AppColors.textDark,
                          fontSize: 14,
                          height: 1.4,
                        ),
                      ),
                    ),
                  );
                },
              ),
            ),

            if (_loading) ...[
              const Padding(
                padding: EdgeInsets.symmetric(vertical: 8),
                child: SizedBox(
                  width: 24,
                  height: 24,
                  child: CircularProgressIndicator(strokeWidth: 2, color: AppColors.primary),
                ),
              ),
            ],

            // Input Bar
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              decoration: const BoxDecoration(
                color: Colors.white,
                border: Border(top: BorderSide(color: AppColors.border)),
              ),
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _controller,
                      decoration: const InputDecoration(
                        hintText: 'Ask about recovery, medications…',
                        border: InputBorder.none,
                        enabledBorder: InputBorder.none,
                        focusedBorder: InputBorder.none,
                        contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                      ),
                      onSubmitted: (_) => _sendMessage(),
                    ),
                  ),
                  const SizedBox(width: 8),
                  IconButton(
                    icon: const Icon(Icons.send_rounded, color: AppColors.primary),
                    onPressed: () => _sendMessage(),
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
