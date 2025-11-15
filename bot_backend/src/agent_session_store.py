"""
In-memory store for mapping session keys to Agora agent IDs.
"""

from typing import Optional
import logging

logger = logging.getLogger(__name__)

_SESSION_TO_AGENT: dict[str, str] = {}


def save_agent(session_key: str, agent_id: str) -> None:
    """
    Save an agent ID for a given session key.
    
    Args:
        session_key: The session identifier (from client or channel name)
        agent_id: The Agora agent ID
    """
    _SESSION_TO_AGENT[session_key] = agent_id
    logger.info(f"Saved agent mapping: {session_key} -> {agent_id}")


def get_agent(session_key: str) -> Optional[str]:
    """
    Get the agent ID for a given session key.
    
    Args:
        session_key: The session identifier
        
    Returns:
        The agent ID if found, None otherwise
    """
    agent_id = _SESSION_TO_AGENT.get(session_key)
    if agent_id:
        logger.debug(f"Found agent for session {session_key}: {agent_id}")
    else:
        logger.debug(f"No agent found for session {session_key}")
    return agent_id


def remove_agent(session_key: str) -> None:
    """
    Remove the agent mapping for a given session key.
    
    Args:
        session_key: The session identifier
    """
    if session_key in _SESSION_TO_AGENT:
        agent_id = _SESSION_TO_AGENT.pop(session_key)
        logger.info(f"Removed agent mapping: {session_key} -> {agent_id}")
    else:
        logger.debug(f"No agent mapping to remove for session {session_key}")


def list_active_sessions() -> dict[str, str]:
    """
    Get all active session mappings.
    
    Returns:
        Dict of session_key -> agent_id
    """
    return _SESSION_TO_AGENT.copy()
