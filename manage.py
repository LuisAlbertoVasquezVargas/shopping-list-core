# manage.py

import sys
import argparse
from http.server import HTTPServer
from dotenv import load_dotenv
from api.chat import handler
from core.logger import Logger
import os

DEFAULT_MODEL_SIZE = "tiny"

# Optimized for 2026 Free Tier: 2.5 Flash-Lite offers the highest RPM (15)
MODEL_MAP = {
    "tiny": "gemini-2.5-flash-lite",
    "mini": "gemini-2.5-flash-lite",
    "small": "gemini-2.5-flash",
    "medium": "gemini-3.1-flash-lite",
    "large": "gemini-3.1-pro-preview"
}

def run_server(size_key):
    load_dotenv()
    model_name = MODEL_MAP.get(size_key.lower(), MODEL_MAP[DEFAULT_MODEL_SIZE])
    handler.selected_model = model_name
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, handler)
    Logger.server(model_name)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["runserver", "list-models"])
    parser.add_argument("--size", default=DEFAULT_MODEL_SIZE)
    args, _ = parser.parse_known_args()
    if args.command == "runserver":
        run_server(args.size)
