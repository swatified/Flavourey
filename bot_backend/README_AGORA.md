# Agora Custom LLM - Gemini Proxy

Production-ready FastAPI service that exposes Google Gemini 2.5 Pro as an OpenAI Chat Completions-compatible endpoint for Agora Conversational AI Engine.

## Architecture

```
Agora Conversational AI Engine
         ↓
   Custom LLM URL: /chat/completions
         ↓
   FastAPI Service (main.py)
         ↓
   OpenAI-compatible Client
         ↓
   Google Gemini 2.5 Pro API
```

## Features

- OpenAI Chat Completions protocol compatibility
- Server-Sent Events (SSE) streaming required by Agora
- Tool/function calling support
- Full parameter pass-through (temperature, max_tokens, etc.)
- Graceful error handling during streaming
- Health check endpoint
- Environment-based configuration

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements-minimal.txt
```

### 2. Set Environment Variables

Create a `.env` file:

```env
GEMINI_API_KEY=your_gemini_api_key_here
PORT=8000
```

Get your Gemini API key from: https://aistudio.google.com/app/apikey

### 3. Run the Service

```bash
python main.py
```

Or with uvicorn directly:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Test the Service

```bash
python test_agora_compat.py
```

## API Endpoints

### GET /health

Health check endpoint.

**Response:**
```json
{"status": "ok"}
```

### POST /chat/completions

OpenAI Chat Completions-compatible endpoint with streaming.

**Request Format:**

```json
{
  "model": "gemini-2.5-pro",
  "messages": [
    {"role": "user", "content": "Hello"}
  ],
  "modalities": ["text"],
  "stream": true,
  "temperature": 0.7,
  "max_tokens": 1000,
  "tools": [...],
  "tool_choice": "auto"
}
```

**Required Fields:**
- `model`: Model identifier (e.g., "gemini-2.5-pro")
- `messages`: Array of message objects with `role` and `content`
- `stream`: Must be `true` (Agora requirement)

**Optional Fields:**
- `modalities`: Array of strings, default `["text"]`
- `tools`: Array of tool/function definitions
- `tool_choice`: Tool selection strategy
- `temperature`: Sampling temperature (0.0-2.0)
- `max_tokens`: Maximum tokens in response
- `audio`: Audio configuration (pass-through)
- `response_format`: Response formatting options
- `stream_options`: Streaming configuration

**Response Format (SSE):**

```
data: {"id":"..","object":"chat.completion.chunk","created":...,"model":"...","choices":[{"index":0,"delta":{"content":"Hello"},"finish_reason":null}]}

data: {"id":"..","object":"chat.completion.chunk","created":...,"model":"...","choices":[{"index":0,"delta":{},"finish_reason":"stop"}]}

data: [DONE]
```

**Error Response:**

- **400 Bad Request**: If `stream` is not `true`
  ```json
  {"detail": "chat completions require streaming"}
  ```

- **503 Service Unavailable**: If Gemini client not initialized

## Agora Integration

Configure Agora Conversational AI Engine to use this service as a Custom LLM:

```yaml
llm:
  type: custom
  url: https://your-domain.com/chat/completions
  model: gemini-2.5-pro
```

The service strictly follows OpenAI Chat Completions streaming format, ensuring compatibility with Agora's expectations:

1. Each chunk is sent as `data: <JSON>\n\n`
2. Stream ends with `data: [DONE]\n\n`
3. Chunks follow OpenAI's delta format
4. Tool calls are properly formatted if tools are provided

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEY` | Yes | - | Google Gemini API key |
| `PORT` | No | 8000 | Server port |

### Gemini API Configuration

The service uses the OpenAI-compatible Gemini endpoint:

```
https://generativelanguage.googleapis.com/v1beta/openai/
```

This endpoint supports:
- Chat Completions with streaming
- Tool/function calling
- OpenAI SDK compatibility

Reference: https://ai.google.dev/gemini-api/docs/openai

## Production Deployment

### Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements-minimal.txt .
RUN pip install --no-cache-dir -r requirements-minimal.txt

COPY main.py .

ENV PORT=8000
EXPOSE 8000

CMD ["python", "main.py"]
```

Build and run:

```bash
docker build -t agora-gemini-proxy .
docker run -p 8000:8000 -e GEMINI_API_KEY=your_key agora-gemini-proxy
```

### Cloud Deployment

The service can be deployed to:
- AWS ECS/Fargate
- Google Cloud Run
- Azure Container Apps
- Heroku
- Railway
- Render

Key requirements:
- Set `GEMINI_API_KEY` environment variable
- Ensure port 8000 is exposed
- Use HTTPS in production

## Testing

### Manual Testing

```bash
curl -X POST http://localhost:8000/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-2.5-pro",
    "messages": [{"role": "user", "content": "Hello"}],
    "stream": true
  }'
```

### Automated Testing

```bash
python test_agora_compat.py
```

Tests include:
- Health check validation
- Non-streaming rejection (400 error)
- Basic streaming with text modality
- Streaming with tool calling
- Complete Agora-style request flow

## Error Handling

The service handles errors gracefully:

1. **Pre-streaming errors**: Return HTTP error with JSON body
2. **During-streaming errors**: Send error in SSE format, then `[DONE]`
3. **Client disconnects**: Log and cleanup, no stack trace spam
4. **Invalid requests**: HTTP 400 with details

## Performance Considerations

- Uses `AsyncOpenAI` for non-blocking I/O
- Streams responses immediately (no buffering)
- Lifespan context manager for client lifecycle
- Minimal memory footprint
- Handles concurrent requests efficiently

## Monitoring

Key metrics to monitor:
- Response time per request
- Stream chunk latency
- Error rate (5xx responses)
- Client disconnect rate
- Gemini API errors

## Limitations

- Requires `stream: true` in requests (Agora requirement)
- Depends on Gemini API availability and rate limits
- No request queuing or retry logic (add if needed)

## Support

For issues or questions:
1. Check Gemini API status
2. Verify `GEMINI_API_KEY` is valid
3. Review server logs for errors
4. Test with `test_agora_compat.py`

## License

See LICENSE file in repository root.
