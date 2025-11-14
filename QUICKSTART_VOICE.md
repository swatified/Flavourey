# Quick Start Guide - Voice Integration

## Prerequisites Check

Before testing, ensure you have:

1. **Backend Running**
   ```powershell
   cd bot_backend
   python -m uvicorn src.server:app --reload --port 8000
   ```

2. **Environment Variables Set**
   - Open `.env` file in the project root
   - Verify `AGORA_APP_ID` is set (currently: `55a8e56af4034120a94c33987000ffed`)
   - Verify `BACKEND_BASE_URL` is set
     - For Android emulator: `http://10.0.2.2:8000`
     - For physical device: `http://<your-computer-ip>:8000`
     - For iOS simulator: `http://localhost:8000`

## Quick Test (5 Minutes)

### Step 1: Update Backend URL (if needed)

If testing on physical device, update `.env`:
```properties
BACKEND_BASE_URL=http://192.168.1.100:8000  # Replace with your IP
```

To find your IP:
```powershell
ipconfig
# Look for "IPv4 Address" under your active network adapter
```

### Step 2: Run the App

```powershell
# From project root
flutter run
```

Or press **F5** in VS Code.

### Step 3: Test Voice Call

1. Navigate to **Chatbot** page (bottom navigation icon)
2. Tap the **green phone icon** in the app bar (top right)
3. **Grant microphone permission** when prompted
4. Wait for:
   - Icon to turn **red**
   - **Duration timer** to appear (00:00, 00:01...)
   - Icon in center to turn into a **green microphone**
5. **Speak**: "Hello, I'm feeling happy today"
6. **Listen** for AI agent's voice response
7. Tap **red call-end icon** to stop
8. Verify UI returns to idle state

## Expected Console Output

### Successful Flow:
```
[AgoraVoiceService] Initialized successfully
[VoiceSessionApi] Generating token for channel: voice_user_...
[VoiceSessionApi] Token generated, starting agent...
[VoiceSessionApi] Agent started: agent_abc123
[AgoraVoiceService] Joining channel: voice_user_... with uid: 123456
[AgoraVoiceService] Joined channel: voice_user_..., uid: 123456
[AgoraVoiceService] Remote user joined: 0 (AI agent)
[AgoraVoiceService] Left channel
[VoiceSessionApi] Session stopped successfully
```

## Troubleshooting

### Issue: "Failed to start voice: Failed to generate token"
**Cause**: Backend not accessible
**Fix**: 
1. Verify backend is running (`http://localhost:8000` should show API info)
2. Update `BACKEND_BASE_URL` in `.env` with correct IP/URL
3. Restart the app

### Issue: "Microphone permission is required"
**Cause**: Permission denied
**Fix**:
1. Go to device Settings → Apps → Flavourey → Permissions
2. Enable Microphone
3. Restart the app

### Issue: No AI voice heard
**Cause**: AI agent not joining or backend LLM not configured
**Fix**:
1. Check backend logs for agent start confirmation
2. Verify `GEMINI_API_KEY` in backend `.env`
3. Check console for "Remote user joined" log

### Issue: "Engine not initialized"
**Cause**: Initialization failed
**Fix**:
1. Check `AGORA_APP_ID` in `.env` is correct
2. Restart the app
3. Check console for initialization errors

## Feature Testing Checklist

Test these features in order:

- [ ] App launches without errors
- [ ] Chatbot page displays correctly
- [ ] Tap phone icon starts session (turns red, shows timer)
- [ ] Permission prompt appears (first time only)
- [ ] AI agent joins (console log: "Remote user joined")
- [ ] AI responds to voice input
- [ ] Call duration updates every second
- [ ] Tap "Mute" button mutes microphone
- [ ] AI stops responding when muted
- [ ] Tap "Unmute" restores audio
- [ ] Tap call-end icon stops session
- [ ] UI returns to idle state
- [ ] Can start another session after stopping

## Advanced Testing

### Test Multiple Sessions
1. Start and stop session 3 times
2. Verify no memory leaks (check Flutter DevTools)
3. Verify no leftover timers

### Test Rapid Tapping
1. Tap phone icon 5 times rapidly
2. Verify only one session starts
3. Verify button stays disabled during operation

### Test Network Interruption
1. Start session
2. Enable airplane mode for 5 seconds
3. Disable airplane mode
4. Verify connection recovers or shows appropriate error

## Next Steps

After successful testing:

1. **Customize AI Prompt**: Edit backend `llm_config` in `/api/agent/start` endpoint
2. **Add Text Chat**: Integrate existing text chat with voice (hybrid mode)
3. **Improve UI**: Add speaking/listening animations
4. **Add Features**: See `VOICE_IMPLEMENTATION.md` for enhancement ideas

## Getting Help

If you encounter issues:

1. Check console logs for detailed error messages
2. Review `VOICE_TESTING_GUIDE.md` for comprehensive testing scenarios
3. Review `VOICE_IMPLEMENTATION.md` for technical details
4. Check backend logs: `bot_backend/logs/`

## Configuration Reference

**Critical Environment Variables:**
- `AGORA_APP_ID`: Your Agora application ID
- `AGORA_APP_CERT`: Your Agora app certificate (backend only)
- `BACKEND_BASE_URL`: Backend API endpoint
- `GEMINI_API_KEY`: Gemini API key (backend only)

**Files Modified:**
- `pubspec.yaml` - Added dependencies
- `android/app/src/main/AndroidManifest.xml` - Added audio permissions
- `ios/Runner/Info.plist` - Added microphone usage description
- `lib/main.dart` - Added config loading
- `lib/pages/chatbot_page.dart` - Complete voice UI implementation
- `lib/services/agora_voice_service.dart` - NEW: Agora SDK wrapper
- `lib/services/voice_session_api.dart` - NEW: Backend API client
- `lib/services/app_config.dart` - NEW: Configuration management
- `.env` - Added `BACKEND_BASE_URL`

## Success!

If you see:
- ✅ AI agent joins and speaks
- ✅ Duration timer updates
- ✅ Mute/unmute works
- ✅ Session ends cleanly

**Congratulations! The integration is working correctly.**

You can now build upon this foundation to add more features like text chat, conversation history, and advanced UI elements.
