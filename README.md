# Mood-Based AI — Agora Conversational Recommender (Python prototype)

This repository contains a voice-first, text-first Python prototype of a mood-based food recommender.
It uses:
- Agora Conversational AI Engine (scaffolded integration)
- Gemini (optional) or a local rule-based fallback for mood classification
- A CSV dataset `Indian-Food-Data.csv` for food items, moods, calories, and tags

Goals
- Detect user mood via conversation
- Collect optional constraints (calories, taste)
- Recommend food items from the CSV dataset
- Provide a backend-first architecture so a Flutter app can connect via REST/WebSocket

Quick start (local)
1. Create and activate a virtualenv (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and fill values (optional):

```powershell
copy .env.example .env
# Edit .env to add AGORA_APP_ID, GEMINI_API_KEY if available
```

3. Run the server (development):

```powershell
#$env:DATA_CSV = "E:\Hackathons\mood-based-ai\Indian-Food-Data.csv"
python -m uvicorn src.server:app --reload --port 8000
```

4. Test with the included text client:

```powershell
python scripts/text_client.py test-session "I am feeling happy and want something spicy under 500 calories"
```

Architecture notes
- `src/data_loader.py`: loads and filters the CSV dataset
- `src/llm.py`: Gemini client wrapper and `LocalLLMStub` fallback
- `src/conversation.py`: ConversationManager that handles mood detection and recommendations
- `src/recommender.py`: wrapper around dataset recommend()
- `src/logging_store.py`: JSONL-based conversation logs
- `src/agora_connector.py`: Agora REST API connector (join/query/leave)
- `src/server.py`: FastAPI server (text-first endpoints). Voice/streaming endpoints are planned — see below.

Agora integration & voice streaming
- The repository implements an `AgoraConnector` with async REST calls to start/query/stop agents.
- For a backend-forwarding audio model (Flutter → backend → Agora), you will typically either:
	- Have Flutter join an Agora channel and the backend starts an agent that joins the same channel (recommended); audio flows via Agora's real-time network.
	- Or have Flutter stream audio to the backend which forwards audio frames to Agora via WebSocket or other channel. This second path is more complex and currently left as a TODO in `src/agora_connector.py`.

Next steps I can implement for you
- Full voice streaming (receive audio chunks from Flutter, forward to Agora Conversational AI Engine) — needs RTC tokens and possibly customer secret.
- Improve LLM integration to use Gemini official client or the exact API schema for responses.
- Unit tests and CI configuration.

RTC token minting helper
- This repo now includes `src/token_helper.py` and a dev endpoint `POST /api/token/generate` that will mint RTC tokens using `AGORA_APP_ID` and `AGORA_APP_CERT` from the environment.
- For the helper to work you must install the Agora token builder package listed in `requirements.txt` (package name `agora-access-token` in this repo) or the equivalent official builder for your environment.
- Security note: the token generation endpoint must be protected in production. Do not expose your App Certificate to clients.

Manual Agora control from Flutter
- The server exposes manual control endpoints so your Flutter app can call them when needed:
	- POST /api/agent/start (body: channel, rtc_token, optional llm_overrides) — starts an agent that joins channel
	- POST /api/agent/leave (body: agent_id) — stops the agent
	- POST /api/agent/speak (body: agent_id, text, priority, interruptable) — speak TTS
	- POST /api/agent/interrupt (body: agent_id) — interrupt agent
	- GET /api/agent/{agent_id}/history — agent conversation history
	- GET /api/agents — list agents

Add your Agora secrets to `.env` (example placeholders are in `.env.example`).

If you want me to continue, tell me which of these you want prioritized next.
# mood-based-ai

## for updates:
```bash
git pull --rebase
```
This is help us in keeping a clean git history.
