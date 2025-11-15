import os
import uvicorn
import json
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from .data_loader import FoodDataset
from .llm import get_default_llm, LocalLLMStub, run_chat_completion, stream_chat_completion
from .recommender import Recommender, search_menu_items
from .logging_store import ConversationStore
from .conversation import ConversationManager
from .agora_connector import AgoraConnector
from .token_helper import generate_rtc_token
from .agora_conversational_agent import start_conversational_agent, stop_conversational_agent
from .agent_session_store import save_agent, get_agent, remove_agent
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


env_paths =Path(__file__).parent.parent.parent / '.env',
for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path)
        logger.info(f"Loaded environment from {env_path}")
        break


DATA_CSV = os.environ.get('DATA_CSV', 'Indian-Food-Data.csv')
LOGS_DIR = os.environ.get('LOGS_DIR', 'logs')

app = FastAPI(title='Mood-based Food Recommender (text prototype)')

store = ConversationStore(LOGS_DIR)

try:
    dataset = FoodDataset.load_from_csv(DATA_CSV)
except Exception:
    dataset = FoodDataset(pd.DataFrame()) if 'pd' in globals() else None

recommender = Recommender(dataset) if dataset is not None else None
llm = get_default_llm()

# Conversation manager encapsulates mood detection and recommendation flow
manager = ConversationManager(store=store, recommender=recommender, llm=llm)

# Agora connector scaffold (used for voice integration). Initialize with env credentials
agora = AgoraConnector(
    app_id=os.environ.get('AGORA_APP_ID'),
    customer_id=os.environ.get('AGORA_CUSTOMER_ID'),
    customer_secret=os.environ.get('AGORA_CUSTOMER_SECRET'),
    base_url=os.environ.get('AGORA_API_BASE')
)


class AskRequest(BaseModel):
    session_id: str
    message: str


class AskResponse(BaseModel):
    reply: str
    mood: Optional[str] = None
    suggestions: Optional[List[dict]] = None


class StartAgentRequest(BaseModel):
    channel: str
    rtc_token: str
    agent_rtc_uid: Optional[str] = '0'
    llm_overrides: Optional[dict] = None


class AgentIdRequest(BaseModel):
    agent_id: str


class SpeakRequest(BaseModel):
    agent_id: str
    text: str
    priority: Optional[str] = 'INTERRUPT'
    interruptable: Optional[bool] = True


class DebugClassifyRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class DebugClassifyResponse(BaseModel):
    mood: Optional[str] = None
    confidence: Optional[float] = None
    raw: Optional[dict] = None


class StartConversationalAgentRequest(BaseModel):
    channelName: str
    rtcToken: str
    sessionKey: Optional[str] = None
    userContext: Optional[dict] = None


class StartConversationalAgentResponse(BaseModel):
    agentId: str
    status: str
    sessionKey: str


class StopConversationalAgentRequest(BaseModel):
    channelName: Optional[str] = None
    sessionKey: Optional[str] = None


class StopConversationalAgentResponse(BaseModel):
    ok: bool
    agentStopped: bool


# Tool executor for /chat/completions
async def execute_tool(tool_name: str, tool_args: Dict[str, Any]) -> Any:
    """Execute tool functions for LLM."""
    logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
    
    if tool_name == "search_menu":
        # Search menu items based on mood, budget, dietary restrictions
        try:
            result = await search_menu_items(
                mood=tool_args.get('mood'),
                max_budget=tool_args.get('max_budget'),
                dietary=tool_args.get('dietary', 'any'),
                allergens_to_avoid=tool_args.get('allergens_to_avoid', [])
            )
            return result
        except Exception as e:
            logger.error(f"Error executing search_menu: {e}")
            return {"error": str(e), "items": []}
    
    elif tool_name == "log_order":
        # Log order summary
        try:
            store.log_order(
                session_id=tool_args.get('session_id', 'unknown'),
                order_data=tool_args
            )
            return {"status": "logged", "order_id": tool_args.get('session_id')}
        except Exception as e:
            logger.error(f"Error logging order: {e}")
            return {"error": str(e)}
    
    else:
        return {"error": f"Unknown tool: {tool_name}"}


@app.post('/chat/completions')
async def chat_completions(request: Request):
    """
    OpenAI Chat Completions-compatible endpoint for Agora Conversational AI.
    
    Supports:
    - Non-streaming responses (stream: false)
    - Streaming responses (stream: true) as Server-Sent Events
    - Tool/function calling
    - System prompt injection
    
    Request body matches OpenAI Chat Completions API format.
    """
    try:
        body = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
    
    # Validate required fields
    if 'messages' not in body:
        raise HTTPException(status_code=400, detail="'messages' field is required")
    
    stream = body.get('stream', False)
    
    try:
        if stream:
            # Return streaming response as SSE
            return StreamingResponse(
                stream_chat_completion(body, tool_executor=execute_tool),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no"
                }
            )
        else:
            # Return non-streaming JSON response
            response = await run_chat_completion(body, tool_executor=execute_tool)
            return JSONResponse(content=response)
    
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise HTTPException(status_code=500, detail=f"Server configuration error: {str(e)}")
    except Exception as e:
        logger.error(f"Chat completion error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/')
async def root():
    """Health check and API info."""
    return {
        "service": "Flavourey Bot Backend",
        "status": "running",
        "endpoints": {
            "chat_completions": "/chat/completions (OpenAI-compatible)",
            "text_chat": "/api/ask",
            "debug": "/api/debug/classify",
            "agora": "/api/agent/*",
            "token": "/api/token/generate"
        },
        "docs": "/docs"
    }


@app.post('/api/ask', response_model=AskResponse)
async def ask(req: AskRequest):
    sid = req.session_id
    msg = req.message.strip()
    if not sid or not msg:
        raise HTTPException(status_code=400, detail='session_id and message required')

    # Delegate conversation handling to ConversationManager
    result = await manager.process_user_message(sid, msg)
    return AskResponse(reply=result.get('reply', ''), mood=result.get('mood'), suggestions=result.get('suggestions'))


@app.post('/api/debug/classify', response_model=DebugClassifyResponse)
async def debug_classify(req: DebugClassifyRequest):
    """Quick debug endpoint to classify mood using the configured LLM.

    Returns parsed `mood`, `confidence`, and the raw response returned by the LLM client.
    If `session_id` is provided the user message will be appended to the conversation store
    for traceability.
    """
    msg = req.message.strip() if req.message else ''
    if not msg:
        raise HTTPException(status_code=400, detail='message is required')
    try:
        # append to conversation store if session_id provided
        if req.session_id:
            try:
                store.append(req.session_id, 'user', msg)
            except Exception:
                # non-fatal: continue even if logging fails
                pass

        # call the configured LLM (could be GeminiClient or LocalLLMStub)
        res = await llm.classify_mood(msg)

        # If logging enabled, record the assistant's classification
        if req.session_id:
            try:
                assistant_text = f"[classification] {res.get('mood')} (confidence={res.get('confidence')})"
                store.append(req.session_id, 'assistant', assistant_text)
            except Exception:
                pass

        return DebugClassifyResponse(mood=res.get('mood'), confidence=res.get('confidence'), raw=res.get('raw'))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/api/agent/start')
async def start_agent(req: StartAgentRequest):
    if not req.channel or not req.rtc_token:
        raise HTTPException(status_code=400, detail='channel and rtc_token are required')
    try:
        # Build a basic LLM config if not provided. Prefer environment Gemini key/model.
        if req.llm_overrides:
            llm_cfg = req.llm_overrides
        else:
            gemini_key = os.environ.get('GEMINI_API_KEY')
            gemini_model = os.environ.get('GEMINI_MODEL') or os.environ.get('DEFAULT_MODEL') or 'gemini-1.0'
            # Minimal LLM config for Agora Conversational AI. This shape may be extended
            # according to Agora's LLM adapter schema. It includes provider hint and
            # the model/key so the conversational agent can call the LLM (when Agora is
            # configured to use an external LLM via the REST bridge).
            llm_cfg = {
                'provider': 'external',
                'type': 'gemini',
                'model': gemini_model,
                # Agora may require the server to host the LLM key; sending API keys to
                # third-party services has security implications. If you prefer, leave
                # 'api_key' empty and configure Agora Console to use the key.
                'api_key': gemini_key,
                'system_prompt': 'You are a helpful assistant that classifies user mood and answers conversationally. Only provide recommendations when explicitly asked.'
            }

        res = await agora.join(channel=req.channel, rtc_token=req.rtc_token, agent_rtc_uid=req.agent_rtc_uid, llm_config=llm_cfg)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/api/agent/leave')
async def leave_agent(req: AgentIdRequest):
    if not req.agent_id:
        raise HTTPException(status_code=400, detail='agent_id required')
    try:
        res = await agora.leave(req.agent_id)
        return {'ok': True, 'result': res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/api/agent/speak')
async def agent_speak(req: SpeakRequest):
    try:
        res = await agora.speak(req.agent_id, req.text, priority=req.priority, interruptable=req.interruptable)
        return {'ok': True, 'result': res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/api/agent/interrupt')
async def agent_interrupt(req: AgentIdRequest):
    try:
        res = await agora.interrupt(req.agent_id)
        return {'ok': True, 'result': res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/api/agent/{agent_id}/history')
async def agent_history(agent_id: str):
    try:
        res = await agora.history(agent_id)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/api/agents')
async def list_agents(channel: Optional[str] = None, state: Optional[int] = None, limit: int = 20):
    try:
        res = await agora.list_agents(channel=channel, state=state, limit=limit)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/api/ai/agent/start', response_model=StartConversationalAgentResponse)
async def start_ai_agent(req: StartConversationalAgentRequest):
    """
    Start an Agora Conversational AI agent in the specified channel.
    
    This creates a voice AI agent that joins the RTC channel and can
    have real-time conversations with users.
    """
    if not req.channelName or not req.rtcToken:
        raise HTTPException(
            status_code=400,
            detail='channelName and rtcToken are required'
        )
    
    session_key = req.sessionKey or req.channelName
    
    try:
        logger.info(f"Starting Conversational AI agent for session: {session_key}")
        
        result = await start_conversational_agent(
            channel_name=req.channelName,
            rtc_token=req.rtcToken,
            user_context=req.userContext,
        )
        
        save_agent(session_key, result["agent_id"])
        
        return StartConversationalAgentResponse(
            agentId=result["agent_id"],
            status=result["status"],
            sessionKey=session_key,
        )
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise HTTPException(status_code=500, detail=f"Configuration error: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to start agent: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/api/ai/agent/stop', response_model=StopConversationalAgentResponse)
async def stop_ai_agent(req: StopConversationalAgentRequest):
    """
    Stop an Agora Conversational AI agent.
    
    This terminates the AI agent and removes it from the RTC channel.
    """
    if not req.sessionKey and not req.channelName:
        raise HTTPException(
            status_code=400,
            detail='Either sessionKey or channelName is required'
        )
    
    session_key = req.sessionKey or req.channelName
    
    try:
        agent_id = get_agent(session_key)
        
        if not agent_id:
            logger.warning(f"No agent found for session: {session_key}")
            return StopConversationalAgentResponse(
                ok=True,
                agentStopped=False,
            )
        
        logger.info(f"Stopping agent {agent_id} for session: {session_key}")
        
        success = await stop_conversational_agent(agent_id)
        
        if success:
            remove_agent(session_key)
        
        return StopConversationalAgentResponse(
            ok=True,
            agentStopped=success,
        )
        
    except Exception as e:
        logger.error(f"Failed to stop agent: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/api/token/generate')
async def generate_token(channel: str, uid: Optional[int] = 0, expire_seconds: Optional[int] = 3600):
    """Generate an RTC token using AGORA_APP_ID and AGORA_APP_CERT from environment.

    Note: This endpoint should be secured in production. It uses App Certificate
    present in the server environment to mint tokens for clients.
    """
    app_id = os.environ.get('AGORA_APP_ID')
    app_cert = os.environ.get('AGORA_APP_CERT')
    if not app_id or not app_cert:
        raise HTTPException(status_code=400, detail='AGORA_APP_ID and AGORA_APP_CERT must be set in environment')
    try:
        token = generate_rtc_token(app_id, app_cert, channel, uid=uid, expire_seconds=expire_seconds)
        return {'token': token, 'app_id': app_id, 'channel': channel, 'uid': uid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == '__main__':
    # quick run for local dev
    port = int(os.environ.get('PORT', 8000))
    uvicorn.run('src.server:app', host='0.0.0.0', port=port, reload=True)
