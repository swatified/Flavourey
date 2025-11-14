# Voice Feature - Agora Conversational AI Integration

## What is this?

The **phone icon** in the chatbot page now enables **real-time voice conversations** with an AI assistant powered by:
- **Agora RTC**: Real-time voice communication
- **Agora Conversational AI Engine**: AI agent orchestration
- **Gemini 2.5 Pro**: Large language model for intelligent responses

## Quick Demo

1. **Start Backend**:
   ```powershell
   cd bot_backend
   python -m uvicorn src.server:app --reload --port 8000
   ```

2. **Run App**:
   ```powershell
   flutter run
   ```

3. **Use Voice**:
   - Navigate to **Chatbot** tab
   - Tap **green phone icon** (top-right)
   - Grant microphone permission
   - **Speak naturally**: "Hello, I'm feeling happy today"
   - **Listen** for AI response
   - Tap **red icon** to end call

## Features

✅ **Real-time Voice**: Continuous conversation, no push-to-talk needed  
✅ **AI Agent**: Automatic speech recognition → LLM → text-to-speech  
✅ **Call Duration**: Live timer shows call length  
✅ **Mute/Unmute**: Control your microphone during calls  
✅ **Error Handling**: Clear error messages for network/permission issues  
✅ **Clean UI**: Simple, intuitive interface  

## Technical Stack

### Frontend (Flutter)
- `agora_rtc_engine: ^6.3.2` - Voice SDK
- `permission_handler: ^11.3.1` - Mic permissions
- `flutter_dotenv: ^5.1.0` - Configuration
- `http: ^1.2.0` - API client

### Backend (Python)
- FastAPI server with Agora REST API integration
- Token generation for secure channel access
- AI agent lifecycle management

### Agora Services
- RTC (Real-Time Communication) for audio transport
- Conversational AI Engine for AI agent hosting

## Configuration

Edit `.env` in project root:

```properties
# Agora credentials
AGORA_APP_ID=your_app_id_here

# Backend endpoint
BACKEND_BASE_URL=http://localhost:8000
```

**Note**: For physical devices, use your computer's IP instead of `localhost`.

## Documentation

| Document | Purpose | Audience |
|----------|---------|----------|
| `QUICKSTART_VOICE.md` | 5-minute test guide | All users |
| `VOICE_TESTING_GUIDE.md` | Comprehensive QA | Testers |
| `VOICE_IMPLEMENTATION.md` | Technical details | Developers |
| `CHANGELOG_VOICE.md` | Complete change list | Developers |

## Troubleshooting

### "Failed to start voice"
→ Backend not running or wrong URL in `.env`

### "Permission required"
→ Grant microphone access in device settings

### No AI voice heard
→ Check backend logs, verify Gemini API key

### Poor audio quality
→ Test on WiFi with good connection

See `VOICE_TESTING_GUIDE.md` for more solutions.

## Architecture

```
Flutter App (chatbot_page.dart)
    ↓
Agora RTC SDK (agora_voice_service.dart)
    ↓
Agora RTC Network
    ↓
Agora Conversational AI Engine
    ↓
Custom LLM Backend (Gemini 2.5 Pro)
```

## Limitations

- Single session at a time (one call)
- No session persistence (lost on app restart)
- Free tier usage (limited monthly minutes)
- Audio only (no video)

## Next Steps

After successful testing:
1. Add text chat UI alongside voice
2. Implement conversation history
3. Add visual feedback for AI speaking/listening
4. Optimize for production deployment

## Status

- [x] Implementation complete
- [x] Documentation complete
- [ ] Testing pending (see `QUICKSTART_VOICE.md`)
- [ ] Production deployment pending

## Questions?

Review the documentation in order:
1. `QUICKSTART_VOICE.md` - Start here
2. `VOICE_TESTING_GUIDE.md` - For testing
3. `VOICE_IMPLEMENTATION.md` - For technical details
