"""
Configuration management for Agora Chat and Conversational AI integration.
"""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class AgoraChatConfig:
    """Configuration for Agora Chat REST API and WebSocket."""
    
    REST_API_BASE: str = os.environ.get("AGORA_CHAT_REST_API", "a61.chat.agora.io")
    WEBSOCKET_BASE: str = os.environ.get("AGORA_CHAT_WEBSOCKET", "mysync-api-61.chat.agora.io")
    
    @classmethod
    def get_rest_api_url(cls, path: str = "") -> str:
        """Get full REST API URL with optional path."""
        base = cls.REST_API_BASE
        if not base.startswith("http"):
            base = f"https://{base}"
        return f"{base}/{path.lstrip('/')}" if path else base
    
    @classmethod
    def get_websocket_url(cls, path: str = "") -> str:
        """Get full WebSocket URL with optional path."""
        base = cls.WEBSOCKET_BASE
        if not base.startswith("ws"):
            base = f"wss://{base}"
        return f"{base}/{path.lstrip('/')}" if path else base


class AgoraConversationalAIConfig:
    """Configuration for Agora Conversational AI."""
    
    APP_ID: str = os.environ.get("AGORA_APP_ID", "")
    CUSTOMER_ID: str = os.environ.get("AGORA_CUSTOMER_ID", "")
    CUSTOMER_SECRET: str = os.environ.get("AGORA_CUSTOMER_SECRET", "")
    APP_CERT: str = os.environ.get("AGORA_APP_CERT", "")
    API_BASE: str = os.environ.get(
        "AGORA_API_BASE",
        "https://api.agora.io/api/conversational-ai-agent/v2"
    )
    CONV_AI_BASE_URL: str = os.environ.get(
        "AGORA_CONV_AI_BASE_URL",
        "https://api.agora.io/api/conversational-ai-agent/v2"
    )
    AGENT_IDLE_TIMEOUT: int = int(os.environ.get("AGORA_AGENT_IDLE_TIMEOUT", "120"))
    
    # RTC Tokens (for testing - should be generated dynamically in production)
    RTC_TOKEN_INT_UID: str = os.environ.get("AGORA_RTC_TOKEN_INT_UID", "")
    RTC_TOKEN_USER_ACCOUNT: str = os.environ.get("AGORA_RTC_TOKEN_USER_ACCOUNT", "")


class GeminiConfig:
    """Configuration for Gemini LLM."""
    
    API_KEY: str = os.environ.get("GEMINI_API_KEY", "")
    DEFAULT_MODEL: str = os.environ.get("DEFAULT_MODEL", "gemini-2.5-pro")
    BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta/openai/"


class LLMConfig:
    """Configuration for external LLM API."""
    
    API_KEY: str = os.environ.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY", "")
    API_URL: str = os.environ.get("LLM_API_URL", "https://m5vdftcq-8000.inc1.devtunnels.ms/chat/completions")
    MODEL: str = os.environ.get("LLM_MODEL", "gpt-4o-mini")


class TTSConfig:
    """Configuration for Text-to-Speech (Microsoft Azure)."""
    
    API_KEY: str = os.environ.get("TTS_API_KEY", "")
    VOICE_ID: str = os.environ.get("TTS_VOICE_ID", "FZkK3TvQ0pjyDmT8fzIW")


class AppConfig:
    """General application configuration."""
    
    LOGS_DIR: str = os.environ.get("LOGS_DIR", "logs")
    DATA_CSV: str = os.environ.get("DATA_CSV", "Indian-Food-Data.csv")
    PORT: int = int(os.environ.get("PORT", "8000"))
    HOST: str = os.environ.get("HOST", "0.0.0.0")


# Convenience exports
agora_chat = AgoraChatConfig()
agora_ai = AgoraConversationalAIConfig()
gemini = GeminiConfig()
llm_config = LLMConfig()
tts_config = TTSConfig()
app_config = AppConfig()
