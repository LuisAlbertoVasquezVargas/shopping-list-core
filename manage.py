# manage.py

import sys
from http.server import HTTPServer
from dotenv import load_dotenv
from api.chat import handler

def run_server():
    load_dotenv()
    server_address = ('localhost', 8000)
    httpd = HTTPServer(server_address, handler)
    print("Core Management: Server active at http://localhost:8000")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutdown.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "runserver":
        run_server()
    else:
        print("Usage: python manage.py runserver")
