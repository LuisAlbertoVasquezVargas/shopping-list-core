# api/index.py

from http.server import BaseHTTPRequestHandler
import os
import json
from urllib.parse import urlparse
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
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _body(self):
        length = int(self.headers.get('Content-Length', 0))
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length))

    def _route(self):
        return [part for part in urlparse(self.path).path.split('/') if part]

    def _handle_error(self, error):
        if isinstance(error, KeyError):
            self._respond(404, {"error": str(error).strip("'")})
        elif isinstance(error, (ValueError, json.JSONDecodeError)):
            self._respond(400, {"error": str(error)})
        else:
            Logger.error("HTTP Handler", str(error))
            self._respond(500, {"error": "Internal server error."})

    def do_OPTIONS(self):
        self._respond(204, {})

    def do_POST(self):
        try:
            route = self._route()
            body = self._body()
            engine = self._get_engine()
            if route == ["api", "lists"]:
                shopping_list = engine.create_list(
                    body.get("name"),
                    body.get("type", "shopping"),
                )
                self._respond(201, {"list": shopping_list})
                return
            if route == ["api", "chat"]:
                list_id = body.get("list_id")
                if not list_id:
                    raise ValueError("list_id is required.")
                res = engine.dispatch(body.get("message", ""), list_id)
                self._respond(200, {"success": True, "result": res})
                return
            self._respond(404, {"error": "Endpoint not found."})
        except Exception as error:
            self._handle_error(error)

    def do_GET(self):
        try:
            route = self._route()
            engine = self._get_engine()
            if route == ["api", "lists"]:
                self._respond(200, {"lists": engine.read_lists()})
                return
            if len(route) == 3 and route[:2] == ["api", "lists"]:
                self._respond(200, {"list": engine.read(route[2])})
                return
            if route == ["api", "chat"]:
                self._respond(200, {"status": "online", "lists": engine.read_lists()})
                return
            self._respond(404, {"error": "Endpoint not found."})
        except Exception as error:
            self._handle_error(error)

    def do_PATCH(self):
        try:
            route = self._route()
            if len(route) != 3 or route[:2] != ["api", "lists"]:
                self._respond(404, {"error": "Endpoint not found."})
                return
            shopping_list = self._get_engine().rename_list(
                route[2],
                self._body().get("name"),
            )
            self._respond(200, {"list": shopping_list})
        except Exception as error:
            self._handle_error(error)

    def do_DELETE(self):
        try:
            route = self._route()
            if len(route) != 3 or route[:2] != ["api", "lists"]:
                self._respond(404, {"error": "Endpoint not found."})
                return
            self._get_engine().delete_list(route[2])
            self._respond(200, {"success": True})
        except Exception as error:
            self._handle_error(error)
