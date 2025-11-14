import os
import json
from typing import List, Dict, Any
from datetime import datetime


class ConversationStore:
    def __init__(self, logs_dir: str = 'logs'):
        self.logs_dir = logs_dir
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # Create orders subdirectory
        self.orders_dir = os.path.join(self.logs_dir, 'orders')
        os.makedirs(self.orders_dir, exist_ok=True)

    def _session_path(self, session_id: str) -> str:
        safe = session_id.replace('/', '_').replace('\\', '_')
        return os.path.join(self.logs_dir, f'session_{safe}.jsonl')
    
    def _order_path(self, order_id: str) -> str:
        safe = order_id.replace('/', '_').replace('\\', '_')
        return os.path.join(self.orders_dir, f'order_{safe}.json')

    def append(self, session_id: str, role: str, text: str):
        """Append a message to conversation log."""
        path = self._session_path(session_id)
        entry = {
            'ts': datetime.utcnow().isoformat() + 'Z',
            'role': role,
            'text': text
        }
        with open(path, 'a', encoding='utf8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    def log_turn(self, session_id: str, user_message: str, assistant_response: str, mood: str = None):
        """Log a complete conversation turn with mood."""
        self.append(session_id, 'user', user_message)
        if mood:
            self.append(session_id, 'system', f'[mood_detected: {mood}]')
        self.append(session_id, 'assistant', assistant_response)

    def read(self, session_id: str) -> List[Dict]:
        """Read conversation history for a session."""
        path = self._session_path(session_id)
        if not os.path.exists(path):
            return []
        out = []
        with open(path, 'r', encoding='utf8') as f:
            for line in f:
                try:
                    out.append(json.loads(line))
                except Exception:
                    continue
        return out
    
    def log_order(self, session_id: str, order_data: Dict[str, Any]):
        """
        Log an order summary.
        
        Args:
            session_id: Session identifier
            order_data: Order details (restaurant, items, mood, allergies, total, etc.)
        """
        order_id = f"{session_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        path = self._order_path(order_id)
        
        order_record = {
            'order_id': order_id,
            'session_id': session_id,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'order_data': order_data
        }
        
        with open(path, 'w', encoding='utf8') as f:
            json.dumps(order_record, indent=2, ensure_ascii=False)
        
        # Also log to conversation
        self.append(session_id, 'system', f'[ORDER_PLACED: {order_id}]')
