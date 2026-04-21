# manage.py

import sys
import argparse
import os
from http.server import HTTPServer
from dotenv import load_dotenv
from api.chat import handler
from core.logger import Logger

MODEL_MAP = {
    "tiny": "gemini-2.5-flash-lite",
    "small": "gemini-3-flash-preview",
    "medium": "gemini-3.1-flash-lite-preview",
    "large": "gemini-3.1-pro-preview"
}

def run_server(size_key):
    load_dotenv()
    model_name = MODEL_MAP.get(size_key.lower(), MODEL_MAP["tiny"])
    handler.selected_model = model_name
    
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, handler)
    
    Logger.info(f"[System] Starting Shopping List Core | Model: {model_name}")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        Logger.info("[System] Shutdown signal received.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["runserver", "list-models"])
    parser.add_argument("--size", default="tiny")
    args, _ = parser.parse_known_args()
    
    if args.command == "runserver":
        run_server(args.size)
    elif args.command == "list-models":
        for key, model in MODEL_MAP.items():
            Logger.info(f"[Config] {key}: {model}")
