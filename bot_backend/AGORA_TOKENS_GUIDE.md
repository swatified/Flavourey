# Agora RTC Tokens Configuration Guide

## Overview

Your Agora RTC tokens have been configured and are ready to use. These tokens authenticate your bot to join Agora RTC channels for voice/video communication.

## Token Types

### 1. **Integer UID Token**
```
AGORA_RTC_TOKEN_INT_UID=00655a8e56af4034120a94c33987000ffed...
```
Use this when your agent uses an integer user ID (e.g., `123456`)

### 2. **User Account Token**
```
AGORA_RTC_TOKEN_USER_ACCOUNT=00655a8e56af4034120a94c33987000ffed...
```
Use this when your agent uses a string user account (e.g., `"bot_agent"`)

## Configuration Files Updated

✅ `.env` - Your tokens are now stored securely  
✅ `config.py` - Added `RTC_TOKEN_INT_UID` and `RTC_TOKEN_USER_ACCOUNT` to `AgoraConversationalAIConfig`  
✅ `agora_helper.py` - Helper functions to use these tokens  
✅ `.env.example` - Updated template for other developers  

## Usage Examples

### Example 1: Get RTC Token in Your Code

```python
from config import agora_ai

# Get integer UID token (default)
rtc_token = agora_ai.RTC_TOKEN_INT_UID

# Or get user account token
rtc_token = agora_ai.RTC_TOKEN_USER_ACCOUNT
```

### Example 2: Using the Helper

```python
from agora_helper import rtc_helper

# Get token (integer UID by default)
token = rtc_helper.get_rtc_token(use_int_uid=True)

# Get user account token
token = rtc_helper.get_rtc_token(use_int_uid=False)
```

### Example 3: Start Agora Voice Agent

```python
from agora_helper import integration_helper
import httpx

async def start_voice_agent(channel_name: str):
    """Start Agora Conversational AI voice agent."""
    
    # Build agent configuration
    payload = integration_helper.create_start_agent_payload(
        channel_name=channel_name,
        agent_uid="123456"  # Your bot's UID
    )
    
    # Call Agora API
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{agora_ai.API_BASE}/start",
            json=payload,
            headers={
                "X-Agora-Customer-Id": agora_ai.CUSTOMER_ID,
                "X-Agora-Customer-Secret": agora_ai.CUSTOMER_SECRET
            }
        )
        return response.json()
```

### Example 4: Update Existing Server Endpoint

Update your existing `/start_agent` endpoint in `src/server.py`:

```python
from config import agora_ai

@app.post('/start_agent')
async def start_agent(request: StartAgentRequest):
    """Start Agora voice agent with configured token."""
    
    # Use configured token if not provided
    rtc_token = request.rtc_token or agora_ai.RTC_TOKEN_INT_UID
    
    payload = {
        "channel": request.channel,
        "rtc_token": rtc_token,
        "agent_rtc_uid": request.agent_rtc_uid or '0',
        "llm": {
            "type": "custom",
            "url": f"http://your-server.com/chat/completions",
            "model": "gemini-2.5-pro"
        }
    }
    
    # Rest of your existing code...
```

## Important Notes

### ⚠️ Token Expiration

These tokens **expire after 24 hours** (or based on how you generated them). For production:

1. **Generate tokens dynamically** using your existing `src/token_helper.py`:
   ```python
   from src.token_helper import build_token
   from config import agora_ai
   import time
   
   # Generate fresh token (expires in 24 hours)
   token = build_token(
       channel_name="my_channel",
       uid=123456,
       app_id=agora_ai.APP_ID,
       app_certificate=agora_ai.APP_CERT,
       expired_ts=int(time.time()) + 86400
   )
   ```

2. **Refresh tokens before expiry** - Implement token refresh logic

3. **Use the helper function**:
   ```python
   from agora_helper import rtc_helper
   
   token = rtc_helper.build_rtc_token(
       channel_name="my_channel",
       uid=123456,
       privilege_expired_ts=0  # 0 = 24h from now
   )
   ```

### 🔒 Security Best Practices

1. **Never commit `.env` file** - It's in `.gitignore`
2. **Rotate tokens regularly** in production
3. **Generate tokens server-side** - Never expose App Certificate to clients
4. **Use environment variables** in deployment platforms (Heroku, AWS, etc.)

## Testing Your Configuration

### Test 1: Verify Token Format

```python
from config import agora_ai
from agora_helper import rtc_helper

# Check if tokens are loaded
print(f"Int UID Token: {agora_ai.RTC_TOKEN_INT_UID[:50]}...")
print(f"User Token: {agora_ai.RTC_TOKEN_USER_ACCOUNT[:50]}...")

# Validate token format
is_valid = rtc_helper.validate_token_expiry(agora_ai.RTC_TOKEN_INT_UID)
print(f"Token valid: {is_valid}")
```

### Test 2: Get Full Agent Config

```python
from agora_helper import integration_helper

config = integration_helper.get_agent_config(
    channel_name="test_channel",
    agent_uid=123456
)

print(config)
# Output:
# {
#   "channel_name": "test_channel",
#   "uid": 123456,
#   "rtc_token": "00655a8e56af...",
#   "app_id": "55a8e56af...",
#   "chat": {
#     "rest_api": "https://a61.chat.agora.io",
#     "websocket": "wss://mysync-api-61.chat.agora.io"
#   }
# }
```

## Integration Checklist

- [x] Tokens stored in `.env`
- [x] Config module updated with token accessors
- [x] Helper functions created in `agora_helper.py`
- [ ] Update `src/server.py` to use configured tokens
- [ ] Test voice agent startup with new tokens
- [ ] Implement dynamic token generation for production
- [ ] Set up token refresh mechanism
- [ ] Test end-to-end voice conversation

## Next Steps

1. **Test the tokens** by starting a voice agent
2. **Implement dynamic token generation** using `build_rtc_token()`
3. **Update your frontend** to request tokens from your backend
4. **Set up monitoring** for token expiration

## Troubleshooting

### Token not working?

1. Check token hasn't expired (24h default)
2. Verify App ID matches token prefix
3. Regenerate token using Agora Console
4. Use dynamic generation instead of static tokens

### Agent not joining channel?

1. Verify channel name matches
2. Check UID is correct (integer vs string)
3. Ensure App Certificate is correct
4. Check Agora Console for error logs

## Reference

- Agora Token Generator: https://webdemo.agora.io/token-builder/
- Your App ID: `55a8e56af4034120a94c33987000ffed`
- Token documentation: https://docs.agora.io/en/voice-calling/develop/authentication-workflow
