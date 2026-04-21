# core/brain.py

import os
import json
from google import genai

class Brain:
    def __init__(self):
        self.client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    def _mock_interpret(self, message):
        msg = message.lower().strip()
        lines = [l.strip() for l in msg.split('\n') if l.strip()]
        
        if msg == "help":
            return {"action": "HELP", "value": None}
            
        if lines[0].startswith("add"):
            # Simple mock: if first line is 'add', take subsequent lines as items
            items = lines[1:] if len(lines) > 1 else [lines[0].replace("add", "").strip()]
            return {"action": "ADD", "value": [i for i in items if i]}
                
        return {"action": "READ", "value": None}

    def interpret(self, message):
        prompt = f"""
        Extract user intent into JSON. 
        
        Actions: ADD, DELETE, READ, HELP.
        
        For ADD:
        If the message contains multiple lines of items, return 'value' as a list of strings.
        Example: 
        "add
        milk
        eggs" -> {{"action": "ADD", "value": ["milk", "eggs"]}}

        Message:
        {message}
        """
        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config={"response_mime_type": "application/json"}
            )
            return json.loads(response.text)
        except:
            return self._mock_interpret(message)
