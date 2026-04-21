# manage.py

import sys
import argparse
from http.server import HTTPServer
from dotenv import load_dotenv
from api.chat import handler

MODEL_MAP = {
    "small": "gemini-1.5-flash-8b",
    "medium": "gemini-1.5-flash",
    "large": "gemini-2.0-flash",
    "ultra": "gemini-1.5-pro"
}

def run_server(size_key):
    load_dotenv()
    model_name = MODEL_MAP.get(size_key.lower(), size_key)
    handler.selected_model = model_name
    
    server_address = ('', 8000) # Use empty string to bind to all interfaces
    httpd = HTTPServer(server_address, handler)
    print(f"--- Shopping List Core ---")
    print(f"Endpoint: http://localhost:8000")
    print(f"Model:    {model_name}")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")

if __name__ == "__main__":
    # If no args at all, print usage and exit
    if len(sys.argv) == 1:
        print("Usage: python manage.py runserver [--size small|medium|large|ultra]")
        sys.exit(0)

    parser = argparse.ArgumentParser()
    parser.add_argument("command", help="Command to run (runserver)")
    parser.add_argument("--size", default="large", help="Model size nickname")
    
    # Use parse_known_args to prevent crashes from weird shell flags
    args, unknown = parser.parse_known_args()
    
    if args.command == "runserver":
        run_server(args.size)
    else:
        print(f"Unknown command: {args.command}")
