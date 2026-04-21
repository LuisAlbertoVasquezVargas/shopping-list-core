# api/chat.py

from http.server import BaseHTTPRequestHandler
import os
import json
from core.engine import Engine

class handler(BaseHTTPRequestHandler):
    selected_model = "gemini-2.0-flash-lite"

    def _get_engine(self):
        return Engine(
            os.environ.get('GH_TOKEN'),
            os.environ.get('GH_OWNER'),
            os.environ.get('GH_REPO'),
            model_name=self.selected_model
        )

    def _respond(self, code, data):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_GET(self):
        try:
            self._respond(200, {"status": "online", "list": self._get_engine().read()})
        except Exception as e:
            self._respond(500, {"error": str(e)})

    def do_POST(self):
        try:
            length = int(self.headers['Content-Length'])
            body = json.loads(self.rfile.read(length))
            res = self._get_engine().dispatch(body.get("message", ""))
            self._respond(200, {"success": True, "result": res})
        except Exception as e:
            print(f"CRITICAL: Handler Error: {str(e)}")
            self._respond(500, {"error": str(e)})
