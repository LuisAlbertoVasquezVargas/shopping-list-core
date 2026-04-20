# core/brain.py

import os
import json
from google import genai

class Brain:
    def __init__(self):
        self.client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    def _mock_interpret(self, message):
        msg = message.lower().strip()
        parts = message.split()
        if any(w in msg for w in ["add", "buy", "get", "need"]):
            item = " ".join(parts[1:]) if len(parts) > 1 else "Unknown"
            return {"action": "ADD", "value": item}
        if any(w in msg for w in ["remove", "delete", "discard"]):
            try: return {"action": "DELETE", "value": int(parts[-1])}
            except: return {"action": "ERROR", "value": "ID required"}
        return {"action": "READ", "value": None}

    def interpret(self, message):
        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=f"Extract intent JSON (ADD/value, DELETE/value, READ/null) from: {message}",
                config={"response_mime_type": "application/json"}
            )
            return json.loads(response.text)
        except Exception as e:
            # Silently fallback so the user experience is seamless
            return self._mock_interpret(message)
