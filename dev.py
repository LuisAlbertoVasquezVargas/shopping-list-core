# dev.py

from http.server import HTTPServer
from dotenv import load_dotenv
from api.chat import handler

def run_development_server():
    load_dotenv()
    
    server_address = ('localhost', 8000)
    httpd = HTTPServer(server_address, handler)
    
    print(f"--- Shopping List Core ---")
    print(f"Local server active at: http://localhost:8000")
    print(f"Streaming api/chat.py logic...")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")

if __name__ == "__main__":
    run_development_server()
