# manage.py

import sys
from http.server import HTTPServer
from dotenv import load_dotenv
from api.chat import handler

def run_server():
    load_dotenv()
    port = 8000
    server_address = ('localhost', port)
    httpd = HTTPServer(server_address, handler)
    
    print(f"--- Shopping List Core Management ---")
    print(f"Local development server active at http://localhost:{port}")
    print(f"Ready to handle GET, POST, PUT, DELETE...")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")

def main():
    if len(sys.argv) < 2:
        print("Usage: python manage.py [runserver]")
        return

    command = sys.argv[1]

    if command == "runserver":
        run_server()
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
