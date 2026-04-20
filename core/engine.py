# core/engine.py

from github import Github
import json

class Engine:
    def __init__(self, token, owner, repo_name):
        self.g = Github(token)
        self.repo = self.g.get_repo(f"{owner}/{repo_name}")
        self.path = "data/active_list.json"

    def _get_file(self):
        file_ref = self.repo.get_contents(self.path)
        data = json.loads(file_ref.decoded_content.decode())
        return file_ref, data

    def read(self):
        _, data = self._get_file()
        return data

    def add_item(self, name):
        file_ref, data = self._get_file()
        new_item = {
            "id": len(data["items"]) + 1,
            "name": name,
            "status": "pending"
        }
        data["items"].append(new_item)
        self.repo.update_file(self.path, f"feat: add {name}", json.dumps(data, indent=2), file_ref.sha)
        return new_item

    def update_item(self, item_id, status):
        file_ref, data = self._get_file()
        for item in data["items"]:
            if item["id"] == item_id:
                item["status"] = status
                break
        self.repo.update_file(self.path, f"patch: item {item_id} to {status}", json.dumps(data, indent=2), file_ref.sha)
        return True

    def delete_item(self, item_id):
        file_ref, data = self._get_file()
        data["items"] = [i for i in data["items"] if i["id"] != item_id]
        self.repo.update_file(self.path, f"fix: remove item {item_id}", json.dumps(data, indent=2), file_ref.sha)
        return True
