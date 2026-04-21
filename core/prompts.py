# core/prompts.py

INTENT_EXTRACTION_PROMPT = """
[SEMANTIC INTENT PARSER v1.2]
Languages: English, Spanish, Portuguese.
Output ONLY JSON.
Format: {{"action": "ADD|DELETE|READ|HELP|ERROR", "value": list|string|null}}

ACTION MAPPING:
1. ADD: User wants to append items. 
   - Note extraction: If the user provides info in (brackets) or after "note:", "obs:", "nota:", extract it alongside the item.
   - Format ADD value as: ["Item Name (Note)", "Second Item"]
2. DELETE: User wants to remove items by ID or name.
3. READ: User wants to see the list.
4. HELP: User asks for the manual/commands.

STRICT RULES:
- If multiple items are listed (e.g. "add eggs, bread, and milk"), return a list of strings.
- Keep the (note) attached to the string in the value list.
- For multilingual inputs like "elimina 04" or "quitar cama", map to DELETE.

USER INPUT:
{message}

JSON RESULT:
"""
