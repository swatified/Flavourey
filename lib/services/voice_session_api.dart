import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

class VoiceSessionInfo {
  final String sessionId;
  final String channelName;
  final String rtcToken;
  final int rtcUid;

  VoiceSessionInfo({
    required this.sessionId,
    required this.channelName,
    required this.rtcToken,
    required this.rtcUid,
  });

  factory VoiceSessionInfo.fromJson(Map<String, dynamic> json) {
    return VoiceSessionInfo(
      sessionId: json['agentId'] ?? json['agent_id'] ?? json['sessionId'] ?? '',
      channelName: json['channel'] ?? json['channelName'] ?? '',
      rtcToken: json['rtc_token'] ?? json['rtcToken'] ?? '',
      rtcUid: (json['rtc_uid'] ?? json['rtcUid'] ?? 0) is int
          ? json['rtc_uid'] ?? json['rtcUid'] ?? 0
          : int.tryParse(json['rtc_uid']?.toString() ?? '0') ?? 0,
    );
  }
}

class VoiceSessionApi {
  final String baseUrl;
  final Map<String, String>? defaultHeaders;

  VoiceSessionApi({
    required this.baseUrl,
    this.defaultHeaders,
  });

  Future<VoiceSessionInfo> startSession(String userId) async {
    final channelName = 'voice_${userId}_${DateTime.now().millisecondsSinceEpoch}';
    final userUid = DateTime.now().millisecondsSinceEpoch % 1000000;

    try {
      // Use pre-generated RTC token from .env file
      final rtcToken = dotenv.env['AGORA_RTC_TOKEN_INT_UID'] ?? '';
      
      if (rtcToken.isEmpty) {
        throw Exception('AGORA_RTC_TOKEN_INT_UID not found in .env file');
      }

      debugPrint('[VoiceSessionApi] Starting Conversational AI agent for channel: $channelName, uid: $userUid');

      final agentUrl = Uri.parse('$baseUrl/api/ai/agent/start');
      final agentResponse = await http.post(
        agentUrl,
        headers: {
          'Content-Type': 'application/json',
          ...?defaultHeaders,
        },
        body: jsonEncode({
          'channelName': channelName,
          'rtcToken': rtcToken,
          'sessionKey': 'user_${userId}_session',
          'userContext': {
            'mood': null,
            'allergies': [],
          },
        }),
      );

      if (agentResponse.statusCode != 200) {
        throw Exception(
            'Failed to start agent: ${agentResponse.statusCode} ${agentResponse.body}');
      }

      final agentData = jsonDecode(agentResponse.body);
      
      debugPrint('[VoiceSessionApi] Conversational AI agent started: ${agentData['agentId']}');

      return VoiceSessionInfo(
        sessionId: agentData['agentId'] as String,
        channelName: channelName,
        rtcToken: rtcToken,
        rtcUid: userUid,
      );
    } catch (e) {
      debugPrint('[VoiceSessionApi] Error starting session: $e');
      rethrow;
    }
  }

  Future<void> stopSession(String sessionId) async {
    final url = Uri.parse('$baseUrl/api/ai/agent/stop');

    try {
      debugPrint('[VoiceSessionApi] Stopping Conversational AI session: $sessionId');

      final response = await http.post(
        url,
        headers: {
          'Content-Type': 'application/json',
          ...?defaultHeaders,
        },
        body: jsonEncode({
          'sessionKey': sessionId,
        }),
      );

      if (response.statusCode != 200) {
        throw Exception(
            'Failed to stop session: ${response.statusCode} ${response.body}');
      }

      debugPrint('[VoiceSessionApi] Conversational AI session stopped successfully');
    } catch (e) {
      debugPrint('[VoiceSessionApi] Error stopping session: $e');
      rethrow;
    }
  }
}
