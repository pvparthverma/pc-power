from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import sys
import logging

# --- Conditionally Configure Logging or Printing ---
IS_WINDOWLESS = sys.executable.endswith("pythonw.exe")

if IS_WINDOWLESS:
    # We're running in the background, so log to a file
    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'server.log')
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    # Define a logger function that matches the print signature
    log = logging.info
else:
    # We're running in a console, so just use the print function
    log = print
# ----------------------------------------------------

secret_key = "REPLACE THIS WITH WHATEVER YOU WANT"

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

        log(f"Received request with power='{power}'.")

        if key != secret_key:
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b"Forbidden")
            if IS_WINDOWLESS:
                logging.warning("Request rejected: Invalid secret key.")
            else:
                log("Request rejected: Invalid secret key.")
            return

        # Decide action
        if power == "shutdown":
            command = "shutdown /s /t 0"
        elif power == "restart":
            command = "shutdown /r /t 0"
        elif power == "sleep":
            command = "rundll32.exe powrprof.dll,SetSuspendState 0,1,0"
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
        log(f"Executing command: {command}")
        os.system(command)

def run_server():
    server_address = ("0.0.0.0", 8080)
    httpd = HTTPServer(server_address, PowerHandler)
    log("Listening for power requests on port 8080...")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
