# Flavourey Bot Backend

OpenAI Chat Completions-compatible backend for Flavourey mood-based food ordering assistant.

## Architecture

- **FastAPI server** exposing `/chat/completions` endpoint
- **Gemini AI** via OpenAI-compatible API for LLM
- **Tool calling** for menu search and recommendations
- **Streaming & non-streaming** responses
- **Agora integration** for voice AI

## Setup

### 1. Create Virtual Environment

```powershell
# Navigate to bot_backend directory
cd bot_backend

# Create venv
python -m venv venv

# Activate venv
.\venv\Scripts\Activate.ps1

# If execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Environment Variables

Create `.env` file in `bot_backend/` directory (or use root `.env`):

```env
# Required for text chat
GEMINI_API_KEY=your_gemini_api_key_here

# Optional for text chat
GEMINI_MODEL=gemini-2.5-pro
PORT=8000
DATA_CSV=../Indian-Food-Data.csv
LOGS_DIR=logs

# Required for Conversational AI agent (voice)
AGORA_APP_ID=your_agora_app_id
AGORA_APP_CERT=your_agora_app_certificate
AGORA_CUSTOMER_ID=your_customer_id
AGORA_CUSTOMER_SECRET=your_customer_secret

# Conversational AI LLM configuration
GEMINI_API_KEY=your_GEMINI_API_KEY
LLM_API_URL=http://localhost:8000/chat/completions
LLM_MODEL=gpt-4o-mini

# Text-to-Speech configuration (Microsoft Azure)
TTS_API_KEY=your_azure_tts_key
TTS_REGION=eastus
TTS_VOICE_NAME=en-US-JennyNeural

# Optional Conversational AI settings
AGORA_CONV_AI_BASE_URL=https://api.agora.io/api/conversational-ai-agent/v2
AGORA_AGENT_IDLE_TIMEOUT=120
```

**Note**: For voice integration, you need:
- Agora account with Conversational AI enabled
- Microsoft Azure account for TTS (or use Agora's built-in TTS)
- The LLM_API_URL can point to this same server's `/chat/completions` endpoint
AGORA_APP_ID=your_app_id
AGORA_APP_CERT=your_app_cert
AGORA_CUSTOMER_ID=your_customer_id
AGORA_CUSTOMER_SECRET=your_customer_secret
```

### 4. Run Server

```powershell
# From bot_backend directory
uvicorn src.server:app --reload --port 8000

# Or using python
python -m uvicorn src.server:app --reload --port 8000
```

Server runs at: `http://localhost:8000`

## API Endpoints

### POST /chat/completions

OpenAI Chat Completions-compatible endpoint for Agora Conversational AI.

**Non-streaming Request:**

```powershell
curl -X POST http://localhost:8000/chat/completions `
  -H "Content-Type: application/json" `
  -d '{
    "model": "gemini-2.5-pro",
    "messages": [
      {"role": "user", "content": "I feel stressed, suggest some comfort food"}
    ],
    "tools": [
      {
        "type": "function",
        "function": {
          "name": "search_menu",
          "description": "Search menu items based on mood, dietary restrictions, and budget",
          "parameters": {
            "type": "object",
            "properties": {
              "mood": {"type": "string", "description": "User mood"},
              "max_budget": {"type": "number", "description": "Maximum budget in INR"},
              "dietary": {"type": "string", "enum": ["veg", "non-veg", "vegan", "any"]},
              "allergens_to_avoid": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["mood"]
          }
        }
      }
    ],
    "stream": false
  }'
```

**Streaming Request:**

```powershell
curl -X POST http://localhost:8000/chat/completions `
  -H "Content-Type: application/json" `
  -d '{
    "model": "gemini-2.5-pro",
    "messages": [
      {"role": "user", "content": "Tell me about your food recommendations"}
    ],
    "stream": true
  }'
```

**Response Format:**

Non-streaming:
```json
{
  "id": "chatcmpl-xxx",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "gemini-2.5-pro",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "I'd love to help! ..."
    },
    "finish_reason": "stop"
  }],
  "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
}
```

Streaming (SSE):
```
data: {"id":"chatcmpl-xxx","object":"chat.completion.chunk","created":1234567890,"model":"gemini-2.5-pro","choices":[{"index":0,"delta":{"content":"Hello"},"finish_reason":null}]}

data: {"id":"chatcmpl-xxx","object":"chat.completion.chunk","created":1234567890,"model":"gemini-2.5-pro","choices":[{"index":0,"delta":{"content":" there"},"finish_reason":null}]}

data: [DONE]
```

### Other Endpoints

- `POST /api/ask` - Simple text-based chat (legacy)
- `POST /api/debug/classify` - Debug mood classification
- `POST /api/agent/start` - Start Agora voice agent
- `POST /api/agent/leave` - Stop Agora agent
- `POST /api/token/generate` - Generate RTC token

## Tool Functions

The bot has access to these tools:

### search_menu

Search menu items based on criteria:

```json
{
  "name": "search_menu",
  "parameters": {
    "mood": "stressed",
    "max_budget": 500,
    "dietary": "veg",
    "allergens_to_avoid": ["nuts", "gluten"]
  }
}
```

Returns list of matching menu items with restaurant info.

## Project Structure

```
bot_backend/
├── src/
│   ├── server.py           # FastAPI app with /chat/completions
│   ├── llm.py              # Gemini OpenAI client + tool calling
│   ├── data_loader.py      # Load restaurant/menu data
│   ├── recommender.py      # Menu search and filtering
│   ├── logging_store.py    # Conversation logging
│   ├── conversation.py     # Conversation management
│   ├── agora_connector.py  # Agora API client
│   └── token_helper.py     # RTC token generation
├── data/
│   └── restaurants.json    # Restaurant & menu data
├── logs/                   # Conversation logs (auto-created)
├── requirements.txt
├── .env
└── README.md
```

## Development

### Adding New Menu Items

Edit `data/restaurants.json`:

```json
{
  "id": "item_xxx",
  "restaurant_id": "rest_xxx",
  "name": "Dish Name",
  "price": 250,
  "veg": true,
  "spice_level": "mild",
  "allergens": ["dairy"],
  "tags": ["comfort", "healthy"],
  "moods": ["happy", "relaxed"],
  "calories": 300
}
```

### Customizing System Prompt

Edit `FLAVOUREY_SYSTEM_PROMPT` in `src/llm.py`.

### Adding New Tools

1. Define tool schema in `/chat/completions` request
2. Implement tool function in `src/recommender.py`
3. Register in tool executor (see `src/server.py`)

## Testing

### Text Chat

```powershell
# Health check
curl http://localhost:8000/

# Test chat completions (non-streaming)
curl -X POST http://localhost:8000/chat/completions `
  -H "Content-Type: application/json" `
  -d '{
    "model": "gemini-2.5-pro",
    "messages": [{"role": "user", "content": "Hello!"}],
    "stream": false
  }'

# Test with tools
curl -X POST http://localhost:8000/chat/completions `
  -H "Content-Type: application/json" `
  -d @test_tool_request.json
```

### Conversational AI Agent (Voice)

```powershell
# Start a Conversational AI agent
curl -X POST http://localhost:8000/api/ai/agent/start `
  -H "Content-Type: application/json" `
  -d '{
    "channelName": "test_channel_123",
    "rtcToken": "YOUR_RTC_TOKEN",
    "sessionKey": "user-session-123",
    "userContext": {
      "mood": "happy",
      "allergies": ["peanuts", "shellfish"]
    }
  }'

# Response:
# {
#   "agentId": "agent_abc123",
#   "status": "RUNNING",
#   "sessionKey": "user-session-123"
# }

# Stop a Conversational AI agent
curl -X POST http://localhost:8000/api/ai/agent/stop `
  -H "Content-Type: application/json" `
  -d '{
    "sessionKey": "user-session-123"
  }'

# Response:
# {
#   "ok": true,
#   "agentStopped": true
# }

# Generate RTC token (for agent and client)
curl -X POST "http://localhost:8000/api/token/generate?channel=test_channel_123&uid=0"

# Response:
# {
#   "token": "006abc...",
#   "app_id": "your_app_id",
#   "channel": "test_channel_123",
#   "uid": 0
# }
```

## Troubleshooting

### GEMINI_API_KEY not set
- Ensure `.env` file exists in `bot_backend/` directory
- Check API key is valid at https://aistudio.google.com/

### Module not found errors
- Activate virtual environment: `.\venv\Scripts\Activate.ps1`
- Reinstall dependencies: `pip install -r requirements.txt`

### Port already in use
- Change PORT in `.env` or use: `uvicorn src.server:app --port 8001`

### Tool calling not working
- Ensure Gemini model supports function calling (gemini-2.5-pro or gemini-2.5-pro)
- Check tool schema matches OpenAI format

## Production Deployment

1. Set `reload=False` in uvicorn
2. Use production ASGI server (gunicorn + uvicorn workers)
3. Set up proper logging
4. Use environment variables for secrets
5. Add rate limiting and authentication
6. Configure CORS if needed

```powershell
# Production run
gunicorn src.server:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## License

See LICENSE file in root directory.
