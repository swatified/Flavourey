"""
LLM integration for Flavourey using Gemini's OpenAI-compatible API.
Provides Chat Completions protocol with tool calling support.
"""

import os
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional, AsyncIterator
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

# Flavourey system prompt
FLAVOUREY_SYSTEM_PROMPT = """You are Flavourey, a friendly mood-based food ordering assistant.

Your capabilities:
- Understand user mood and emotional state
- Recommend food matching mood, dietary restrictions, and budget
- Handle allergies (veg/non-veg/vegan)
- Search menus and provide personalized suggestions
- Help users place orders

Guidelines:
1. Be empathetic and match user's emotional tone
2. Ask about allergies and dietary restrictions
3. Respect budget constraints
4. When user wants to order, create an ORDER_SUMMARY with restaurant, items, quantities, mood, allergies, total
5. Use available tools to search menus
6. Be concise but friendly

ORDER_SUMMARY format:
```
ORDER_SUMMARY:
Restaurant: [Name]
Items: [Quantity]x [Item] - ₹[Price]
Special Instructions: [Any]
Mood: [Inferred]
Allergies Respected: [List or None]
Total: ₹[Amount]
```
"""


class GeminiOpenAIClient:
    """Gemini client using OpenAI-compatible Chat Completions API."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.environ.get('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY required")
        
        self.model = model or os.environ.get('GEMINI_MODEL', 'gemini-2.5-pro')
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
        
        self.client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
    
    async def chat_completion(self, messages: List[Dict], model: Optional[str] = None,
                             tools: Optional[List[Dict]] = None, tool_choice: Optional[Any] = None,
                             stream: bool = False, temperature: float = 0.7,
                             max_tokens: Optional[int] = None, **kwargs) -> Any:
        """Create chat completion."""
        params = {
            "model": model or self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream,
        }
        if max_tokens:
            params["max_tokens"] = max_tokens
        if tools:
            params["tools"] = tools
        if tool_choice:
            params["tool_choice"] = tool_choice
        params.update(kwargs)
        
        try:
            return await self.client.chat.completions.create(**params)
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise


def inject_system_prompt(messages: List[Dict]) -> List[Dict]:
    """Inject Flavourey system prompt if not present."""
    has_system = any(msg.get('role') == 'system' for msg in messages)
    if not has_system:
        return [{"role": "system", "content": FLAVOUREY_SYSTEM_PROMPT}, *messages]
    return messages


async def run_chat_completion(request_body: Dict, tool_executor: Optional[callable] = None) -> Dict:
    """Run chat completion with tool calling loop."""
    client = GeminiOpenAIClient()
    
    messages = inject_system_prompt(request_body.get('messages', []))
    model = request_body.get('model')
    tools = request_body.get('tools')
    tool_choice = request_body.get('tool_choice')
    stream = request_body.get('stream', False)
    temperature = request_body.get('temperature', 0.7)
    max_tokens = request_body.get('max_tokens')
    
    max_iterations = 5
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        
        response = await client.chat_completion(
            messages=messages, model=model, tools=tools, tool_choice=tool_choice,
            stream=stream, temperature=temperature, max_tokens=max_tokens
        )
        
        if stream:
            return response
        
        choice = response.choices[0]
        message = choice.message
        
        if not message.tool_calls or not tool_executor:
            return response.model_dump()
        
        messages.append(message.model_dump())
        
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            tool_args_str = tool_call.function.arguments
            
            try:
                tool_args = json.loads(tool_args_str) if isinstance(tool_args_str, str) else tool_args_str
            except json.JSONDecodeError:
                tool_args = {}
            
            logger.info(f"Executing tool: {tool_name} with {tool_args}")
            
            try:
                tool_result = await tool_executor(tool_name, tool_args)
                tool_result_str = json.dumps(tool_result) if not isinstance(tool_result, str) else tool_result
            except Exception as e:
                logger.error(f"Tool execution error: {e}")
                tool_result_str = json.dumps({"error": str(e)})
            
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": tool_result_str
            })
        
        tool_choice = None
    
    logger.warning(f"Hit max tool calling iterations ({max_iterations})")
    return response.model_dump()


async def stream_chat_completion(request_body: Dict, tool_executor: Optional[callable] = None) -> AsyncIterator[str]:
    """Stream chat completion as SSE."""
    tools = request_body.get('tools')
    
    if tools and tool_executor:
        modified_body = {**request_body, 'stream': False}
        final_response = await run_chat_completion(modified_body, tool_executor)
        
        choice = final_response['choices'][0]
        content = choice['message'].get('content', '')
        chunk_size = 20
        
        for i in range(0, len(content), chunk_size):
            chunk_content = content[i:i+chunk_size]
            chunk = {
                "id": final_response['id'],
                "object": "chat.completion.chunk",
                "created": final_response['created'],
                "model": final_response['model'],
                "choices": [{
                    "index": 0,
                    "delta": {"content": chunk_content},
                    "finish_reason": None
                }]
            }
            yield f"data: {json.dumps(chunk)}\n\n"
            await asyncio.sleep(0.01)
        
        final_chunk = {
            "id": final_response['id'],
            "object": "chat.completion.chunk",
            "created": final_response['created'],
            "model": final_response['model'],
            "choices": [{
                "index": 0,
                "delta": {},
                "finish_reason": choice.get('finish_reason', 'stop')
            }]
        }
        yield f"data: {json.dumps(final_chunk)}\n\n"
        yield "data: [DONE]\n\n"
    
    else:
        client = GeminiOpenAIClient()
        messages = inject_system_prompt(request_body.get('messages', []))
        
        stream_response = await client.chat_completion(
            messages=messages, model=request_body.get('model'), stream=True,
            temperature=request_body.get('temperature', 0.7), max_tokens=request_body.get('max_tokens')
        )
        
        async for chunk in stream_response:
            yield f"data: {json.dumps(chunk.model_dump())}\n\n"
        
        yield "data: [DONE]\n\n"


# Backward compatibility
class LocalLLMStub:
    MOOD_KEYWORDS = {
        'happy': ['happy', 'good', 'great', 'fantastic', 'joy', 'awesome', 'excited'],
        'sad': ['sad', 'down', 'unhappy', 'depressed', 'low', 'blue'],
        'angry': ['angry', 'mad', 'annoyed', 'frustrated', 'upset'],
        'energetic': ['energetic', 'active', 'hyped', 'pumped'],
        'romantic': ['romantic', 'date', 'love', 'cozy'],
        'stressed': ['stressed', 'anxious', 'overwhelmed'],
        'relaxed': ['relaxed', 'calm', 'chill']
    }
    
    async def classify_mood(self, text: str) -> Dict:
        t = text.lower()
        for mood, keywords in self.MOOD_KEYWORDS.items():
            for kw in keywords:
                if kw in t:
                    return {'mood': mood, 'confidence': 0.8, 'raw': None}
        return {'mood': 'neutral', 'confidence': 0.5, 'raw': None}


def get_default_llm():
    try:
        return GeminiOpenAIClient()
    except ValueError:
        logger.warning("GEMINI_API_KEY not set, using LocalLLMStub")
        return LocalLLMStub()
