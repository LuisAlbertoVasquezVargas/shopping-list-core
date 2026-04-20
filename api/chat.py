# api/chat.py

from http.server import BaseHTTPRequestHandler
from github import Github
import os
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        token = os.environ.get('GH_TOKEN')
        owner = os.environ.get('GH_OWNER')
        repo_name = os.environ.get('GH_REPO')

        if not all([token, owner, repo_name]):
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"Error: Missing environment configuration")
            return

        try:
            g = Github(token)
            repo = g.get_repo(f"{owner}/{repo_name}")
            file_content = repo.get_contents("data/active_list.json")
            data = json.loads(file_content.decoded_content.decode())

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            response = {
                "status": "core_online",
                "database": repo_name,
                "current_list": data
            }
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def do_POST(self):
        token = os.environ.get('GH_TOKEN')
        owner = os.environ.get('GH_OWNER')
        repo_name = os.environ.get('GH_REPO')

        try:
            # 1. Parse incoming JSON body
            content_length = int(self.headers['Content-Length'])
            post_data = json.loads(self.rfile.read(content_length))
            new_item_name = post_data.get("item")

            # 2. Connect to GitHub and get current file (and its SHA)
            g = Github(token)
            repo = g.get_repo(f"{owner}/{repo_name}")
            file_ref = repo.get_contents("data/active_list.json")
            current_data = json.loads(file_ref.decoded_content.decode())

            # 3. Update the data structure
            new_item = {
                "id": len(current_data["items"]) + 1,
                "name": new_item_name,
                "status": "pending"
            }
            current_data["items"].append(new_item)
            current_data["last_updated"] = "2026-04-20" # Static for now, can use datetime later

            # 4. Commit change back to GitHub
            repo.update_file(
                file_ref.path,
                f"feat: add {new_item_name} via core",
                json.dumps(current_data, indent=2),
                file_ref.sha
            )

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "added": new_item_name}).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
