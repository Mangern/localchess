from http.server import BaseHTTPRequestHandler, HTTPServer
import sqlite3
import socket

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

HOST_NAME = get_local_ip()
PORT = 6969

class ChessServer(BaseHTTPRequestHandler):
    def do_GET(self):
        user_agent = self.headers.get("User-Agent")

        if "Mobile" in user_agent:
            return self.do_get_mobile()


        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(b"Heii")

    def do_get_mobile(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(b"You on mobile huh")


if __name__ == "__main__":
    chess_server = HTTPServer((HOST_NAME, PORT), ChessServer)
    print(f"Chess server started http://{HOST_NAME}:{PORT}")

    try:
        chess_server.serve_forever()
    except KeyboardInterrupt:
        pass

    chess_server.server_close()
    print("Bye")
