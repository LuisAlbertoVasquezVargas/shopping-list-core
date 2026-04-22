# core/engine.py

from github import Github
import json
from core.brain import Brain
from core.logger import Logger

class Engine:
    def __init__(self, token, owner, repo_name, model_name="gemini-2.5-flash-lite"):
        self.g = Github(token)
        self.repo = self.g.get_repo(f"{owner}/{repo_name}")
        self.path = "data/active_list.json"
        self.brain = Brain(model_name=model_name)

    def _get_file(self):
        file_ref = self.repo.get_contents(self.path)
        data = json.loads(file_ref.decoded_content.decode())
        return file_ref, data

    def read(self):
        _, data = self._get_file()
        return data

    def dispatch(self, message):
        try:
            _, current_data = self._get_file()
            intent = self.brain.interpret(message, context=current_data)
            action = intent.get("action", "ERROR")
            val = intent.get("value")
            conf = intent.get("confirmation", "Processed.")

            if action == "READ":
                return self._format_response(current_data, conf, "READ")
            if action == "DELETE":
                targets = [t.get("name") or t.get("id") if isinstance(t, dict) else t for t in (val if isinstance(val, list) else [val])]
                data = self.delete_item(targets)
                return self._format_response(data, conf, "DELETE")
            if action == "ADD":
                data = self.add_items(val)
                return self._format_response(data, conf, "ADD")
            if action == "CLEAR":
                data = self.clear_list()
                return self._format_response(data, conf, "CLEAR")
            if action == "HELP":
                return {"type": "help", "payload": [], "meta": {"action": "HELP", "message": conf}}
            return {"type": "error", "payload": f"Unhandled action: {action}"}
        except Exception as e:
            Logger.info(f"[Engine] Crash: {str(e)}")
            return {"type": "error", "payload": f"Internal Error: {str(e)}"}

    def _format_response(self, data, message, action):
        return {
            "type": "table",
            "payload": data.get("items", []),
            "meta": {"action": action, "message": message}
        }

    def delete_item(self, val):
        file_ref, data = self._get_file()
        targets = [str(t).lower() for t in val if t is not None]
        data["items"] = [i for i in data["items"] if str(i["id"]) not in targets and str(i["name"]).lower() not in targets]
        self.repo.update_file(self.path, "fix: remove items", json.dumps(data, indent=2), file_ref.sha)
        return data

    def add_items(self, items_list):
        if not items_list: return self.read()
        file_ref, data = self._get_file()
        for item in items_list:
            ids = [i["id"] for i in data["items"]]
            next_id = max(ids) + 1 if ids else 1
            data["items"].append({
                "id": next_id,
                "name": item.get("name", "Unknown"),
                "metadata": item.get("notes", ""),
                "category": item.get("category", "Other"),
                "status": "pending"
            })
        self.repo.update_file(self.path, "feat: add items", json.dumps(data, indent=2), file_ref.sha)
        return data

    def clear_list(self):
        file_ref, data = self._get_file()
        data["items"] = []
        self.repo.update_file(self.path, "feat: clear list", json.dumps(data, indent=2), file_ref.sha)
        return data
