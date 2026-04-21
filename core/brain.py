# core/brain.py

import os
import json
from google import genai
from core.prompts import INTENT_EXTRACTION_PROMPT
from core.logger import Logger

class Brain:
    def __init__(self, model_name="gemini-2.5-flash-lite"):
        self.client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        self.model_name = model_name

    def interpret(self, message, context=None):
        try:
            raw_response = self._generate(message, context)
            text = raw_response.text
            clean_json = text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json)
        except Exception as e:
            Logger.info(f"[Brain] Parsing error: {str(e)}")
            return {"action": "ERROR", "value": str(e)}

    def _generate(self, message, context):
        state_str = json.dumps(context, indent=2) if context else "Empty"
        prompt = INTENT_EXTRACTION_PROMPT.format(message=message, context=state_str)
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )
        return response
