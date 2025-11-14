import 'package:flutter/material.dart';
import 'dart:async';
import '../services/agora_voice_service.dart';
import '../services/voice_session_api.dart';
import '../services/app_config.dart';

class ChatbotPage extends StatefulWidget {
  const ChatbotPage({super.key});

  @override
  State<ChatbotPage> createState() => _ChatbotPageState();
}

class _ChatbotPageState extends State<ChatbotPage> {
  late AgoraVoiceService _voiceService;
  late VoiceSessionApi _sessionApi;
  
  VoiceSessionInfo? _activeSession;
  bool _isStartingOrStopping = false;
  Timer? _callDurationTimer;
  int _callDurationSeconds = 0;
  bool _isLocalMuted = false;

  @override
  void initState() {
    super.initState();
    _voiceService = AgoraVoiceService(appId: AppConfig.agoraAppId);
    _sessionApi = VoiceSessionApi(baseUrl: AppConfig.backendBaseUrl);
    _initializeVoiceService();
  }

  Future<void> _initializeVoiceService() async {
    try {
      await _voiceService.initialize();
    } catch (e) {
      debugPrint('[ChatbotPage] Failed to initialize voice service: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Voice initialization failed: ${e.toString()}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _startVoiceSession() async {
    if (_isStartingOrStopping) return;

    setState(() {
      _isStartingOrStopping = true;
    });

    try {
      final userId = 'user_${DateTime.now().millisecondsSinceEpoch}';
      
      final sessionInfo = await _sessionApi.startSession(userId);
      
      await _voiceService.joinChannel(
        token: sessionInfo.rtcToken,
        channelName: sessionInfo.channelName,
        uid: sessionInfo.rtcUid,
      );

      setState(() {
        _activeSession = sessionInfo;
        _callDurationSeconds = 0;
      });

      _startCallDurationTimer();

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Voice session started'),
            backgroundColor: Colors.green,
            duration: Duration(seconds: 2),
          ),
        );
      }
    } catch (e) {
      debugPrint('[ChatbotPage] Failed to start voice session: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to start voice: ${e.toString()}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isStartingOrStopping = false;
        });
      }
    }
  }

  Future<void> _stopVoiceSession() async {
    if (_isStartingOrStopping || _activeSession == null) return;

    setState(() {
      _isStartingOrStopping = true;
    });

    try {
      await _voiceService.leaveChannel();
      
      await _sessionApi.stopSession(_activeSession!.sessionId);

      _stopCallDurationTimer();

      setState(() {
        _activeSession = null;
        _callDurationSeconds = 0;
        _isLocalMuted = false;
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Voice session ended'),
            backgroundColor: Colors.grey,
            duration: Duration(seconds: 2),
          ),
        );
      }
    } catch (e) {
      debugPrint('[ChatbotPage] Failed to stop voice session: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to stop voice: ${e.toString()}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isStartingOrStopping = false;
        });
      }
    }
  }

  void _startCallDurationTimer() {
    _callDurationTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (mounted) {
        setState(() {
          _callDurationSeconds++;
        });
      }
    });
  }

  void _stopCallDurationTimer() {
    _callDurationTimer?.cancel();
    _callDurationTimer = null;
  }

  String _formatDuration(int seconds) {
    final minutes = seconds ~/ 60;
    final secs = seconds % 60;
    return '${minutes.toString().padLeft(2, '0')}:${secs.toString().padLeft(2, '0')}';
  }

  Future<void> _toggleMute() async {
    try {
      final newMuteState = !_isLocalMuted;
      await _voiceService.muteLocalAudio(newMuteState);
      setState(() {
        _isLocalMuted = newMuteState;
      });
    } catch (e) {
      debugPrint('[ChatbotPage] Failed to toggle mute: $e');
    }
  }

  @override
  void dispose() {
    _stopCallDurationTimer();
    _voiceService.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final bool isActive = _activeSession != null;

    return Scaffold(
      backgroundColor: const Color(0xFFF5F5F5),
      appBar: AppBar(
        backgroundColor: const Color(0xFFFAC587),
        title: const Text(
          'AI Chatbot',
          style: TextStyle(
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
        elevation: 0,
        centerTitle: true,
        actions: [
          if (isActive)
            Padding(
              padding: const EdgeInsets.only(right: 8.0),
              child: Center(
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    _formatDuration(_callDurationSeconds),
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 14,
                    ),
                  ),
                ),
              ),
            ),
          Padding(
            padding: const EdgeInsets.only(right: 8.0),
            child: IconButton(
              onPressed: _isStartingOrStopping
                  ? null
                  : (isActive ? _stopVoiceSession : _startVoiceSession),
              icon: Icon(
                isActive ? Icons.call_end : Icons.phone,
                color: Colors.white,
              ),
              style: IconButton.styleFrom(
                backgroundColor: isActive
                    ? Colors.red.shade700
                    : Colors.green.shade700,
                disabledBackgroundColor: Colors.grey,
              ),
            ),
          ),
        ],
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: const Color(0xFFFF9A56).withValues(alpha: 0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(
                isActive ? Icons.mic : Icons.chat_bubble_rounded,
                size: 80,
                color: isActive ? Colors.green : const Color(0xFFFF9A56),
              ),
            ),
            const SizedBox(height: 32),
            Text(
              isActive ? 'Voice Active' : 'AI Chatbot',
              style: const TextStyle(
                fontSize: 28,
                fontWeight: FontWeight.bold,
                color: Color(0xFF2D3142),
              ),
            ),
            const SizedBox(height: 12),
            Text(
              isActive
                  ? 'Tap the phone icon to end call'
                  : 'Coming Soon',
              style: TextStyle(
                fontSize: 18,
                color: Colors.grey[600],
                fontWeight: FontWeight.w500,
              ),
            ),
            const SizedBox(height: 8),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 40),
              child: Text(
                isActive
                    ? 'Speak naturally with the AI assistant'
                    : 'Chat with our AI to get personalized food recommendations',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.grey[500],
                  height: 1.5,
                ),
              ),
            ),
            if (isActive) ...[
              const SizedBox(height: 32),
              ElevatedButton.icon(
                onPressed: _toggleMute,
                icon: Icon(_isLocalMuted ? Icons.mic_off : Icons.mic),
                label: Text(_isLocalMuted ? 'Unmute' : 'Mute'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: _isLocalMuted
                      ? Colors.red.shade100
                      : Colors.green.shade100,
                  foregroundColor: _isLocalMuted
                      ? Colors.red.shade900
                      : Colors.green.shade900,
                  padding: const EdgeInsets.symmetric(
                    horizontal: 24,
                    vertical: 12,
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
