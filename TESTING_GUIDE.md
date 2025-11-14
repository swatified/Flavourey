# Complete App Testing Guide

## ✅ Backend Status: RUNNING

Your backend server is now running on **http://localhost:8000** with:
- ✅ Gemini 2.5 Pro LLM integration
- ✅ Agora Chat REST API: https://a61.chat.agora.io
- ✅ Agora Chat WebSocket: wss://mysync-api-61.chat.agora.io
- ✅ OpenAI Chat Completions endpoint: http://localhost:8000/chat/completions

---

## Step-by-Step Testing Process

### STEP 1: Backend Server ✅ DONE

The server is already running. You should see:
```
INFO: Application startup complete.
INFO: Uvicorn running on http://0.0.0.0:8000
```

Keep this terminal running!

---

### STEP 2: Test Backend API (Optional but Recommended)

Open a **NEW terminal** and test the backend:

```powershell
# Activate venv
D:\SHRI1\github\mood-based-ai\.venv\Scripts\Activate.ps1

# Navigate to backend
cd D:\SHRI1\github\mood-based-ai\bot_backend

# Run tests
python tests\test_agora_compat.py
```

Expected output:
- ✅ Health check passes
- ✅ Non-streaming rejected (400 error)
- ✅ Streaming works with food-related responses
- ✅ [DONE] sentinel received

---

### STEP 3: Build and Run Flutter App

Open a **NEW terminal** for Flutter:

```powershell
# Navigate to project root (where pubspec.yaml is)
cd D:\SHRI1\github\mood-based-ai

# Get Flutter dependencies
flutter pub get

# Check connected devices
flutter devices

# Run on your preferred device
flutter run -d <device-name>

# OR for Chrome web:
flutter run -d chrome

# OR for Windows desktop:
flutter run -d windows
```

---

### STEP 4: Test App Features

Once the Flutter app launches:

#### Test 1: Basic Navigation
- [ ] App opens to splash screen
- [ ] Navigate to home page
- [ ] See food items from dataset

#### Test 2: Mood-Based Search
- [ ] Select a mood (happy, sad, stressed, etc.)
- [ ] See food recommendations matching mood
- [ ] Check if recommendations make sense

#### Test 3: Cart Functionality
- [ ] Add items to cart
- [ ] View cart page
- [ ] Check item quantities and prices

#### Test 4: Backend Integration (if implemented)
- [ ] Voice/chat interaction with Agora
- [ ] LLM responses from Gemini
- [ ] Real-time updates

---

## Common Issues & Solutions

### Issue 1: Backend Not Responding
**Symptom:** Flutter app can't connect to backend

**Solution:**
```powershell
# Check if backend is running
curl http://localhost:8000/health

# Should return: {"status":"ok"}
```

### Issue 2: Flutter Build Errors
**Symptom:** `flutter run` fails

**Solution:**
```powershell
# Clean and rebuild
flutter clean
flutter pub get
flutter run
```

### Issue 3: Device Not Found
**Symptom:** No devices available

**Solution:**
```powershell
# List available devices
flutter devices

# For web:
flutter run -d chrome

# For Windows:
flutter run -d windows

# For Android (with emulator running):
flutter run -d <emulator-id>
```

### Issue 4: Port 8000 Already in Use
**Symptom:** Backend won't start

**Solution:**
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace <PID> with actual process ID)
taskkill /PID <PID> /F

# Or change port in .env:
# PORT=8001
```

---

## Testing Checklist

### Backend Testing
- [x] Server starts successfully
- [ ] Health endpoint responds
- [ ] /chat/completions accepts requests
- [ ] Streaming works
- [ ] Gemini integration working
- [ ] Agora Chat config loaded

### Flutter App Testing
- [ ] App builds without errors
- [ ] Splash screen displays
- [ ] Home page shows food items
- [ ] Dish details page works
- [ ] Cart functionality works
- [ ] Navigation between pages works

### Integration Testing
- [ ] Flutter app connects to backend
- [ ] Voice agent starts (if implemented)
- [ ] LLM responses received
- [ ] Food recommendations work
- [ ] Order placement works

---

## Next Steps After Testing

### If Everything Works ✅
1. Test end-to-end user flow
2. Try different moods and preferences
3. Test error scenarios
4. Optimize performance
5. Deploy to production

### If Issues Found ❌
1. Check console logs (backend terminal)
2. Check Flutter debug console
3. Verify environment variables in `.env`
4. Check API keys are valid
5. Review error messages

---

## Monitoring During Testing

### Backend Terminal
Watch for:
```
INFO: 127.0.0.1:XXXXX - "POST /chat/completions HTTP/1.1" 200 OK
INFO: Creating streaming completion with model: gemini-2.5-pro
```

### Flutter Console
Watch for:
```
D/FlutterView: Successfully connected to backend
I/flutter: Loaded X food items
```

---

## Quick Commands Reference

```powershell
# Start backend
cd D:\SHRI1\github\mood-based-ai\bot_backend
python main.py

# Test backend
python tests\test_agora_compat.py

# Run Flutter app
cd D:\SHRI1\github\mood-based-ai
flutter run -d chrome

# Check health
curl http://localhost:8000/health

# View logs
# Backend logs are in terminal
# Flutter logs are in debug console
```

---

## Architecture Overview

```
┌─────────────────┐
│  Flutter App    │
│  (Frontend)     │
└────────┬────────┘
         │
         │ HTTP/WebSocket
         ▼
┌─────────────────┐
│  FastAPI Server │
│  main.py:8000   │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌─────┐   ┌─────────┐
│Gemini│   │ Agora   │
│ API  │   │Chat/RTC │
└──────┘   └─────────┘
```

---

## Success Indicators

Your testing is successful when:
1. ✅ Backend responds to health checks
2. ✅ Flutter app builds and runs
3. ✅ You can browse food items
4. ✅ Mood-based recommendations work
5. ✅ Cart operations succeed
6. ✅ No critical errors in consoles

---

## Support

If you encounter issues:
1. Check both terminal outputs (backend + Flutter)
2. Verify `.env` file has all required values
3. Ensure all dependencies are installed
4. Check firewall isn't blocking port 8000
5. Try restarting both backend and Flutter app

Good luck with testing! 🚀
