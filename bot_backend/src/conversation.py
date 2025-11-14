from typing import Optional, List, Dict, Any
import re
from .logging_store import ConversationStore
from .llm import get_default_llm, LocalLLMStub
from .recommender import Recommender


class ConversationManager:
    """Manages conversation state per session, uses LLM to classify mood and calls recommender.

    This manager persists messages via ConversationStore. It is intentionally simple so it
    can be extended with richer dialogue policies later.
    """

    def __init__(self, store: ConversationStore, recommender: Recommender, llm: Optional[Any] = None):
        self.store = store
        self.recommender = recommender
        self.llm = llm or get_default_llm()

    def _extract_existing_mood(self, session_id: str) -> Optional[str]:
        history = self.store.read(session_id)
        for e in reversed(history):
            if e.get('role') == 'bot' and 'detected mood' in e.get('text', '').lower():
                parts = e['text'].split(':')
                if len(parts) >= 2:
                    return parts[1].strip()
        return None

    async def classify_mood(self, text: str) -> Dict:
        try:
            return await self.llm.classify_mood(text)
        except Exception:
            return await LocalLLMStub().classify_mood(text)

    def parse_constraints(self, text: str) -> Dict:
        max_cal = None
        tastes: List[str] = []
        m = re.search(r'(\d{2,4})\s*(k?cal|calories|kcal)?', text.lower())
        if m:
            try:
                max_cal = int(m.group(1))
            except Exception:
                max_cal = None
        for kw in ['spicy', 'sweet', 'sour', 'salty', 'savory', 'crispy', 'fried', 'veg', 'vegetarian', 'non-veg', 'vegan']:
            if kw in text.lower():
                tastes.append(kw)
        return {'max_calories': max_cal, 'tastes': tastes}

    async def process_user_message(self, session_id: str, message: str) -> Dict:
        self.store.append(session_id, 'user', message)

        detected_mood = self._extract_existing_mood(session_id)

        if not detected_mood:
            # Try classify with LLM
            mood_res = await self.classify_mood(message)
            mood = mood_res.get('mood')
            confidence = mood_res.get('confidence', 0.0)
            if mood and mood != 'neutral':
                bot_text = f"Detected mood: {mood}. Do you want food suggestions for this mood? Also tell me if you have a calorie limit or taste preference."
                self.store.append(session_id, 'bot', bot_text)
                return {'reply': bot_text, 'mood': mood, 'suggestions': None}
            else:
                bot_text = "I couldn't tell how you're feeling — could you tell me your current mood (happy, sad, energetic, romantic, etc.)? Also mention if you care about calories or taste."
                self.store.append(session_id, 'bot', bot_text)
                return {'reply': bot_text, 'mood': None, 'suggestions': None}

        # If we already have mood, parse constraints from current message
        constraints = self.parse_constraints(message)
        suggestions = self.recommender.recommend(mood=detected_mood, max_calories=constraints.get('max_calories'), tastes=constraints.get('tastes'))
        if not suggestions:
            bot_text = "Sorry, I couldn't find suggestions that match your requirements. Try relaxing constraints or checking back later."
            self.store.append(session_id, 'bot', bot_text)
            return {'reply': bot_text, 'mood': detected_mood, 'suggestions': []}

        lines = [f"Here are some recommendations for mood: {detected_mood}: \n"]
        for s in suggestions:
            name = s.get('name') or s.get('title') or s.get('dish') or s.get('food') or 'Unknown'
            cal_col = None
            for c in ['calories', 'calorie', 'kcal']:
                if c in s:
                    cal_col = s.get(c)
                    break
            cal_info = f" ({cal_col} kcal)" if cal_col else ''
            lines.append(f"- {name}{cal_info}")
        bot_text = '\n'.join(lines)
        self.store.append(session_id, 'bot', bot_text)
        return {'reply': bot_text, 'mood': detected_mood, 'suggestions': suggestions}
