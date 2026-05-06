# api/chat.py

from http.server import BaseHTTPRequestHandler
import os
import json
from core.engine import Engine
from core.logger import Logger

class handler(BaseHTTPRequestHandler):
    def _get_engine(self):
        model = os.environ.get('SELECTED_MODEL', 'gemini-2.5-flash-lite')
        return Engine(
            os.environ.get('GH_TOKEN'),
            os.environ.get('GH_OWNER'),
            os.environ.get('GH_REPO'),
            model_name=model
        )

    def _respond(self, code, data):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length))
            res = self._get_engine().dispatch(body.get("message", ""))
            self._respond(200, {"success": True, "result": res})
        except Exception as e:
            Logger.error("HTTP Handler", str(e))
            self._respond(500, {"error": str(e)})

    def do_GET(self):
        try:
            self._respond(200, {"status": "online", "list": self._get_engine().read()})
        except Exception as e:
            Logger.error("HTTP Handler", str(e))
            self._respond(500, {"error": str(e)})
