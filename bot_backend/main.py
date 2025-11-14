"""
FastAPI service for Agora Conversational AI Engine Custom LLM integration.
Proxies requests to Google Gemini 2.5 Pro via OpenAI-compatible API.
"""

import os
import json
import asyncio
import logging
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from openai import AsyncOpenAI
from dotenv import load_dotenv

from config import gemini, agora_chat, agora_ai

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


class Message(BaseModel):
    role: str
    content: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    modalities: Optional[List[str]] = Field(default_factory=lambda: ["text"])
    tools: Optional[List[Dict[str, Any]]] = None
    tool_choice: Optional[Any] = None
    response_format: Optional[Dict[str, Any]] = None
    audio: Optional[Dict[str, Any]] = None
    stream: bool = False
    stream_options: Optional[Dict[str, Any]] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None


gemini_client: Optional[AsyncOpenAI] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global gemini_client
    
    if not gemini.API_KEY:
        logger.error("GEMINI_API_KEY not set in environment")
        raise RuntimeError("GEMINI_API_KEY environment variable is required")
    
    gemini_client = AsyncOpenAI(api_key=gemini.API_KEY, base_url=gemini.BASE_URL)
    
    logger.info(f"Gemini client initialized with base_url: {gemini.BASE_URL}")
    logger.info(f"Agora Chat REST API: {agora_chat.get_rest_api_url()}")
    logger.info(f"Agora Chat WebSocket: {agora_chat.get_websocket_url()}")
    
    yield
    
    await gemini_client.close()
    logger.info("Gemini client closed")


app = FastAPI(
    title="Agora Custom LLM - Gemini Proxy",
    description="OpenAI Chat Completions-compatible endpoint for Agora using Gemini 2.5 Pro",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """
    OpenAI Chat Completions endpoint for Agora Conversational AI Engine.
    
    Streams responses from Gemini 2.5 Pro via Server-Sent Events (SSE).
    Compatible with Agora Custom LLM integration requirements.
    """
    
    if not request.stream:
        raise HTTPException(
            status_code=400,
            detail="chat completions require streaming"
        )
    
    if not gemini_client:
        raise HTTPException(
            status_code=503,
            detail="Gemini client not initialized"
        )
    
    async def generate_sse_stream():
        try:
            params = {
                "model": request.model,
                "messages": [msg.model_dump(exclude_none=True) for msg in request.messages],
                "stream": True,
            }
            
            # Gemini OpenAI-compatible API supported parameters
            if request.tools:
                params["tools"] = request.tools
                if request.tool_choice:
                    params["tool_choice"] = request.tool_choice
            
            if request.temperature is not None:
                params["temperature"] = request.temperature
            
            if request.max_tokens is not None:
                params["max_tokens"] = request.max_tokens
            
            if request.top_p is not None:
                params["top_p"] = request.top_p
            
            # Note: Gemini OpenAI API does not support:
            # - modalities (always text)
            # - audio
            # - response_format
            # - stream_options
            # - frequency_penalty
            # - presence_penalty
            # These are accepted by the endpoint but ignored for Agora compatibility
            
            logger.info(f"Creating streaming completion with model: {request.model}")
            
            stream = await gemini_client.chat.completions.create(**params)
            
            async for chunk in stream:
                chunk_dict = chunk.model_dump()
                yield f"data: {json.dumps(chunk_dict)}\n\n"
            
            yield "data: [DONE]\n\n"
            
        except asyncio.CancelledError:
            logger.info("Client disconnected during streaming")
            raise
        
        except Exception as e:
            logger.error(f"Error during streaming: {e}", exc_info=True)
            
            error_data = {
                "error": {
                    "message": str(e),
                    "type": "server_error"
                }
            }
            yield f"data: {json.dumps(error_data)}\n\n"
            yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate_sse_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


if __name__ == "__main__":
    import uvicorn
    from config import app_config
    
    uvicorn.run(
        "main:app",
        host=app_config.HOST,
        port=app_config.PORT,
        reload=True,
        log_level="info"
    )
