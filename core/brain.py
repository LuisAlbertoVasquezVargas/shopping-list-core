# core/brain.py

import os
import json
from google import genai

class Brain:
    def __init__(self):
        self.client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    def _mock_interpret(self, message):
        msg = message.lower().strip()
        parts = msg.split()
        
        if msg == "help":
            return {"action": "HELP", "value": None}
            
        if any(w in msg for w in ["add", "buy", "get", "need"]):
            item = " ".join(parts[1:]) if len(parts) > 1 else "Unknown"
            return {"action": "ADD", "value": item}
            
        if any(w in msg for w in ["remove", "delete", "discard"]):
            # Mock remains rigid, but LLM will be smarter
            try: 
                return {"action": "DELETE", "value": int(parts[-1])}
            except: 
                return {"action": "DELETE", "value": parts[-1]} # Pass the string if ID fails
                
        return {"action": "READ", "value": None}

    def interpret(self, message):
        prompt = f"""
        Extract the user's intent into a JSON object.
        
        Valid Actions:
        - ADD: User wants to put something on the list.
        - DELETE: User wants to remove something (by ID or by name).
        - READ: User wants to see the list.
        - HELP: User explicitly asked for help or commands.

        Instructions:
        1. If DELETE is used with a name (e.g., "pollito"), set value to that name.
        2. If DELETE is used with an ID, set value to the integer ID.
        3. For HELP, set value to null.
        4. Include an "explanation" field if you are correcting a typo or mapping a nickname (e.g., "Interpreted 'pollito' as 'pollo'").

        Message: {message}
        """
        
        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config={"response_mime_type": "application/json"}
            )
            return json.loads(response.text)
        except Exception as e:
            return self._mock_interpret(message)
