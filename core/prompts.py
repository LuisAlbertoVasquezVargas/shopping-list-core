# core/prompts.py

INTENT_EXTRACTION_PROMPT = """
[SHOPPING CORE PARSER v2.0]
Return STRICT JSON only.

SCHEMA:
{{
  "action": "ADD|DELETE|READ|CLEAR|HELP",
  "value": [
    {{"name": "item name", "category": "category", "notes": "extra info"}}
  ],
  "confirmation": "Natural language response grounded in current state"
}}

NOTE: For DELETE, "value" must be a list of objects containing the "name" or "id" to remove.

CURRENT LIST STATE:
{context}

USER INPUT:
{message}
"""
