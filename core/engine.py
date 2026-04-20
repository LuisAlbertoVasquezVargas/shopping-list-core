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

        if action == "ADD": return self.add_item(val)
        if action == "DELETE": return self.delete_item(val)
        if action == "READ": return self.read()
        if action == "ERROR": return {"error": val}
        
        return {"status": "confused", "msg": f"No action for: {val}"}

    def read(self):
        _, data = self._get_file()
        return data

    def add_item(self, name):
        file_ref, data = self._get_file()
        new_item = {"id": len(data["items"]) + 1, "name": name, "status": "pending"}
        data["items"].append(new_item)
        self.repo.update_file(self.path, f"feat: add {name}", json.dumps(data, indent=2), file_ref.sha)
        return new_item

    def delete_item(self, item_id):
        file_ref, data = self._get_file()
        data["items"] = [i for i in data["items"] if i["id"] != item_id]
        self.repo.update_file(self.path, f"fix: remove item {item_id}", json.dumps(data, indent=2), file_ref.sha)
        return True
