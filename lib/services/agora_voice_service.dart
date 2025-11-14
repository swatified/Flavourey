import 'package:agora_rtc_engine/agora_rtc_engine.dart';
import 'package:flutter/foundation.dart';
import 'package:permission_handler/permission_handler.dart';

class AgoraVoiceService {
  final String appId;
  RtcEngine? _engine;
  bool _isJoined = false;
  int? _remoteUid;
  bool _isLocalAudioMuted = false;

  AgoraVoiceService({required this.appId});

  bool get isJoined => _isJoined;
  int? get remoteUid => _remoteUid;
  bool get isLocalAudioMuted => _isLocalAudioMuted;

  Future<void> initialize() async {
    if (_engine != null) {
      debugPrint('[AgoraVoiceService] Already initialized');
      return;
    }

    await _requestPermissions();

    _engine = createAgoraRtcEngine();
    await _engine!.initialize(RtcEngineContext(
      appId: appId,
      channelProfile: ChannelProfileType.channelProfileCommunication,
    ));

    await _engine!.enableAudio();
    await _engine!.setAudioProfile(
      profile: AudioProfileType.audioProfileDefault,
      scenario: AudioScenarioType.audioScenarioChatroom,
    );

    _registerEventHandlers();

    debugPrint('[AgoraVoiceService] Initialized successfully');
  }

  Future<void> _requestPermissions() async {
    final status = await Permission.microphone.request();
    if (status.isDenied || status.isPermanentlyDenied) {
      debugPrint('[AgoraVoiceService] Microphone permission denied');
      throw Exception('Microphone permission is required for voice calls');
    }
  }

  void _registerEventHandlers() {
    _engine!.registerEventHandler(
      RtcEngineEventHandler(
        onJoinChannelSuccess: (RtcConnection connection, int elapsed) {
          debugPrint(
              '[AgoraVoiceService] Joined channel: ${connection.channelId}, uid: ${connection.localUid}');
          _isJoined = true;
        },
        onUserJoined: (RtcConnection connection, int remoteUid, int elapsed) {
          debugPrint(
              '[AgoraVoiceService] Remote user joined: $remoteUid (AI agent)');
          _remoteUid = remoteUid;
        },
        onUserOffline: (RtcConnection connection, int remoteUid,
            UserOfflineReasonType reason) {
          debugPrint('[AgoraVoiceService] Remote user offline: $remoteUid');
          if (_remoteUid == remoteUid) {
            _remoteUid = null;
          }
        },
        onConnectionStateChanged: (RtcConnection connection,
            ConnectionStateType state, ConnectionChangedReasonType reason) {
          debugPrint(
              '[AgoraVoiceService] Connection state changed: $state, reason: $reason');
        },
        onError: (ErrorCodeType err, String msg) {
          debugPrint('[AgoraVoiceService] Error: $err - $msg');
        },
      ),
    );
  }

  Future<void> joinChannel({
    required String token,
    required String channelName,
    required int uid,
  }) async {
    if (_engine == null) {
      throw Exception('Engine not initialized. Call initialize() first.');
    }

    if (_isJoined) {
      debugPrint('[AgoraVoiceService] Already joined a channel');
      return;
    }

    final options = ChannelMediaOptions(
      channelProfile: ChannelProfileType.channelProfileCommunication,
      clientRoleType: ClientRoleType.clientRoleBroadcaster,
      autoSubscribeAudio: true,
      publishMicrophoneTrack: true,
    );

    await _engine!.joinChannel(
      token: token,
      channelId: channelName,
      uid: uid,
      options: options,
    );

    debugPrint(
        '[AgoraVoiceService] Joining channel: $channelName with uid: $uid');
  }

  Future<void> leaveChannel() async {
    if (_engine == null) {
      debugPrint('[AgoraVoiceService] Engine not initialized');
      return;
    }

    if (!_isJoined) {
      debugPrint('[AgoraVoiceService] Not in a channel');
      return;
    }

    await _engine!.leaveChannel();
    _isJoined = false;
    _remoteUid = null;
    _isLocalAudioMuted = false;

    debugPrint('[AgoraVoiceService] Left channel');
  }

  Future<void> muteLocalAudio(bool mute) async {
    if (_engine == null) {
      debugPrint('[AgoraVoiceService] Engine not initialized');
      return;
    }

    await _engine!.muteLocalAudioStream(mute);
    _isLocalAudioMuted = mute;
    debugPrint('[AgoraVoiceService] Local audio ${mute ? 'muted' : 'unmuted'}');
  }

  Future<void> dispose() async {
    if (_engine != null) {
      await leaveChannel();
      await _engine!.release();
      _engine = null;
      debugPrint('[AgoraVoiceService] Disposed');
    }
  }
}
