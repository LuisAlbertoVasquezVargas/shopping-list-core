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
