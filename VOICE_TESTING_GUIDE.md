# Agora Voice Integration - Testing Guide

## Overview
This document outlines how to test the Agora Conversational AI voice integration in the Flavourey Flutter app.

## Prerequisites

1. **Environment Setup**
   - Ensure `.env` file is properly configured with:
     - `AGORA_APP_ID`: Your Agora App ID
     - `AGORA_APP_CERT`: Your Agora App Certificate
     - `BACKEND_BASE_URL`: Backend server URL (default: http://localhost:8000)

2. **Backend Service**
   - The Python backend must be running at the configured `BACKEND_BASE_URL`
   - Backend should expose:
     - `POST /api/token/generate` - Generates RTC tokens
     - `POST /api/agent/start` - Starts Agora AI agent
     - `POST /api/agent/leave` - Stops Agora AI agent

3. **Dependencies**
   - Run `flutter pub get` to install all dependencies
   - Key dependencies:
     - `agora_rtc_engine: ^6.3.2`
     - `permission_handler: ^11.3.1`
     - `flutter_dotenv: ^5.1.0`
     - `http: ^1.2.0`

## Stage 1: Build-Only Testing

**Objective**: Verify the app compiles and launches without runtime errors.

### Steps:
1. Install dependencies:
   ```powershell
   flutter pub get
   ```

2. Build and run the app:
   ```powershell
   flutter run
   ```

3. Navigate to the Chatbot page from the main navigation.

### Expected Results:
- App builds successfully without compilation errors
- App launches and displays the main navigation
- Chatbot page shows "Coming Soon" screen with a green phone icon in the app bar
- No runtime exceptions in the debug console

## Stage 2: Permission & Initialization Testing

**Objective**: Verify Agora SDK initialization and microphone permissions.

### Steps:
1. Launch the app on a physical device (recommended) or emulator
2. Navigate to the Chatbot page
3. Observe the debug console for initialization logs

### Expected Results:
- Console should show: `[AgoraVoiceService] Initialized successfully`
- No permission errors
- If permissions are not granted, app should prompt for microphone access

### Troubleshooting:
- **Android**: Check `AndroidManifest.xml` includes `RECORD_AUDIO` permission
- **iOS**: Verify `NSMicrophoneUsageDescription` is in `Info.plist`
- If permission is denied, manually grant it in device settings and restart the app

## Stage 3: Join/Leave Channel Testing

**Objective**: Test basic Agora channel operations without AI agent.

### Steps:
1. Start the backend server:
   ```powershell
   cd bot_backend
   python -m uvicorn src.server:app --reload --port 8000
   ```

2. Ensure backend is accessible from your device:
   - For Android emulator: Use `http://10.0.2.2:8000`
   - For physical device: Use your computer's local IP (e.g., `http://192.168.1.100:8000`)
   - Update `BACKEND_BASE_URL` in `.env` accordingly

3. In the app, tap the green phone icon in the app bar

### Expected Results:
- Loading state (button becomes disabled/grey)
- Console logs:
  ```
  [VoiceSessionApi] Generating token for channel: voice_user_...
  [VoiceSessionApi] Token generated, starting agent...
  [VoiceSessionApi] Agent started: <agent_id>
  [AgoraVoiceService] Joining channel: voice_user_... with uid: ...
  [AgoraVoiceService] Joined channel: voice_user_..., uid: ...
  ```
- Icon changes to red call-end icon
- Call duration timer appears (00:00, 00:01, ...)
- Icon changes from chat bubble to green microphone
- Text changes to "Voice Active"
- Mute/Unmute button appears
- Success snackbar: "Voice session started"

4. Tap the red call-end icon to leave

### Expected Results:
- Console logs:
  ```
  [AgoraVoiceService] Left channel
  [VoiceSessionApi] Session stopped successfully
  ```
- Icon changes back to green phone icon
- Call duration timer disappears
- UI returns to "Coming Soon" state
- Snackbar: "Voice session ended"

### Troubleshooting:
- **Network errors**: Check backend URL configuration
- **Token generation fails**: Verify `AGORA_APP_ID` and `AGORA_APP_CERT` in backend `.env`
- **Join fails**: Check Agora App ID matches between backend and Flutter app
- **No agent joining**: Verify Agora Conversational AI Engine is properly configured

## Stage 4: Full AI Conversation Testing

**Objective**: Test end-to-end voice conversation with AI agent.

### Steps:
1. Ensure backend is running with proper Gemini API configuration
2. Start a voice session (tap phone icon)
3. Wait for remote user joined log:
   ```
   [AgoraVoiceService] Remote user joined: <uid> (AI agent)
   ```
4. Speak naturally into the microphone (e.g., "Hello, I'm feeling happy today")
5. Listen for AI agent's voice response

### Expected Results:
- Remote user joins within 2-5 seconds
- Audio from AI agent is clear and intelligible
- AI responds appropriately to user's speech
- Conversation flows naturally
- No audio glitches or drops

### Test Scenarios:
1. **Basic greeting**: "Hello, how are you?"
2. **Mood detection**: "I'm feeling stressed and need comfort food"
3. **Food recommendation**: "What should I eat?"
4. **Interruption**: Speak while AI is talking (AI should handle gracefully)

### Troubleshooting:
- **No AI voice heard**: Check backend logs for Agora agent start errors
- **Audio quality issues**: Check network bandwidth
- **AI not responding**: Verify Gemini API key and LLM configuration in backend
- **Remote user not joining**: Agent may have failed to start; check backend logs

## Stage 5: Mute/Unmute Testing

**Objective**: Verify local audio muting functionality.

### Steps:
1. Start a voice session
2. Speak something and verify AI responds
3. Tap the "Mute" button
4. Speak again

### Expected Results:
- Button label changes to "Unmute"
- Button color changes to red
- Console log: `[AgoraVoiceService] Local audio muted`
- AI should not respond to speech (no audio being transmitted)

5. Tap "Unmute" button
6. Speak again

### Expected Results:
- Button label changes to "Mute"
- Button color changes to green
- Console log: `[AgoraVoiceService] Local audio unmuted`
- AI responds to speech normally

## Stage 6: Edge Cases & Error Handling

### Test Case 1: Rapid Button Taps
**Steps**: Tap the phone icon multiple times rapidly

**Expected**: 
- Button becomes disabled during operation
- Only one session starts
- No duplicate agent creation
- Console shows guard log: `[AgoraVoiceService] Already joined a channel`

### Test Case 2: Network Interruption
**Steps**: 
1. Start voice session
2. Disable device network (airplane mode)
3. Wait 10 seconds
4. Re-enable network

**Expected**:
- Console logs connection state changes
- App doesn't crash
- Audio may resume or require manual reconnection

### Test Case 3: App Backgrounding
**Steps**:
1. Start voice session
2. Press home button (background app)
3. Wait 30 seconds
4. Return to app

**Expected**:
- Session state is maintained
- Call duration continues accurately
- Audio resumes (platform-dependent)

### Test Case 4: Backend Offline
**Steps**:
1. Stop backend server
2. Attempt to start voice session

**Expected**:
- Error snackbar appears with descriptive message
- App doesn't crash
- Button returns to idle state
- No Agora channel is joined

### Test Case 5: Invalid Token
**Steps**: Modify backend to return expired or invalid token

**Expected**:
- Join fails with connection error
- Console logs error
- Error snackbar displayed
- App returns to idle state

### Test Case 6: Permission Denied
**Steps**:
1. Deny microphone permission in device settings
2. Attempt to start voice session

**Expected**:
- Exception caught during initialization
- Error snackbar: "Microphone permission is required for voice calls"
- No channel join attempted

## Stage 7: Performance & Resource Testing

### Memory Monitoring
- Use Flutter DevTools memory profiler
- Start/stop voice sessions 10 times
- Check for memory leaks

**Expected**: Memory usage should stabilize after a few cycles

### Battery Testing
- Monitor battery drain during extended voice session (5-10 minutes)
- Compare with baseline (app idle)

**Expected**: Reasonable battery consumption (< 10% for 10-minute call)

### Audio Quality
- Test on different devices (iOS/Android)
- Test on different network conditions (WiFi/4G/poor signal)
- Check for echo, feedback, or distortion

**Expected**: Clear audio on good network, graceful degradation on poor network

## Common Issues & Solutions

### Issue: "Engine not initialized" error
**Solution**: Ensure `initialize()` is called in `initState` and completes before joining channel

### Issue: No remote audio heard
**Solution**: 
1. Check backend logs for agent start confirmation
2. Verify Agora Console settings (Conversational AI Engine enabled)
3. Ensure proper LLM configuration in backend

### Issue: Permission request doesn't appear
**Solution**:
1. Verify platform-specific permission configurations
2. Check that `permission_handler` is properly installed
3. Try on physical device instead of simulator

### Issue: Token generation fails
**Solution**:
1. Verify `AGORA_APP_ID` and `AGORA_APP_CERT` match in both `.env` files
2. Check backend server logs for detailed error
3. Ensure token generation endpoint is accessible

### Issue: Call duration not updating
**Solution**: Check that timer is started in `_startCallDurationTimer()` and state updates are called within `if (mounted)` check

## Success Criteria

A successful integration should demonstrate:
- ✅ App launches without errors
- ✅ Microphone permissions properly requested and handled
- ✅ Voice session starts within 3-5 seconds
- ✅ AI agent joins channel and responds to speech
- ✅ Clear audio quality in both directions
- ✅ Call duration displays accurately
- ✅ Mute/unmute functions correctly
- ✅ Session ends cleanly without errors
- ✅ Error cases handled gracefully with user feedback
- ✅ No memory leaks after multiple sessions

## Next Steps

After successful testing:
1. Add text chat UI alongside voice (hybrid mode)
2. Implement conversation history display
3. Add visual feedback for AI speaking/listening states
4. Implement push-to-talk mode as an option
5. Add voice activity detection indicators
6. Implement session persistence across app restarts
7. Add analytics/logging for production monitoring

## Resources

- [Agora Flutter SDK Documentation](https://docs.agora.io/en/voice-calling/get-started/get-started-sdk?platform=flutter)
- [Agora Conversational AI Engine](https://docs.agora.io/en/conversational-ai/overview/product-overview)
- [Flutter Permission Handler](https://pub.dev/packages/permission_handler)
- Backend API documentation: `bot_backend/README.md`
