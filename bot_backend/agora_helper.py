"""
Helper functions for Agora RTC and Chat integration.
"""

import time
import hmac
import hashlib
import struct
from typing import Optional
from config import agora_ai, agora_chat


class AgoraRTCHelper:
    """Helper for Agora RTC token management and channel operations."""
    
    @staticmethod
    def get_rtc_token(use_int_uid: bool = True) -> str:
        """
        Get RTC token from environment.
        
        Args:
            use_int_uid: If True, returns token for integer UID, else returns token for user account
        
        Returns:
            RTC token string
        
        Note:
            These tokens are for testing only. In production, generate tokens dynamically
            using the Agora RTC Token Builder with proper expiration times.
        """
        if use_int_uid:
            return agora_ai.RTC_TOKEN_INT_UID
        return agora_ai.RTC_TOKEN_USER_ACCOUNT
    
    @staticmethod
    def build_rtc_token(
        channel_name: str,
        uid: int = 0,
        role: int = 1,
        privilege_expired_ts: int = 0
    ) -> str:
        """
        Build RTC token dynamically (recommended for production).
        
        Args:
            channel_name: RTC channel name
            uid: User ID (0 for string user account)
            role: 1 for publisher, 2 for subscriber
            privilege_expired_ts: Token expiration timestamp (0 for 24h from now)
        
        Returns:
            Generated RTC token
        
        Note:
            For production use, implement proper token generation using Agora's
            RTC Token Builder library or use the existing token_helper.py
        """
        if privilege_expired_ts == 0:
            privilege_expired_ts = int(time.time()) + 86400  # 24 hours
        
        # This is a placeholder - use the actual token_helper.py implementation
        # or Agora's official token builder library
        from src.token_helper import build_token
        return build_token(channel_name, uid, agora_ai.APP_ID, agora_ai.APP_CERT, privilege_expired_ts)
    
    @staticmethod
    def validate_token_expiry(token: str) -> bool:
        """
        Check if token is expired (basic validation).
        
        Args:
            token: RTC token to validate
        
        Returns:
            True if token appears valid, False otherwise
        
        Note:
            This is a basic check. Proper validation requires decoding the token structure.
        """
        if not token or len(token) < 20:
            return False
        
        # RTC tokens start with the App ID
        return token.startswith(agora_ai.APP_ID)


class AgoraChatHelper:
    """Helper for Agora Chat REST API and WebSocket operations."""
    
    @staticmethod
    def get_rest_headers(auth_token: Optional[str] = None) -> dict:
        """
        Get headers for Agora Chat REST API requests.
        
        Args:
            auth_token: Optional authentication token
        
        Returns:
            Dictionary of HTTP headers
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        
        return headers
    
    @staticmethod
    def build_chat_message(
        from_user: str,
        to_user: str,
        message: str,
        msg_type: str = "text"
    ) -> dict:
        """
        Build Agora Chat message payload.
        
        Args:
            from_user: Sender user ID
            to_user: Recipient user ID
            message: Message content
            msg_type: Message type (text, image, audio, video, file, location, cmd)
        
        Returns:
            Message payload dictionary
        """
        return {
            "from": from_user,
            "to": to_user,
            "type": msg_type,
            "body": {
                "msg": message
            }
        }


class AgoraIntegrationHelper:
    """Combined helper for full Agora integration."""
    
    @staticmethod
    def get_agent_config(channel_name: str, agent_uid: int = 123456) -> dict:
        """
        Build Agora Conversational AI agent configuration.
        
        Args:
            channel_name: RTC channel name for the voice agent
            agent_uid: Agent's RTC user ID
        
        Returns:
            Agent configuration dictionary for Agora API
        """
        rtc_token = AgoraRTCHelper.get_rtc_token(use_int_uid=True)
        
        return {
            "channel_name": channel_name,
            "uid": agent_uid,
            "rtc_token": rtc_token,
            "app_id": agora_ai.APP_ID,
            "chat": {
                "rest_api": agora_chat.get_rest_api_url(),
                "websocket": agora_chat.get_websocket_url()
            }
        }
    
    @staticmethod
    def create_start_agent_payload(
        channel_name: str,
        rtc_token: Optional[str] = None,
        agent_uid: str = "0"
    ) -> dict:
        """
        Create payload for starting Agora Conversational AI agent.
        
        Args:
            channel_name: RTC channel name
            rtc_token: RTC token (if None, uses env token)
            agent_uid: Agent's user ID
        
        Returns:
            Start agent API payload
        """
        if rtc_token is None:
            rtc_token = AgoraRTCHelper.get_rtc_token(use_int_uid=True)
        
        return {
            "channel": channel_name,
            "rtc_token": rtc_token,
            "agent_rtc_uid": agent_uid,
            "llm": {
                "type": "custom",
                "url": "https://your-server.com/chat/completions",
                "model": "gemini-2.5-pro"
            }
        }


# Convenience exports
rtc_helper = AgoraRTCHelper()
chat_helper = AgoraChatHelper()
integration_helper = AgoraIntegrationHelper()
