import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo

from google import genai

from core.logger import Logger
from core.prompts import CATEGORIES, SHOPPING_LIST_PROMPT, TODO_LIST_PROMPT


class Brain:
    def __init__(self, model_name="gemini-2.5-flash-lite"):
        self.client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        self.model_name = model_name

    def interpret(self, message, context=None, list_type="shopping"):
        try:
            raw_response = self._generate(message, context, list_type)
            clean_json = (
                raw_response.text
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )
            return json.loads(clean_json)
        except Exception as error:
            Logger.info(f"[Brain] Parsing error: {str(error)}")
            return {"action": "ERROR", "value": str(error)}

    def _generate(self, message, context, list_type):
        state = json.dumps(context, indent=2) if context else "Empty"

        if list_type == "todo":
            timezone_name = os.environ.get("USER_TIMEZONE", "America/Lima")
            try:
                current_datetime = datetime.now(
                    ZoneInfo(timezone_name)
                ).isoformat()
            except Exception:
                timezone_name = "UTC"
                current_datetime = datetime.now(ZoneInfo("UTC")).isoformat()

            prompt = TODO_LIST_PROMPT.format(
                message=message,
                context=state,
                current_datetime=current_datetime,
                timezone=timezone_name,
            )
        else:
            prompt = SHOPPING_LIST_PROMPT.format(
                message=message,
                context=state,
                categories=", ".join(CATEGORIES),
            )

        return self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )
