from http.server import BaseHTTPRequestHandler, HTTPServer
import os

secret_key = ">:jNuC:Waw>yNv1bß1xf-#ElRjpX-#MVJIRWe°%1"

class PowerHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Get key header
        key = self.headers.get("key", "")
        
        # Read body (get 'power' value)
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode()
        
        # Extract power value
        power = ""
        for part in body.split("&"):
            if part.startswith("power="):
                power = part.split("=")[1].strip().lower()

        if key != secret_key:
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b"Forbidden")
            return

        # Decide action
        if power == "shutdown":
            command = "shutdown /s /t 0"   # Windows
        elif power == "restart":
            command = "shutdown /r /t 0"   # Windows
        elif power == "sleep":
            command = "rundll32.exe powrprof.dll,SetSuspendState 0,1,0"  # Windows sleep
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Invalid power option")
            return

        # Send response before executing command
        self.send_response(200)
        self.end_headers()
        self.wfile.write(f"Executing {power}".encode())

        # Run the command
        os.system(command)

def run_server():
    server_address = ("0.0.0.0", 8080)
    httpd = HTTPServer(server_address, PowerHandler)
    print("Listening for power requests...")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()