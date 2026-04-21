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
        intent = self.brain.interpret(message)
        action = intent.get("action")
        val = intent.get("value")

        print(f"\n[BRAIN LOG] Action: {action} | Value: {val}")

        if action == "ERROR": return {"type": "error", "payload": val}
        if action == "ADD": return self.add_items(val)
        if action == "DELETE": return self.delete_item(val)
        if action == "READ": return self.read()

        return self.read()

    def read(self):
        _, data = self._get_file()
        return data

    def add_items(self, val):
        if not val: return self.read()
        file_ref, data = self._get_file()
        items_to_add = val if isinstance(val, list) else [val]
        for name in items_to_add:
            ids = [i["id"] for i in data["items"]]
            next_id = max(ids) + 1 if ids else 1
            data["items"].append({"id": next_id, "name": name.strip(), "status": "pending"})
        self.repo.update_file(self.path, f"feat: add {len(items_to_add)} items", json.dumps(data, indent=2), file_ref.sha)
        return data

    def delete_item(self, val):
        file_ref, data = self._get_file()
        targets = [str(v).lower() for v in (val if isinstance(val, list) else [val])]
        data["items"] = [i for i in data["items"] if str(i["id"]) not in targets and i["name"].lower() not in targets]
        self.repo.update_file(self.path, f"fix: remove items", json.dumps(data, indent=2), file_ref.sha)
        return data
