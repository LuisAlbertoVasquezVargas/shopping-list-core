# core/brain.py

import os
import json
from google import genai
from core.prompts import INTENT_EXTRACTION_PROMPT

class Brain:
    def __init__(self, model_name="gemini-2.0-flash"):
        self.client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        self.model_name = model_name.replace("models/", "")

    def interpret(self, message):
        if not message or len(message.strip()) == 0:
            return {"action": "READ", "value": None}

        prompt = INTENT_EXTRACTION_PROMPT.format(message=message)
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={"response_mime_type": "application/json", "temperature": 0}
            )
            return json.loads(response.text.strip())
        except Exception as e:
            return {"action": "ERROR", "value": f"Brain ({self.model_name}) Error: {str(e)}"}
