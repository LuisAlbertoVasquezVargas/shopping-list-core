# core/engine.py

from github import Github
import json
import re
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

    def dispatch(self, message):
        intent = self.brain.interpret(message)
        action = intent.get("action")
        val = intent.get("value")

        if action == "ERROR":
            return {"type": "error", "payload": val or "Unknown parsing error."}
        
        if action == "HELP":
            return {
                "type": "help", 
                "payload": "Commands: ADD [items], REMOVE [id/name], LIST, HELP. (Supported: EN, ES, PT)"
            }

        if action in ["ADD", "DELETE"] and val is None:
            return self.read()

        if action == "ADD": 
            res = self.add_items(val)
            return {"type": "table", "payload": res["items"]}

        if action == "DELETE": 
            res = self.delete_item(val)
            return {"type": "table", "payload": res["items"]}
        
        return {"type": "table", "payload": self.read()["items"]}

    def read(self):
        _, data = self._get_file()
        return data

    def add_items(self, val):
        if not val: return self.read()
        file_ref, data = self._get_file()
        items_to_process = val if isinstance(val, list) else [val]
        
        for raw_entry in items_to_process:
            match = re.search(r'\((.*?)\)', raw_entry)
            note = match.group(1) if match else ""
            name = re.sub(r'\(.*?\)', '', raw_entry).strip()
            
            ids = [i["id"] for i in data["items"]]
            next_id = max(ids) + 1 if ids else 1
            
            data["items"].append({
                "id": next_id, 
                "name": name, 
                "metadata": note,
                "status": "pending"
            })
        
        self.repo.update_file(self.path, "feat: update list items", json.dumps(data, indent=2), file_ref.sha)
        return data

    def delete_item(self, val):
        if not val: return self.read()
        file_ref, data = self._get_file()
        
        targets = val if isinstance(val, list) else [val]
        processed_targets = []
        for t in targets:
            t_str = str(t).strip()
            if t_str.isdigit():
                processed_targets.append(int(t_str))
            else:
                processed_targets.append(t_str.lower())
        
        def should_keep(item):
            item_id = item.get("id")
            item_name = str(item.get("name", "")).lower()
            if item_id in processed_targets: return False
            if item_name in processed_targets: return False
            return True

        original_count = len(data["items"])
        data["items"] = [i for i in data["items"] if should_keep(i)]
        
        if len(data["items"]) < original_count:
            self.repo.update_file(self.path, "fix: remove items", json.dumps(data, indent=2), file_ref.sha)
        else:
            Logger.info("No items matched for deletion.")
            
        return data
