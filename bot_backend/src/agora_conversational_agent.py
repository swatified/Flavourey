"""
Agora Conversational AI agent service for managing voice AI agents.
"""

import base64
import httpx
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from ..config import agora_ai, llm_config, tts_config

logger = logging.getLogger(__name__)


def build_agora_headers() -> Dict[str, str]:
    """
    Build HTTP headers for Agora REST calls using Basic auth with
    AGORA_CUSTOMER_ID and AGORA_CUSTOMER_SECRET.
    """
    if not agora_ai.CUSTOMER_ID or not agora_ai.CUSTOMER_SECRET:
        raise ValueError("AGORA_CUSTOMER_ID and AGORA_CUSTOMER_SECRET must be set")
    
    credentials = f"{agora_ai.CUSTOMER_ID}:{agora_ai.CUSTOMER_SECRET}"
    encoded = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
    
    return {
        "Authorization": f"Basic {encoded}",
        "Content-Type": "application/json",
    }


async def start_conversational_agent(
    channel_name: str,
    rtc_token: str,
    user_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Start an Agora Conversational AI agent in the specified channel.
    
    Args:
        channel_name: The RTC channel name
        rtc_token: The RTC token for the agent
        user_context: Optional user context with mood, allergies, etc.
        
    Returns:
        Dict with agent_id, status, create_ts
        
    Raises:
        httpx.HTTPError: If the API request fails
        ValueError: If required config is missing
    """
    if not agora_ai.APP_ID:
        raise ValueError("AGORA_APP_ID must be set")
    
    url = f"{agora_ai.CONV_AI_BASE_URL}/projects/{agora_ai.APP_ID}/join"
    headers = build_agora_headers()
    
    system_message_content = (
        "You are Flavourey, a mood-based food assistant. "
        "You talk to exactly one user at a time over voice. "
        "Ask friendly questions about their mood, cravings, context, "
        "budget, preferred cuisine, and allergies. "
        "NEVER suggest dishes containing ingredients in their allergy list. "
        "Prefer concrete dishes and options over generic advice. "
        "Keep responses concise and conversational."
    )
    
    if user_context:
        if user_context.get("mood"):
            system_message_content += f"\n\nUser's current mood: {user_context['mood']}."
        
        if user_context.get("allergies"):
            allergies = ", ".join(user_context["allergies"])
            system_message_content += (
                f"\n\nCRITICAL: User has allergies to: {allergies}. "
                f"NEVER suggest dishes with these ingredients."
            )
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    agent_name = f"flavourey-agent-{channel_name}-{timestamp}"
    
    body = {
        "name": agent_name,
        "properties": {
            "channel": channel_name,
            "token": rtc_token,
            "agent_rtc_uid": "0",
            "remote_rtc_uids": ["*"],
            "enable_string_uid": False,
            "idle_timeout": agora_ai.AGENT_IDLE_TIMEOUT,
            "llm": {
                "url": llm_config.API_URL,
                "api_key": llm_config.API_KEY,
                "system_messages": [
                    {
                        "role": "system",
                        "content": system_message_content,
                    }
                ],
                "greeting_message": (
                    "Hey, I'm Flavourey. Tell me how you're feeling "
                    "and what you feel like eating."
                ),
                "failure_message": (
                    "Sorry, I'm having trouble with that. "
                    "Try asking about food, mood, or cravings."
                ),
                "max_history": 10,
                "params": {
                    "model": llm_config.MODEL,
                },
            },
            "asr": {
                "language": "en-US",
            },
            "tts": {
                "vendor": "microsoft",
                "params": {
                    "key": tts_config.API_KEY,
                    "region": tts_config.REGION,
                    "voice_name": tts_config.VOICE_NAME,
                },
            },
        },
    }
    
    logger.info(f"Starting Conversational AI agent for channel: {channel_name}")
    logger.debug(f"Request body: {body}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, headers=headers, json=body)
        response.raise_for_status()
        
        result = response.json()
        logger.info(
            f"Agent started successfully: {result.get('agent_id')} "
            f"(status: {result.get('status')})"
        )
        
        return {
            "agent_id": result["agent_id"],
            "status": result["status"],
            "create_ts": result.get("create_ts", 0),
        }


async def stop_conversational_agent(agent_id: str) -> bool:
    """
    Stop an Agora Conversational AI agent.
    
    Args:
        agent_id: The agent ID to stop
        
    Returns:
        True if stopped successfully, False otherwise
    """
    if not agora_ai.APP_ID:
        raise ValueError("AGORA_APP_ID must be set")
    
    url = f"{agora_ai.CONV_AI_BASE_URL}/projects/{agora_ai.APP_ID}/agents/{agent_id}/leave"
    headers = build_agora_headers()
    
    logger.info(f"Stopping Conversational AI agent: {agent_id}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers)
            response.raise_for_status()
            
            logger.info(f"Agent stopped successfully: {agent_id}")
            return True
            
    except httpx.HTTPError as e:
        logger.error(f"Failed to stop agent {agent_id}: {e}")
        return False
