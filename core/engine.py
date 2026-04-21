# core/engine.py

from github import Github
import json
from core.brain import Brain

class Engine:
    def __init__(self, token, owner, repo_name, model_name="gemini-2.0-flash"):
        self.g = Github(token)
        self.repo = self.g.get_repo(f"{owner}/{repo_name}")
        self.path = "data/active_list.json"
        self.brain = Brain(model_name=model_name)

    def _get_file(self):
        file_ref = self.repo.get_contents(self.path)
        data = json.loads(file_ref.decoded_content.decode())
        return file_ref, data

    def dispatch(self, message):
        msg_clean = message.lower().strip()
        
        if msg_clean in ["show", "list", "read"]:
            return self.read()

        if msg_clean.startswith("add "):
            return self.add_items(message[4:].strip())

        if msg_clean.startswith("del ") or msg_clean.startswith("delete "):
            target = msg_clean.replace("delete", "").replace("del", "").strip()
            return self.delete_item(target)

        intent = self.brain.interpret(message)
        action = intent.get("action")
        val = intent.get("value")

        if action == "ERROR": return {"type": "error", "payload": val}
        if action == "ADD": return self.add_items(val)
        if action == "DELETE": return self.delete_item(val)
        
        return self.read()

    def read(self):
        _, data = self._get_file()
        return data

    def add_items(self, val):
        if not val: return self.read()
        file_ref, data = self._get_file()
        
        raw_items = val.split('\n') if isinstance(val, str) else val
        items_to_add = [i.strip() for i in raw_items if i and i.strip()]

        if not items_to_add: return data

        for name in items_to_add:
            ids = [i["id"] for i in data["items"]]
            next_id = max(ids) + 1 if ids else 1
            data["items"].append({"id": next_id, "name": name, "status": "pending"})

        commit_msg = f"feat: add {', '.join(items_to_add[:3])}"
        self.repo.update_file(self.path, commit_msg, json.dumps(data, indent=2), file_ref.sha)
        return data

    def delete_item(self, target):
        file_ref, data = self._get_file()
        data["items"] = [i for i in data["items"] if str(i["id"]) != str(target) and i["name"].lower() != str(target).lower()]
        self.repo.update_file(self.path, f"fix: remove {target}", json.dumps(data, indent=2), file_ref.sha)
        return data
