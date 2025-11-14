
import os
from typing import Optional, Dict, Any
import base64
import aiohttp
import json


class AgoraConnector:
    """Connector for Agora Conversational AI REST API.

    Reads `AGORA_API_BASE` from env if present. Authentication uses Basic auth
    with `AGORA_CUSTOMER_ID`:`AGORA_CUSTOMER_SECRET`. If those are absent and
    `AGORA_APP_ID` is present we send a best-effort Basic header built from
    the App ID, but production integrations should use Customer credentials.
    """

    DEFAULT_BASE = 'https://api.agora.io/api/conversational-ai-agent/v2'

    def __init__(
        self,
        app_id: Optional[str] = None,
        customer_id: Optional[str] = None,
        customer_secret: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        self.app_id = app_id or os.environ.get('AGORA_APP_ID')
        self.customer_id = customer_id or os.environ.get('AGORA_CUSTOMER_ID')
        self.customer_secret = customer_secret or os.environ.get('AGORA_CUSTOMER_SECRET')
        self.base = base_url or os.environ.get('AGORA_API_BASE') or self.DEFAULT_BASE

    def _auth_header(self) -> Dict[str, str]:
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        if self.customer_id and self.customer_secret:
            raw = f"{self.customer_id}:{self.customer_secret}".encode('utf8')
            token = base64.b64encode(raw).decode('ascii')
            headers['Authorization'] = f'Basic {token}'
            return headers
        # fallback: if only app id present, send it as Basic as well (best-effort)
        if self.app_id:
            token = base64.b64encode(self.app_id.encode('utf8')).decode('ascii')
            headers['Authorization'] = f'Basic {token}'
            return headers
        raise RuntimeError('No Agora credentials available: set AGORA_CUSTOMER_ID/AGORA_CUSTOMER_SECRET or AGORA_APP_ID in environment')

    async def _handle_response(self, resp: aiohttp.ClientResponse) -> Any:
        text = await resp.text()
        try:
            data = json.loads(text)
        except Exception:
            data = text
        if resp.status >= 400:
            raise RuntimeError(f'Agora API error {resp.status}: {data}')
        return data

    async def join(self, channel: str, rtc_token: str, agent_rtc_uid: str = '0', llm_config: Optional[Dict[str, Any]] = None) -> Dict:
        """Start a conversational AI agent that joins an Agora channel.

        Returns the agent creation response (agent_id, status, etc.).
        """
        if not self.app_id:
            raise RuntimeError('AGORA_APP_ID is required')
        url = f"{self.base}/projects/{self.app_id}/join"
        headers = self._auth_header()
        payload = {
            'name': f'agent_{channel}',
            'properties': {
                'channel': channel,
                'token': rtc_token,
                'agent_rtc_uid': agent_rtc_uid,
                'remote_rtc_uids': ['*'],
                'enable_string_uid': False,
                'idle_timeout': 120,
                'llm': llm_config or {}
            }
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as resp:
                return await self._handle_response(resp)

    async def query(self, agent_id: str) -> Dict:
        if not self.app_id:
            raise RuntimeError('AGORA_APP_ID is required')
        url = f"{self.base}/projects/{self.app_id}/agents/{agent_id}"
        headers = self._auth_header()
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                return await self._handle_response(resp)

    async def leave(self, agent_id: str) -> Dict:
        if not self.app_id:
            raise RuntimeError('AGORA_APP_ID is required')
        url = f"{self.base}/projects/{self.app_id}/agents/{agent_id}/leave"
        headers = self._auth_header()
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers) as resp:
                return await self._handle_response(resp)

    async def speak(self, agent_id: str, text: str, priority: str = 'INTERRUPT', interruptable: bool = True) -> Dict:
        if not self.app_id:
            raise RuntimeError('AGORA_APP_ID is required')
        url = f"{self.base}/projects/{self.app_id}/agents/{agent_id}/speak"
        headers = self._auth_header()
        payload = {
            'text': text,
            'priority': priority,
            'interruptable': interruptable
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as resp:
                return await self._handle_response(resp)

    async def interrupt(self, agent_id: str) -> Dict:
        if not self.app_id:
            raise RuntimeError('AGORA_APP_ID is required')
        url = f"{self.base}/projects/{self.app_id}/agents/{agent_id}/interrupt"
        headers = self._auth_header()
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={}, headers=headers) as resp:
                return await self._handle_response(resp)

    async def history(self, agent_id: str) -> Dict:
        if not self.app_id:
            raise RuntimeError('AGORA_APP_ID is required')
        url = f"{self.base}/projects/{self.app_id}/agents/{agent_id}/history"
        headers = self._auth_header()
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                return await self._handle_response(resp)

    async def list_agents(self, channel: Optional[str] = None, from_time: Optional[int] = None, to_time: Optional[int] = None, state: Optional[int] = None, limit: int = 20, cursor: Optional[str] = None) -> Dict:
        if not self.app_id:
            raise RuntimeError('AGORA_APP_ID is required')
        params = {'limit': limit}
        if channel:
            params['channel'] = channel
        if from_time:
            params['from_time'] = from_time
        if to_time:
            params['to_time'] = to_time
        if state is not None:
            params['state'] = state
        if cursor:
            params['cursor'] = cursor
        url = f"{self.base}/projects/{self.app_id}/agents"
        headers = self._auth_header()
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as resp:
                return await self._handle_response(resp)
