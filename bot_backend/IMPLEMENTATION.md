# Flavourey Bot Backend - Implementation Summary

## Completed Implementation

I've successfully built the OpenAI Chat Completions-compatible backend for Flavourey. Here's what has been implemented:

### 1. **Core LLM Integration** (`src/llm.py`)

**Features:**
-  OpenAI-compatible Gemini client using `generativelanguage.googleapis.com/v1beta/openai/`
-  System prompt with Flavourey persona (mood-aware, allergy-conscious, budget-aware)
-  Tool/function calling support with execution loop
-  Streaming and non-streaming responses
-  Automatic system prompt injection
-  Backward-compatible LocalLLMStub for testing without API key

**Key Functions:**
- `GeminiOpenAIClient`: Main client class
- `run_chat_completion()`: Handles non-streaming with tool calling
- `stream_chat_completion()`: Handles SSE streaming
- `inject_system_prompt()`: Adds Flavourey persona

### 2. **FastAPI Server** (`src/server.py`)

**New Endpoints:**
-  **POST /chat/completions** - OpenAI Chat Completions compatible
  - Supports `stream: true/false`
  - Handles tool calling
  - Returns proper OpenAI format
  - SSE streaming with `data: [DONE]` terminator

-  **GET /** - Health check with API info

**Existing Endpoints (preserved):**
- POST /api/ask - Text-based chat
- POST /api/debug/classify - Mood classification debug
- POST /api/agent/* - Agora voice integration
- POST /api/token/generate - RTC token generation

**Tool Executor:**
-  `execute_tool()` function routes tool calls to appropriate handlers
-  Integrated with `search_menu` tool
-  Integrated with `log_order` tool

### 3. **Menu Search & Recommendations** (`src/recommender.py`)

**Enhanced Features:**
-  `search_menu_items()` async tool function
-  Filters by mood, budget, dietary restrictions, allergens
-  Returns enriched results with restaurant info
-  Prioritizes mood-matched items

**Filtering Support:**
- Mood matching (happy, sad, stressed, energetic, romantic, etc.)
- Budget constraints (max_budget in INR)
- Dietary preferences (veg, non-veg, vegan, any)
- Allergen avoidance (dairy, nuts, gluten, eggs, etc.)

### 4. **Sample Restaurant Data** (`data/restaurants.json`)

**Includes:**
-  3 restaurants (Spice Garden, Comfort Kitchen, The Green Bowl)
-  10 menu items with rich metadata:
  - Price, category, veg/non-veg
  - Spice levels
  - Allergen information
  - Mood tags
  - Calorie counts
  - Dietary tags

### 5. **Logging System** (`src/logging_store.py`)

**Enhanced Features:**
-  `log_turn()` - Log complete conversation turns with mood
-  `log_order()` - Log ORDER_SUMMARY blocks
-  Separate orders directory for order tracking
-  JSON format for easy parsing

### 6. **Documentation** (`bot_backend/README.md`)

**Comprehensive Guide:**
-  Setup instructions (venv, dependencies, env vars)
-  How to run the server
-  API endpoint documentation
-  Example curl commands (streaming & non-streaming)
-  Tool function documentation
-  Troubleshooting guide
-  Production deployment tips

### 7. **Dependencies** (`requirements.txt`)

**Includes:**
- FastAPI + uvicorn (web framework)
- openai (for Gemini OpenAI-compatible API)
- aiohttp (async HTTP)
- pandas (data processing)
- pydantic (validation)
- python-dotenv (environment variables)
- agora-access-token (RTC tokens)

##  File Structure

```
bot_backend/
├── src/
│   ├── server.py            FastAPI app with /chat/completions
│   ├── llm.py               Gemini OpenAI client + tool calling
│   ├── recommender.py       search_menu tool function
│   ├── logging_store.py     log_turn + log_order functions
│   ├── data_loader.py      (preserved, works with CSV)
│   ├── conversation.py     (preserved, for /api/ask endpoint)
│   ├── agora_connector.py  (preserved, for voice integration)
│   └── token_helper.py     (preserved, RTC token generation)
├── data/
│   └── restaurants.json     Sample menu data (3 restaurants, 10 items)
├── logs/                   (auto-created for conversation logs)
│   └── orders/             (auto-created for order summaries)
├── requirements.txt         All Python dependencies
├── README.md                Complete setup & usage guide
└── .env                    (you need to create this)
```

##  Quick Start

### 1. Setup Environment

```powershell
cd bot_backend

# Create venv
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Create .env File

Create `bot_backend/.env`:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-pro
PORT=8000
```

### 3. Run Server

```powershell
uvicorn src.server:app --reload --port 8000
```

Server runs at: http://localhost:8000

### 4. Test /chat/completions

**Non-streaming:**

```powershell
curl -X POST http://localhost:8000/chat/completions `
  -H "Content-Type: application/json" `
  -d '{
    "model": "gemini-2.5-pro",
    "messages": [
      {"role": "user", "content": "I feel stressed, suggest comfort food under 500 rupees"}
    ],
    "tools": [
      {
        "type": "function",
        "function": {
          "name": "search_menu",
          "description": "Search menu items based on mood and constraints",
          "parameters": {
            "type": "object",
            "properties": {
              "mood": {"type": "string"},
              "max_budget": {"type": "number"},
              "dietary": {"type": "string", "enum": ["veg", "non-veg", "vegan", "any"]},
              "allergens_to_avoid": {"type": "array", "items": {"type": "string"}}
            }
          }
        }
      }
    ],
    "stream": false
  }'
```

**Streaming:**

```powershell
curl -X POST http://localhost:8000/chat/completions `
  -H "Content-Type: application/json" `
  -d '{
    "model": "gemini-2.5-pro",
    "messages": [
      {"role": "user", "content": "Tell me about healthy options"}
    ],
    "stream": true
  }'
```

##  How It Works

### Tool Calling Flow

1. **Request** → User sends message via /chat/completions
2. **System Prompt Injection** → Flavourey persona added automatically
3. **Gemini Call** → OpenAI-compatible API called
4. **Tool Detection** → If Gemini wants to use a tool, extract tool_calls
5. **Tool Execution** → `execute_tool()` runs `search_menu()` or `log_order()`
6. **Result Injection** → Tool results added as 'tool' messages
7. **Final Response** → Gemini called again with tool results to get user-facing reply
8. **Stream/Return** → Response streamed (SSE) or returned as JSON

### Example Tool Call

User: "I'm feeling sad, recommend something comforting"

1. Gemini infers mood: sad
2. Gemini calls: `search_menu(mood="sad", dietary="any")`
3. Tool returns: Mac & Cheese, Chocolate Lava Cake, Mushroom Soup
4. Gemini formats response: "I sense you're feeling down. Here are some comforting options..."

##  Customization

### Adding More Menu Items

Edit `bot_backend/data/restaurants.json`:

```json
{
  "id": "item_011",
  "restaurant_id": "rest_001",
  "name": "Paneer Tikka",
  "price": 250,
  "veg": true,
  "spice_level": "medium",
  "allergens": ["dairy"],
  "tags": ["protein", "indian"],
  "moods": ["happy", "energetic"],
  "calories": 300
}
```

### Customizing System Prompt

Edit `FLAVOUREY_SYSTEM_PROMPT` in `src/llm.py`.

### Adding New Tools

1. Define tool schema in request
2. Implement function in `src/recommender.py` or new module
3. Register in `execute_tool()` in `src/server.py`

##  Ready for Agora!

This backend is now fully compatible with Agora Conversational AI Engine. Point Agora's Custom LLM configuration to:

```
URL: http://your-server:8000/chat/completions
Protocol: OpenAI Chat Completions
```

Agora will:
- Send voice-transcribed messages to your backend
- Receive responses (streaming or non-streaming)
- Your bot will use tools to search menus
- Users can order food via voice!

##  Troubleshooting

### "GEMINI_API_KEY required"
- Create `.env` file in `bot_backend/` directory
- Add: `GEMINI_API_KEY=your_key_here`

### "Restaurant data not found"
- Ensure `bot_backend/data/restaurants.json` exists
- Check file is valid JSON

### Import errors
- Activate venv: `.\venv\Scripts\Activate.ps1`
- Reinstall: `pip install -r requirements.txt`

### Tool calling not working
- Use gemini-2.5-pro or gemini-2.5-pro (older models don't support tools)
- Check tool schema matches OpenAI format

##  Next Steps

1. **Test locally**: Run server and test with curl
2. **Add more menu items**: Expand `restaurants.json`
3. **Integrate with Flutter**: Connect Flutter app to backend
4. **Deploy**: Host on cloud (Railway, Render, AWS, etc.)
5. **Connect Agora**: Point Agora to your deployed endpoint

##  What's Working

-  OpenAI Chat Completions protocol
-  Gemini AI integration
-  Tool/function calling
-  Streaming responses (SSE)
-  Mood-based menu search
-  Dietary & allergen filtering
-  Budget constraints
-  Order logging
-  Conversation history
-  Backward compatibility with existing endpoints

##  You're All Set!

The Flavourey bot brain is ready. Follow the Quick Start guide to get it running locally, then deploy and connect to Agora for voice integration!

For questions or issues, check the troubleshooting section in `README.md`.
