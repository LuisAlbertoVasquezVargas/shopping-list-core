# core/brain.py

import os
import json
from google import genai
from core.prompts import INTENT_EXTRACTION_PROMPT
from core.logger import Logger

class Brain:
    def __init__(self, model_name="gemini-2.0-flash-lite"):
        self.client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        self.model_name = model_name.replace("models/", "")
        self.fallback_model = "gemini-2.0-flash-lite"

    def interpret(self, message):
        if not message or len(message.strip()) == 0:
            return {"action": "READ", "value": None}

        # Try primary model, fallback on 503
        result = self._generate(self.model_name, message)
        
        if result.get("action") == "ERROR" and "503" in result.get("value", ""):
            if self.model_name != self.fallback_model:
                Logger.info(f"Primary model busy. Falling back to {self.fallback_model}...")
                return self._generate(self.fallback_model, message)
        
        return result

    def _generate(self, model, message):
        prompt = INTENT_EXTRACTION_PROMPT.format(message=message)
        try:
            response = self.client.models.generate_content(
                model=model,
                contents=prompt,
                config={"response_mime_type": "application/json", "temperature": 0}
            )
            data = json.loads(response.text.strip())
            Logger.brain(data.get("action"), data.get("value"))
            return data
        except Exception as e:
            Logger.error(f"Brain ({model})", str(e))
            return {"action": "ERROR", "value": str(e)}
