from http.server import BaseHTTPRequestHandler, HTTPServer
import sqlite3
import socket
import os
import json

from localchess import LocalChess

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

HOST_NAME = get_local_ip()
PORT = 6969

data_manager = LocalChess()


class ChessServer(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.has_clock_user = False
        super().__init__(*args, **kwargs)

    def send_404(self):
        self.send_response(404)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(b"Not found")

    def send_html_response(self, html_file_name):
        with open(html_file_name, "rb") as f:
            content = f.read()

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(content)

    def send_css_response(self, css_file_name):
        with open(css_file_name, "rb") as f:
            content = f.read()

        self.send_response(200)
        self.send_header("Content-Type", "text/css")
        self.end_headers()
        self.wfile.write(content)

    def send_js_response(self, js_file_name):
        with open(js_file_name, "rb") as f:
            content = f.read()

        self.send_response(200)
        self.send_header("Content-Type", "text/javascript")
        self.end_headers()
        self.wfile.write(content)

    def send_text(self, s: str):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(s.encode("utf-8"))

    def send_json_response(self, data):
        data_bytes = json.dumps(data).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(data_bytes)

    def do_GET(self):

        if self.path == "/":
            user_agent = self.headers.get("User-Agent")
            if "Mobile" in user_agent: #type: ignore
                return self.send_html_response("html/mobile/mobile.html")
            else:
                return self.send_html_response("html/host/host.html")

        elif self.path == "/html/host/style.css":
            return self.send_css_response("html/host/style.css")

        elif self.path == "/html/host/script.js":
            return self.send_css_response("html/host/script.js")

        elif self.path == "/html/mobile/style.css":
            return self.send_css_response("html/mobile/style.css")

        elif self.path == "/clock":
            return self.send_html_response("html/clock/clock.html")

        elif self.path == "/html/clock/style.css":
            return self.send_css_response("html/clock/style.css")

        elif self.path == "/html/clock/script.js":
            return self.send_js_response("html/clock/script.js")

        elif self.path == "/html/common/utils.js":
            return self.send_js_response("html/common/utils.js")

        elif self.path == "/favicon.ico":
            self.send_response(200)
            with open("favicon.ico", "rb") as f:
                self.wfile.write(f.read())

        else:
            return self.send_404()

    def do_POST(self):
        if self.path == "/players":
            return self.send_json_response(data_manager.get_players())
        elif self.path == "/register_result":
            try:
                content_length = int(self.headers.get("Content-Length")) #pyright: ignore
                body_bytes = self.rfile.read(content_length)
                json_body = json.loads(body_bytes)
                data_manager.register_result(
                    json_body["white"],
                    json_body["black"],
                    json_body["result"]
                )
                self.send_response(200)
            except:
                self.send_response(400) # Bad request
        return self.send_404()

if __name__ == "__main__":
    chess_server = HTTPServer((HOST_NAME, PORT), ChessServer)
    print(f"Chess server started http://{HOST_NAME}:{PORT}")

    try:
        chess_server.serve_forever()
    except KeyboardInterrupt:
        pass

    chess_server.server_close()
    print("Bye")
