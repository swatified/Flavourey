# Agora Voice Integration - Implementation Summary

## Overview
This document provides a technical overview of the Agora Conversational AI voice integration in the Flavourey Flutter app.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Flutter UI Layer                         │
│                  (chatbot_page.dart)                        │
│  - Call button controls                                     │
│  - Duration timer display                                   │
│  - Mute/unmute controls                                     │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ├──────────────────────────────────────┐
                 │                                      │
                 ▼                                      ▼
┌────────────────────────────────┐   ┌─────────────────────────────────┐
│   AgoraVoiceService            │   │   VoiceSessionApi               │
│   (agora_voice_service.dart)   │   │   (voice_session_api.dart)      │
│                                │   │                                 │
│  - RtcEngine lifecycle         │   │  - POST /api/token/generate     │
│  - Channel join/leave          │   │  - POST /api/agent/start        │
│  - Audio mute/unmute           │   │  - POST /api/agent/leave        │
│  - Event handlers              │   │  - Session info management      │
└────────────────┬───────────────┘   └──────────────┬──────────────────┘
                 │                                   │
                 ▼                                   ▼
┌────────────────────────────────┐   ┌─────────────────────────────────┐
│   Agora RTC Engine SDK         │   │   Python Backend                │
│   (agora_rtc_engine)           │   │   (bot_backend/src/server.py)   │
│                                │   │                                 │
│  - Audio capture/playback      │   │  - Token generation             │
│  - RTC channel management      │   │  - Agora agent control          │
│  - Network handling            │   │  - LLM integration (Gemini)     │
└────────────────┬───────────────┘   └──────────────┬──────────────────┘
                 │                                   │
                 └──────────────┬────────────────────┘
                                │
                                ▼
                ┌───────────────────────────────────┐
                │   Agora RTC Network               │
                │   + Conversational AI Engine      │
                │                                   │
                │  - Real-time audio transport      │
                │  - AI agent orchestration         │
                │  - STT → LLM → TTS pipeline      │
                └───────────────────────────────────┘
```

## File Structure

```
lib/
├── main.dart                          # App entry point (loads config)
├── pages/
│   └── chatbot_page.dart              # Main voice UI (StatefulWidget)
└── services/
    ├── app_config.dart                # Environment configuration loader
    ├── agora_voice_service.dart       # Agora RTC SDK wrapper
    └── voice_session_api.dart         # Backend API client
```

## Component Details

### 1. app_config.dart
**Purpose**: Centralized configuration management using `.env` file.

**Key Methods**:
- `load()`: Loads environment variables from `.env`
- `validate()`: Ensures required config is present
- `agoraAppId`: Getter for Agora App ID
- `backendBaseUrl`: Getter for backend API URL

**Usage**:
```dart
await AppConfig.load();
AppConfig.validate();
```

### 2. agora_voice_service.dart
**Purpose**: Manages Agora RTC Engine lifecycle and audio operations.

**Key Properties**:
- `_engine`: RtcEngine instance
- `_isJoined`: Channel join state
- `_remoteUid`: AI agent's UID
- `_isLocalAudioMuted`: Mic mute state

**Key Methods**:
- `initialize()`: Sets up RTC engine with communication profile
- `joinChannel()`: Joins voice channel with token/channel/uid
- `leaveChannel()`: Leaves channel and resets state
- `muteLocalAudio()`: Toggles local microphone
- `dispose()`: Cleans up resources

**Event Handlers**:
- `onJoinChannelSuccess`: Confirms successful join
- `onUserJoined`: Detects AI agent joining
- `onUserOffline`: Detects AI agent leaving
- `onConnectionStateChanged`: Network state monitoring
- `onError`: Error logging

### 3. voice_session_api.dart
**Purpose**: HTTP client for backend session management.

**Models**:
- `VoiceSessionInfo`: Data class for session details
  - `sessionId`: AI agent ID
  - `channelName`: RTC channel name
  - `rtcToken`: Authentication token
  - `rtcUid`: User's RTC UID

**Key Methods**:
- `startSession(userId)`: 
  1. Generates unique channel name and UID
  2. Calls `/api/token/generate` for RTC token
  3. Calls `/api/agent/start` to launch AI agent
  4. Returns session info
  
- `stopSession(sessionId)`:
  1. Calls `/api/agent/leave` with agent ID
  2. Triggers agent shutdown on backend

### 4. chatbot_page.dart
**Purpose**: Voice call UI and state management.

**State Variables**:
- `_voiceService`: AgoraVoiceService instance
- `_sessionApi`: VoiceSessionApi instance
- `_activeSession`: Current session info (null if idle)
- `_isStartingOrStopping`: Prevents double-taps
- `_callDurationTimer`: Updates duration every second
- `_callDurationSeconds`: Call time in seconds
- `_isLocalMuted`: Mic mute state

**Lifecycle**:
```
initState()
  └─> _initializeVoiceService()
       └─> _voiceService.initialize()
            └─> RTC engine ready
            
User taps call icon (idle)
  └─> _startVoiceSession()
       ├─> _sessionApi.startSession()
       │    ├─> Backend: generate token
       │    └─> Backend: start AI agent
       ├─> _voiceService.joinChannel()
       │    └─> Join RTC channel
       └─> _startCallDurationTimer()
            └─> UI updates every second
            
User taps call icon (active)
  └─> _stopVoiceSession()
       ├─> _voiceService.leaveChannel()
       │    └─> Leave RTC channel
       ├─> _sessionApi.stopSession()
       │    └─> Backend: stop AI agent
       └─> _stopCallDurationTimer()
            └─> Reset UI state

dispose()
  └─> Clean up timers and voice service
```

**UI States**:
1. **Idle**: Green phone icon, "Coming Soon" text
2. **Starting**: Grey disabled icon (loading)
3. **Active**: Red call-end icon, duration timer, mute button, "Voice Active" text
4. **Stopping**: Grey disabled icon (loading)

## Backend Integration

### Endpoints Used

#### POST /api/token/generate
**Request**:
```json
{
  "channel": "voice_user_123_1234567890",
  "uid": 123456,
  "expire_seconds": 3600
}
```

**Response**:
```json
{
  "token": "006abc...xyz",
  "app_id": "55a8e56a...",
  "channel": "voice_user_123_1234567890",
  "uid": 123456
}
```

#### POST /api/agent/start
**Request**:
```json
{
  "channel": "voice_user_123_1234567890",
  "rtc_token": "006abc...xyz",
  "agent_rtc_uid": "0"
}
```

**Response**:
```json
{
  "agent_id": "agent_abc123",
  "channel": "voice_user_123_1234567890",
  "status": "joining"
}
```

#### POST /api/agent/leave
**Request**:
```json
{
  "agent_id": "agent_abc123"
}
```

**Response**:
```json
{
  "ok": true,
  "result": { "status": "left" }
}
```

## Configuration

### .env File
```properties
AGORA_APP_ID=<your_app_id>
AGORA_APP_CERT=<your_app_certificate>
BACKEND_BASE_URL=http://localhost:8000
```

### Android Permissions (AndroidManifest.xml)
```xml
<uses-permission android:name="android.permission.INTERNET"/>
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE"/>
<uses-permission android:name="android.permission.ACCESS_WIFI_STATE"/>
<uses-permission android:name="android.permission.RECORD_AUDIO"/>
<uses-permission android:name="android.permission.MODIFY_AUDIO_SETTINGS"/>
<uses-permission android:name="android.permission.BLUETOOTH" android:maxSdkVersion="30"/>
<uses-permission android:name="android.permission.BLUETOOTH_CONNECT" android:minSdkVersion="31"/>
```

### iOS Permissions (Info.plist)
```xml
<key>NSMicrophoneUsageDescription</key>
<string>This app needs access to your microphone for voice conversations with the AI assistant.</string>
```

## Error Handling

### Client-Side Errors
1. **Engine not initialized**: Shows error snackbar, prevents join
2. **Permission denied**: Throws exception with clear message
3. **Network errors**: Catches and displays in snackbar
4. **Double-tap prevention**: `_isStartingOrStopping` guard

### Backend Errors
1. **Token generation fails**: HTTP error caught and displayed
2. **Agent start fails**: Error message from backend shown
3. **Agent leave fails**: Logged but doesn't block UI reset

### Network Issues
1. **Connection state changes**: Logged to console
2. **User offline**: Detected by `onUserOffline` event
3. **Reconnection**: Handled by Agora SDK automatically

## State Management

Uses simple `setState()` approach:
- **Pros**: Simple, no extra dependencies, easy to debug
- **Cons**: Not shared across screens (acceptable for isolated feature)
- **Future**: Could migrate to Provider/Riverpod if needed for state sharing

## Audio Configuration

```dart
ChannelProfileType.channelProfileCommunication
  - Optimized for one-on-one voice calls
  - Low latency
  - High audio quality

AudioScenarioType.audioScenarioChatroom
  - Optimized for conversational audio
  - Echo cancellation enabled
  - Noise suppression enabled
```

## Security Considerations

1. **Token Generation**: Done server-side using App Certificate
2. **No hardcoded secrets**: All credentials in `.env` file
3. **UID Generation**: Dynamic based on timestamp (not predictable user IDs)
4. **Channel Names**: Unique per session to prevent collisions
5. **Token Expiry**: 3600 seconds (configurable)

## Performance Optimization

1. **Lazy Initialization**: RTC engine initialized once in `initState`
2. **Resource Cleanup**: Proper disposal of engine and timers
3. **Efficient State Updates**: Only update UI when mounted
4. **Single Engine Instance**: Reused across multiple sessions
5. **Minimal Logs**: Only essential logs in production build

## Testing Checklist

- [ ] Build succeeds without errors
- [ ] App launches without crashes
- [ ] Permissions requested correctly
- [ ] Voice session starts within 5 seconds
- [ ] AI agent joins and responds
- [ ] Call duration displays and updates
- [ ] Mute/unmute works correctly
- [ ] Session ends cleanly
- [ ] Rapid tap handling works
- [ ] Network error handling works
- [ ] Memory doesn't leak after multiple sessions

## Known Limitations

1. **Single Session**: Only one voice session at a time
2. **No Persistence**: Session lost on app restart
3. **No Recording**: Free tier doesn't include cloud recording
4. **No Text Chat**: Voice-only in current implementation
5. **Basic UI**: Minimal visual feedback (can be enhanced)

## Future Enhancements

1. **Hybrid Mode**: Simultaneous text and voice
2. **Conversation History**: Display chat transcript
3. **Visual Indicators**: Speaking/listening animations
4. **Push-to-Talk**: Optional mode for controlled input
5. **Voice Activity Detection**: Show when user/AI is speaking
6. **Session Persistence**: Resume after app restart
7. **Multiple Languages**: TTS/STT language selection
8. **Custom Prompts**: User-configurable system prompts
9. **Analytics**: Track usage, errors, session duration
10. **Optimization**: Background mode, battery usage

## Troubleshooting Quick Reference

| Issue | Likely Cause | Solution |
|-------|-------------|----------|
| Build fails | Missing dependencies | Run `flutter pub get` |
| Permission error | Manifest not updated | Check AndroidManifest.xml / Info.plist |
| Token error | Invalid credentials | Verify AGORA_APP_ID and AGORA_APP_CERT |
| No AI voice | Backend not running | Start backend server |
| Network error | Wrong backend URL | Check BACKEND_BASE_URL in .env |
| Audio quality issues | Network problems | Test on WiFi with good connection |
| Memory leak | Timer not cancelled | Check dispose() implementation |

## Dependencies Version Reference

```yaml
agora_rtc_engine: ^6.3.2
permission_handler: ^11.3.1
flutter_dotenv: ^5.1.0
http: ^1.2.0
```

All dependencies are compatible with Flutter SDK ^3.7.2.

## Code Style & Conventions

- **Naming**: Snake_case for private methods/fields, camelCase for public
- **Comments**: Only where logic is non-obvious
- **Error Handling**: Try-catch with user-friendly messages
- **Logging**: Prefixed with component name (e.g., `[AgoraVoiceService]`)
- **State Guards**: Always check `mounted` before setState
- **Null Safety**: Leverages Dart's null safety features

## Deployment Notes

### Development
- Use localhost backend URL
- Verbose logging enabled
- Debug mode with hot reload

### Production
- Use HTTPS backend URL
- Disable debug logs (check kDebugMode)
- Enable ProGuard/R8 for Android
- Use release build optimization

### Testing Environments
- **Local**: `http://localhost:8000`
- **Android Emulator**: `http://10.0.2.2:8000`
- **Physical Device**: `http://<local-ip>:8000`
- **Staging**: `https://staging-api.example.com`
- **Production**: `https://api.example.com`

## Support & Resources

- **Agora Documentation**: https://docs.agora.io
- **Flutter SDK Guide**: https://docs.agora.io/en/voice-calling/get-started/get-started-sdk?platform=flutter
- **API Reference**: https://api-ref.agora.io/en/voice-sdk/flutter/6.x/API/rtc_api_overview.html
- **Community**: https://www.agora.io/en/community/
- **GitHub Issues**: Report issues in project repository
