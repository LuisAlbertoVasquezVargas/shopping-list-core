import json
import unittest
from unittest.mock import patch

from core.engine import Engine


class MissingFile(Exception):
    status = 404


class FileRef:
    def __init__(self, content, sha="sha"):
        self.decoded_content = content.encode()
        self.sha = sha


class FakeRepo:
    def __init__(self):
        self.files = {
            "data/active_list.json": {
                "version": "1.0",
                "items": [{"id": 1, "name": "milk", "status": "pending"}],
            }
        }

    def get_contents(self, path):
        if path not in self.files:
            raise MissingFile()
        return FileRef(json.dumps(self.files[path]))

    def create_file(self, path, _message, content):
        self.files[path] = json.loads(content)
        return {"content": FileRef(content)}

    def update_file(self, path, _message, content, _sha):
        self.files[path] = json.loads(content)


class FakeGithub:
    repo = FakeRepo()

    def __init__(self, _token):
        pass

    def get_repo(self, _name):
        return self.repo


class EngineTest(unittest.TestCase):
    def setUp(self):
        FakeGithub.repo = FakeRepo()
        github_patch = patch("core.engine.Github", FakeGithub)
        brain_patch = patch("core.engine.Brain")
        github_patch.start()
        brain_patch.start()
        self.addCleanup(github_patch.stop)
        self.addCleanup(brain_patch.stop)
        self.engine = Engine("token", "owner", "repo")

    def test_migrates_the_existing_list(self):
        lists = self.engine.read_lists()

        self.assertEqual(len(lists), 1)
        self.assertEqual(lists[0]["name"], "My shopping list")
        self.assertEqual(lists[0]["type"], "shopping")
        self.assertEqual(lists[0]["item_count"], 1)

    def test_crud_and_items_are_scoped_to_a_list(self):
        original = self.engine.read_lists()[0]
        friends = self.engine.create_list("Weekend with friends")

        self.engine.add_items(
            friends["id"],
            [{"name": "chips", "notes": "2 bags", "category": "Grocery"}],
        )
        self.engine.rename_list(friends["id"], "Movie night")

        self.assertEqual(self.engine.read(friends["id"])["name"], "Movie night")
        self.assertEqual(len(self.engine.read(friends["id"])["items"]), 1)
        self.assertEqual(len(self.engine.read(original["id"])["items"]), 1)

        self.engine.delete_list(friends["id"])
        self.assertEqual(len(self.engine.read_lists()), 1)

    def test_todo_tasks_have_separate_fields_and_actions(self):
        todo = self.engine.create_list("Work", "todo")
        self.engine.add_items(
            todo["id"],
            [{
                "title": "Prepare slides",
                "priority": "high",
                "due_at": "2026-07-28T17:00:00-05:00",
                "notes": "Quarterly review",
            }],
        )

        self.engine.set_task_status(
            todo["id"],
            [{"title": "Prepare slides"}],
            True,
        )
        self.engine.update_tasks(
            todo["id"],
            [{"id": 1, "priority": "low", "title": "Present slides"}],
        )

        task = self.engine.read(todo["id"])["items"][0]
        self.assertEqual(task["title"], "Present slides")
        self.assertEqual(task["priority"], "low")
        self.assertEqual(task["status"], "completed")
        self.assertIsNotNone(task["completed_at"])

    def test_rejects_blank_names_and_unknown_lists(self):
        with self.assertRaises(ValueError):
            self.engine.create_list("   ")
        with self.assertRaises(ValueError):
            self.engine.create_list("Invalid", "calendar")
        with self.assertRaises(KeyError):
            self.engine.read("missing")


if __name__ == "__main__":
    unittest.main()
