# api/chat.py

from http.server import BaseHTTPRequestHandler
import os
import json
from core.engine import Engine

class handler(BaseHTTPRequestHandler):
    def _get_engine(self):
        return Engine(
            os.environ.get('GH_TOKEN'),
            os.environ.get('GH_OWNER'),
            os.environ.get('GH_REPO')
        )

    def _respond(self, code, data):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _get_body(self):
        length = int(self.headers['Content-Length'])
        return json.loads(self.rfile.read(length))

    def do_GET(self):
        try:
            self._respond(200, {"status": "core_online", "current_list": self._get_engine().read()})
        except Exception as e:
            self._respond(500, {"error": str(e)})

    def do_POST(self):
        try:
            body = self._get_body()
            item = self._get_engine().add_item(body.get("item"))
            self._respond(200, {"success": True, "added": item})
        except Exception as e:
            self._respond(500, {"error": str(e)})

    def do_PUT(self):
        try:
            body = self._get_body()
            self._get_engine().update_item(body.get("id"), body.get("status", "bought"))
            self._respond(200, {"success": True})
        except Exception as e:
            self._respond(500, {"error": str(e)})

    def do_DELETE(self):
        try:
            body = self._get_body()
            self._get_engine().delete_item(body.get("id"))
            self._respond(200, {"success": True})
        except Exception as e:
            self._respond(500, {"error": str(e)})
