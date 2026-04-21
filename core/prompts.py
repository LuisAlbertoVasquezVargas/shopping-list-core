# core/prompts.py

INTENT_EXTRACTION_PROMPT = """
[SEMANTIC INTENT PARSER]
Target Languages: English, Spanish, Portuguese.
Output ONLY JSON.
Format: {{"action": "ADD|DELETE|READ|ERROR", "value": list|string|null}}

ACTION MAPPING:
1. ADD: User wants to put something on the list.
   - Synonyms: add, put, insert, buy, agrega, añade, pon, compra, adicionar, colocar, por, comprar.
2. DELETE: User wants to remove or clear something.
   - Synonyms: remove, delete, erase, kill, drop, clear, quita, borra, elimina, saca, remover, apagar, excluir, tirar.
3. READ: User wants to see the current items.
   - Synonyms: list, show, print, what's there, display, lista, muestra, enséñame, mostrar, listar, ver.

STRICT RULES:
- If numeric IDs are provided (e.g., 01, 04, 5), extract them as strings in the "value" list.
- If multiple items are mentioned (commas, "and", "y", "e", new lines), extract ALL into the "value" list.
- If the intent is unclear, use "ERROR".

USER INPUT:
{message}

JSON RESULT:
"""
