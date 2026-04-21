# core/prompts.py

INTENT_EXTRACTION_PROMPT = """
[STRICT PARSER]
Output ONLY JSON.
Format: {{"action": "ADD|DELETE|READ|ERROR", "value": list|string|null}}

COMMAND PROTOCOL:
1. Input MUST start with a command: ADD, DELETE, REMOVE, LIST, SHOW.
2. If no valid command is found at the start, action is ERROR.
3. Multi-line/commas: extract each item into the "value" list.

EXAMPLES:
"add milk, eggs" -> {{"action": "ADD", "value": ["milk", "eggs"]}}
"remove 01, 05" -> {{"action": "DELETE", "value": ["01", "05"]}}
"list" -> {{"action": "READ", "value": null}}

USER INPUT:
{message}

JSON RESULT:
"""
