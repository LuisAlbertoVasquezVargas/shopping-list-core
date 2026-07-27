# core/engine.py

from github import Github
import json
from datetime import datetime, timezone
from uuid import uuid4
from core.brain import Brain
from core.logger import Logger

class Engine:
    def __init__(self, token, owner, repo_name, model_name="gemini-2.5-flash-lite"):
        self.g = Github(token)
        self.repo = self.g.get_repo(f"{owner}/{repo_name}")
        self.path = "data/lists.json"
        self.legacy_path = "data/active_list.json"
        self.brain = Brain(model_name=model_name)

    def _get_file(self):
        try:
            file_ref = self.repo.get_contents(self.path)
            data = json.loads(file_ref.decoded_content.decode())
            return file_ref, self._normalize_store(data)
        except Exception as error:
            if getattr(error, "status", None) != 404:
                raise
            return self._migrate_legacy_list()

    def _migrate_legacy_list(self):
        legacy_ref = self.repo.get_contents(self.legacy_path)
        legacy_data = json.loads(legacy_ref.decoded_content.decode())
        now = self._now()
        store = {
            "version": "2.0",
            "lists": [{
                "id": uuid4().hex,
                "name": "My shopping list",
                "type": "shopping",
                "created_at": now,
                "updated_at": legacy_data.get("last_updated", now),
                "items": legacy_data.get("items", []),
            }],
        }
        file_ref = self.repo.create_file(
            self.path,
            "feat: migrate shopping data to multiple lists",
            json.dumps(store, indent=2),
        )
        return file_ref["content"], store

    def _normalize_store(self, data):
        if not isinstance(data, dict) or not isinstance(data.get("lists"), list):
            raise ValueError("Invalid multi-list data store.")
        for shopping_list in data["lists"]:
            shopping_list.setdefault("type", "shopping")
        return data

    @staticmethod
    def _now():
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _summary(shopping_list):
        items = shopping_list.get("items", [])
        return {
            "id": shopping_list["id"],
            "name": shopping_list["name"],
            "type": shopping_list.get("type", "shopping"),
            "item_count": len(items),
            "created_at": shopping_list.get("created_at"),
            "updated_at": shopping_list.get("updated_at"),
        }

    @staticmethod
    def _find_list(store, list_id):
        shopping_list = next(
            (item for item in store["lists"] if item["id"] == list_id),
            None,
        )
        if shopping_list is None:
            raise KeyError(f"Shopping list '{list_id}' was not found.")
        return shopping_list

    def read_lists(self):
        _, store = self._get_file()
        return [self._summary(item) for item in store["lists"]]

    def read(self, list_id=None):
        _, store = self._get_file()
        if list_id is None:
            if not store["lists"]:
                return None
            return store["lists"][0]
        return self._find_list(store, list_id)

    def create_list(self, name, list_type="shopping"):
        clean_name = " ".join(str(name or "").split())
        if not clean_name:
            raise ValueError("List name is required.")
        if len(clean_name) > 80:
            raise ValueError("List name must be 80 characters or fewer.")
        if list_type not in ("shopping", "todo"):
            raise ValueError("List type must be 'shopping' or 'todo'.")

        file_ref, store = self._get_file()
        now = self._now()
        shopping_list = {
            "id": uuid4().hex,
            "name": clean_name,
            "type": list_type,
            "created_at": now,
            "updated_at": now,
            "items": [],
        }
        store["lists"].append(shopping_list)
        self._save(file_ref, store, f"feat: create list {clean_name}")
        return shopping_list

    def rename_list(self, list_id, name):
        clean_name = " ".join(str(name or "").split())
        if not clean_name:
            raise ValueError("List name is required.")
        if len(clean_name) > 80:
            raise ValueError("List name must be 80 characters or fewer.")

        file_ref, store = self._get_file()
        shopping_list = self._find_list(store, list_id)
        shopping_list["name"] = clean_name
        shopping_list["updated_at"] = self._now()
        self._save(file_ref, store, f"feat: rename list to {clean_name}")
        return shopping_list

    def delete_list(self, list_id):
        file_ref, store = self._get_file()
        self._find_list(store, list_id)
        store["lists"] = [
            item for item in store["lists"] if item["id"] != list_id
        ]
        self._save(file_ref, store, "feat: delete shopping list")

    def _save(self, file_ref, store, message):
        self.repo.update_file(
            self.path,
            message,
            json.dumps(store, indent=2),
            file_ref.sha,
        )

    def dispatch(self, message, list_id):
        try:
            _, store = self._get_file()
            current_list = self._find_list(store, list_id)
            list_type = current_list.get("type", "shopping")
            intent = self.brain.interpret(
                message,
                context=current_list,
                list_type=list_type,
            )
            action = intent.get("action", "ERROR")
            val = intent.get("value")
            conf = intent.get("confirmation", "Processed.")

            if action == "READ":
                return self._format_response(current_list, conf, "READ")
            if action == "DELETE":
                targets = val if isinstance(val, list) else [val]
                data = self.delete_item(list_id, targets)
                return self._format_response(data, conf, "DELETE")
            if action == "ADD":
                data = self.add_items(list_id, val)
                return self._format_response(data, conf, "ADD")
            if action == "CLEAR":
                data = self.clear_list(list_id)
                return self._format_response(data, conf, "CLEAR")
            if list_type == "todo" and action in ("COMPLETE", "REOPEN"):
                data = self.set_task_status(list_id, val, action == "COMPLETE")
                return self._format_response(data, conf, action)
            if list_type == "todo" and action == "UPDATE":
                data = self.update_tasks(list_id, val)
                return self._format_response(data, conf, action)
            if action == "HELP":
                return {
                    "type": "help",
                    "payload": [],
                    "meta": {
                        "action": "HELP",
                        "message": conf,
                        "list_type": list_type,
                    },
                }
            return {"type": "error", "payload": f"Unhandled action: {action}"}
        except Exception as e:
            Logger.info(f"[Engine] Crash: {str(e)}")
            return {"type": "error", "payload": f"Internal Error: {str(e)}"}

    def _format_response(self, data, message, action):
        return {
            "type": "table",
            "payload": data.get("items", []),
            "meta": {
                "action": action,
                "message": message,
                "list_type": data.get("type", "shopping"),
            }
        }

    def delete_item(self, list_id, val):
        file_ref, store = self._get_file()
        data = self._find_list(store, list_id)
        targets = [
            str(
                target.get("id")
                or target.get("title")
                or target.get("name")
            ).lower()
            if isinstance(target, dict)
            else str(target).lower()
            for target in val
            if target is not None
        ]
        data["items"] = [
            item for item in data["items"]
            if str(item["id"]).lower() not in targets
            and str(item.get("title") or item.get("name", "")).lower()
            not in targets
        ]
        data["updated_at"] = self._now()
        self._save(file_ref, store, "fix: remove items")
        return data

    def add_items(self, list_id, items_list):
        if not items_list:
            return self.read(list_id)
        file_ref, store = self._get_file()
        data = self._find_list(store, list_id)
        for item in items_list:
            ids = [i["id"] for i in data["items"]]
            next_id = max(ids) + 1 if ids else 1
            if data.get("type") == "todo":
                priority = item.get("priority")
                if priority not in (None, "low", "medium", "high"):
                    priority = None
                data["items"].append({
                    "id": next_id,
                    "title": item.get("title", "Untitled task"),
                    "notes": item.get("notes", ""),
                    "priority": priority,
                    "due_at": item.get("due_at"),
                    "status": "pending",
                    "completed_at": None,
                })
            else:
                quantity = item.get("quantity")
                unit = item.get("unit", "")
                notes = item.get("notes", "")
                metadata = notes
                if quantity is not None:
                    metadata = f"{quantity} {unit}".strip()
                    if notes:
                        metadata = f"{metadata} — {notes}"
                data["items"].append({
                    "id": next_id,
                    "name": item.get("name", "Unknown"),
                    "quantity": quantity,
                    "unit": unit,
                    "metadata": metadata,
                    "category": item.get("category", "Other"),
                    "status": "pending"
                })
        data["updated_at"] = self._now()
        self._save(file_ref, store, "feat: add items")
        return data

    def clear_list(self, list_id):
        file_ref, store = self._get_file()
        data = self._find_list(store, list_id)
        data["items"] = []
        data["updated_at"] = self._now()
        self._save(file_ref, store, "feat: clear list")
        return data

    @staticmethod
    def _task_matches(task, target):
        if isinstance(target, dict):
            target = target.get("id") or target.get("title")
        if target is None:
            return False
        normalized = str(target).lower()
        return (
            str(task.get("id")).lower() == normalized
            or str(task.get("title", "")).lower() == normalized
        )

    def set_task_status(self, list_id, targets, completed):
        file_ref, store = self._get_file()
        data = self._find_list(store, list_id)
        if data.get("type") != "todo":
            raise ValueError("Task status is only available for TODO lists.")

        target_list = targets if isinstance(targets, list) else [targets]
        now = self._now()
        for task in data["items"]:
            if any(
                self._task_matches(task, target)
                for target in target_list
            ):
                task["status"] = "completed" if completed else "pending"
                task["completed_at"] = now if completed else None
        data["updated_at"] = now
        self._save(file_ref, store, "feat: update task status")
        return data

    def update_tasks(self, list_id, updates):
        file_ref, store = self._get_file()
        data = self._find_list(store, list_id)
        if data.get("type") != "todo":
            raise ValueError("Task updates are only available for TODO lists.")

        update_list = updates if isinstance(updates, list) else [updates]
        for update in update_list:
            if not isinstance(update, dict):
                continue
            for task in data["items"]:
                if not self._task_matches(task, update):
                    continue
                for field in ("title", "notes", "due_at"):
                    if field in update:
                        task[field] = update[field]
                if (
                    "priority" in update
                    and update["priority"] in (None, "low", "medium", "high")
                ):
                    task["priority"] = update["priority"]
        data["updated_at"] = self._now()
        self._save(file_ref, store, "feat: update tasks")
        return data
