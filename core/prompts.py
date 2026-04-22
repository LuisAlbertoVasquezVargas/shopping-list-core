# core/prompts.py

CATEGORIES = ["Grocery", "Electronics", "House stuff", "Kitchen stuff", "Bicycle", "Personal Care", "Other"]

INTENT_EXTRACTION_PROMPT = """
[SHOPPING CORE v2.1]
Return STRICT JSON.

CATEGORIES: {categories}

SCHEMA:
{{
  "action": "ADD|DELETE|READ|CLEAR|HELP",
  "value": [
    {{"name": "item", "category": "one from CATEGORIES list", "notes": "info"}}
  ],
  "confirmation": "A single-sentence, professional acknowledgement."
}}

CONTEXT:
{context}

USER MESSAGE:
{message}
"""
