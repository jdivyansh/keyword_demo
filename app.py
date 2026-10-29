import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?")[0]
        status = 200

        if path == "/":
            response = {
                "service": "devx-demo",
                "version": os.getenv("APP_VERSION", "v1"),
                "message": "Hello from the developer platform!"
            }
        elif path in ("/healthz", "/readyz"):
            response = {"status": "healthy"}
        elif path == "/work":
            status = 500 if os.getenv("FAIL_MODE", "0") == "1" else 200
            response = {
                "status": "error" if status == 500 else "success"
            }
        else:
            status = 404
            response = {"error": "Not found"}

        body = json.dumps(response).encode()

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    print("Service running at http://localhost:8080", flush=True)
    server = ThreadingHTTPServer(("0.0.0.0", 8080), Handler)
    server.serve_forever()