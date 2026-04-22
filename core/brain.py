# core/brain.py

import os
import json
from google import genai
from core.prompts import INTENT_EXTRACTION_PROMPT, CATEGORIES
from core.logger import Logger

class Brain:
    def __init__(self, model_name="gemini-2.5-flash-lite"):
        self.keys = os.environ.get("GEMINI_API_KEYS", "").split(",")
        self.current_key_index = 0
        self.model_name = model_name
        self._init_client()

    def _init_client(self):
        key = self.keys[self.current_key_index].strip()
        self.client = genai.Client(api_key=key)

    def _rotate_key(self):
        self.current_key_index = (self.current_key_index + 1) % len(self.keys)
        Logger.info(f"[Brain] Rotating to API Key #{self.current_key_index + 1}")
        self._init_client()

    def interpret(self, message, context=None):
        for _ in range(len(self.keys)):
            try:
                raw_response = self._generate(message, context)
                text = raw_response.text
                clean_json = text.replace("```json", "").replace("```", "").strip()
                return json.loads(clean_json)
            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "403" in err_str:
                    self._rotate_key()
                    continue
                Logger.info(f"[Brain] Error: {err_str}")
                return {"action": "ERROR", "value": err_str}
        return {"action": "ERROR", "value": "Exhausted all keys."}

    def _generate(self, message, context):
        state_str = json.dumps(context, indent=2) if context else "Empty"
        prompt = INTENT_EXTRACTION_PROMPT.format(
            message=message, 
            context=state_str,
            categories=", ".join(CATEGORIES)
        )
        return self.client.models.generate_content(model=self.model_name, contents=prompt)
