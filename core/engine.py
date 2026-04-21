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
        action = intent["action"]
        val = intent["value"]
        explanation = intent.get("explanation") # Capture Gemini's reasoning

        # 1. HELP branch: Signal the frontend to show the HelpView
        if action == "HELP": 
            return {"type": "help"}

        # 2. Add explanation to responses if Gemini provided one
        res = None
        if action == "ADD": res = self.add_item(val)
        elif action == "DELETE": res = self.delete_item(val)
        elif action == "READ": res = self.read()
        elif action == "ERROR": return {"error": val}
        else: return {"status": "confused", "msg": f"No action for: {val}"}

        # If it's an "Honest AI" moment, attach the explanation to the result
        if explanation and isinstance(res, (dict, list)):
            return {"explanation": explanation, "items": res if isinstance(res, list) else None, **(res if isinstance(res, dict) else {})}
        
        return res

    def read(self):
        _, data = self._get_file()
        return data

    def add_item(self, name):
        file_ref, data = self._get_file()
        existing_ids = [i["id"] for i in data["items"]]
        next_id = max(existing_ids) + 1 if existing_ids else 1
        
        new_item = {"id": next_id, "name": name, "status": "pending"}
        data["items"].append(new_item)
        
        self.repo.update_file(self.path, f"feat: add {name}", json.dumps(data, indent=2), file_ref.sha)
        return new_item

    def delete_item(self, target):
        """target can be an int (ID) or a string (Name)"""
        file_ref, data = self._get_file()
        initial_count = len(data["items"])
        
        # Flexible filter: check ID if target is int, check Name if target is string
        if isinstance(target, int):
            data["items"] = [i for i in data["items"] if i["id"] != target]
        else:
            # Case-insensitive name match
            data["items"] = [i for i in data["items"] if i["name"].lower() != str(target).lower()]
        
        if len(data["items"]) == initial_count:
            return {"error": f"Item '{target}' not found"}

        self.repo.update_file(self.path, f"fix: remove {target}", json.dumps(data, indent=2), file_ref.sha)
        return True
