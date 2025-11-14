# Agora Chat Configuration Guide

## Overview

The Agora Chat configuration has been added to support both REST API and WebSocket connections for your Flavourey chatbot.

## Configuration Files

### 1. Environment Variables (`.env`)

Add these to your `.env` file:

```env
# Agora Chat Configuration
AGORA_CHAT_REST_API=a61.chat.agora.io
AGORA_CHAT_WEBSOCKET=mysync-api-61.chat.agora.io

# Agora Conversational AI (existing)
AGORA_APP_ID=your_app_id
AGORA_CUSTOMER_ID=your_customer_id
AGORA_CUSTOMER_SECRET=your_customer_secret
AGORA_APP_CERT=your_app_cert

# Gemini LLM
GEMINI_API_KEY=your_gemini_key
```

### 2. Configuration Module (`config.py`)

A centralized configuration module has been created with these classes:

#### `AgoraChatConfig`
Manages Agora Chat REST API and WebSocket endpoints.

**Usage:**
```python
from config import agora_chat

# Get REST API URL
rest_url = agora_chat.get_rest_api_url("/chat/messages")
# Returns: https://a61.chat.agora.io/chat/messages

# Get WebSocket URL
ws_url = agora_chat.get_websocket_url("/connect")
# Returns: wss://mysync-api-61.chat.agora.io/connect
```

#### `AgoraConversationalAIConfig`
Manages Agora Conversational AI credentials.

**Usage:**
```python
from config import agora_ai

app_id = agora_ai.APP_ID
customer_id = agora_ai.CUSTOMER_ID
api_base = agora_ai.API_BASE
```

#### `GeminiConfig`
Manages Gemini LLM configuration.

**Usage:**
```python
from config import gemini

api_key = gemini.API_KEY
model = gemini.DEFAULT_MODEL
base_url = gemini.BASE_URL
```

#### `AppConfig`
General application settings.

**Usage:**
```python
from config import app_config

port = app_config.PORT
host = app_config.HOST
logs_dir = app_config.LOGS_DIR
```

## Integration Examples

### Example 1: Send Message via Agora Chat REST API

```python
import httpx
from config import agora_chat, agora_ai

async def send_chat_message(user_id: str, message: str):
    url = agora_chat.get_rest_api_url("/chat/messages")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {agora_ai.APP_ID}"
    }
    
    payload = {
        "from": "bot",
        "to": user_id,
        "type": "text",
        "body": message
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        return response.json()
```

### Example 2: Connect to Agora Chat WebSocket

```python
import websockets
from config import agora_chat

async def connect_to_chat_websocket():
    ws_url = agora_chat.get_websocket_url()
    
    async with websockets.connect(ws_url) as websocket:
        # Send authentication
        await websocket.send(json.dumps({
            "type": "auth",
            "token": "your_auth_token"
        }))
        
        # Receive messages
        async for message in websocket:
            data = json.loads(message)
            print(f"Received: {data}")
```

### Example 3: Using in FastAPI Endpoints

```python
from fastapi import APIRouter
from config import agora_chat, agora_ai, gemini

router = APIRouter()

@router.get("/config/info")
async def get_config_info():
    """Get current configuration (for debugging)."""
    return {
        "agora_chat": {
            "rest_api": agora_chat.REST_API_BASE,
            "websocket": agora_chat.WEBSOCKET_BASE
        },
        "gemini": {
            "model": gemini.DEFAULT_MODEL,
            "base_url": gemini.BASE_URL
        },
        "agora_ai": {
            "api_base": agora_ai.API_BASE
        }
    }
```

## Updated main.py

The `main.py` file now automatically loads and logs these configurations on startup:

```
INFO: Gemini client initialized with base_url: https://generativelanguage.googleapis.com/v1beta/openai/
INFO: Agora Chat REST API: https://a61.chat.agora.io
INFO: Agora Chat WebSocket: wss://mysync-api-61.chat.agora.io
```

## Next Steps

To integrate Agora Chat with your bot:

1. **Set environment variables** in your `.env` file
2. **Import configuration** in your code: `from config import agora_chat`
3. **Use helper methods** to construct URLs:
   - `agora_chat.get_rest_api_url(path)` for REST API calls
   - `agora_chat.get_websocket_url(path)` for WebSocket connections

## Testing

Test the configuration:

```bash
# Start the server
python main.py

# Check logs for configuration output
# You should see the Agora Chat endpoints logged on startup
```

## Security Notes

- Never commit your `.env` file with real credentials
- Use `.env.example` as a template
- Keep `AGORA_CUSTOMER_SECRET` and `AGORA_APP_CERT` secure
- In production, use environment variables or secret management systems
