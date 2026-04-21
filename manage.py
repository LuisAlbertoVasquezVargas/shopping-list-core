# manage.py

import sys
import argparse
from http.server import HTTPServer
from dotenv import load_dotenv
from api.chat import handler
from google import genai
import os

MODEL_MAP = {
    "small": "gemini-2.0-flash-lite",
    "medium": "gemini-2.5-flash",
    "large": "gemini-3-flash-preview",
    "ultra": "gemini-3.1-pro-preview"
}

def list_available_models():
    load_dotenv()
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    print("\n[DISCOVERY] Available models for your key:")
    try:
        for model in client.models.list():
            print(f"  > {model.name}")
    except Exception as e:
        print(f"  FAILED to list: {e}")
    print("")

def run_server(size_key):
    load_dotenv()
    model_name = MODEL_MAP.get(size_key.lower(), size_key)
    handler.selected_model = model_name
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, handler)
    print(f"--- Shopping List Core ---")
    print(f"Server: http://localhost:8000 | Model: {model_name}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["runserver", "list-models"])
    parser.add_argument("--size", default="small")
    args, _ = parser.parse_known_args()
    if args.command == "list-models":
        list_available_models()
    elif args.command == "runserver":
        run_server(args.size)
