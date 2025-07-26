import http.server
import socketserver
import argparse
from pathlib import Path

DEFAULT_PORT = 8000

# Serve files relative to repository root
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

class Handler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path: str) -> str:
        # Serve metadata and narrative from examples/output
        if path.startswith('examples/output'):
            return str(ROOT / path.lstrip('/'))
        # Otherwise serve from frontend directory
        return str(HERE / path.lstrip('/'))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Simple HTTP server for the demo frontend")
    parser.add_argument('--port', type=int, default=DEFAULT_PORT, help='Port to listen on')
    args = parser.parse_args()
    port = args.port

    with socketserver.TCPServer(('', port), Handler) as httpd:
        print(f"Serving on http://localhost:{port}")
        httpd.serve_forever()
