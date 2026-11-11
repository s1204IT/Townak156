#!/usr/bin/env python3
import http.server, os, ssl, urllib.request

CERT = "certs/fullchain.pem"
KEY = "certs/leaf.key"
APK = "apk/TouchSetupLogin.apk"
PORT = 8443
NAME = "TouchSetupLogin.apk"
APK_URL = "https://github.com/Kobold831/SetupLogin/releases/download/open/TouchSetupLogin.apk"

def ensure_apk():
    if os.path.exists(APK):
        return
    os.makedirs(os.path.dirname(APK) or ".", exist_ok=True)
    urllib.request.urlretrieve(APK_URL, APK)

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.split("?")[0].endswith(NAME):
            ensure_apk()
            data = open(APK, "rb").read()
            self.send_response(200)
            self.send_header("Content-Type", "application/vnd.android.package-archive")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        else:
            body = b"ok\n"
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    def log_message(self, fmt, *args):
        print("%s %s" % (self.address_string(), fmt % args), flush=True)

def main():
    ensure_apk()
    srv = http.server.HTTPServer(("0.0.0.0", PORT), Handler)
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(CERT, KEY)
    srv.socket = ctx.wrap_socket(srv.socket, server_side=True)
    srv.serve_forever()

if __name__ == "__main__":
    main()
