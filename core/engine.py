# core/engine.py

from github import Github
import json
from core.brain import Brain

class Engine:
    def __init__(self, token, owner, repo_name):
        self.g = Github(token)
        self.repo = self.g.get_repo(f"{owner}/{repo_name}")
        self.path = "data/active_list.json"
        self.brain = Brain()

    def _get_file(self):
        file_ref = self.repo.get_contents(self.path)
        data = json.loads(file_ref.decoded_content.decode())
        return file_ref, data

    def dispatch(self, message):
        intent = self.brain.interpret(message)
        action = intent.get("action")
        val = intent.get("value")

        if action == "HELP": return {"type": "help"}
        if action == "READ": return self.read()
        if action == "ADD": return self.add_items(val)
        if action == "DELETE": return self.delete_item(val)
        
        return {"error": "Unknown intent"}

    def read(self):
        _, data = self._get_file()
        return data

    def add_items(self, val):
        """Handles both a single string or a list of strings"""
        file_ref, data = self._get_file()
        items_to_add = [val] if isinstance(val, str) else val
        
        new_entries = []
        for name in items_to_add:
            existing_ids = [i["id"] for i in data["items"]]
            next_id = max(existing_ids) + 1 if existing_ids else 1
            item = {"id": next_id, "name": name, "status": "pending"}
            data["items"].append(item)
            new_entries.append(name)

        # Batch Update
        commit_msg = f"feat: batch add {', '.join(new_entries[:3])}"
        self.repo.update_file(self.path, commit_msg, json.dumps(data, indent=2), file_ref.sha)
        
        # Return the updated list so the UI refreshes the table
        return data

    def delete_item(self, item_id):
        file_ref, data = self._get_file()
        # Handle case where ID is passed as string or int
        data["items"] = [i for i in data["items"] if str(i["id"]) != str(item_id)]
        self.repo.update_file(self.path, f"fix: remove item {item_id}", json.dumps(data, indent=2), file_ref.sha)
        return data
