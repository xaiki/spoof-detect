#!/usr/bin/python
import http.server
import ssl
import threading

def launch_httpd(httpd):
    print(f'launch {httpd.socket}')
    httpd.serve_forever()

def make_httpd(port):
    return http.server.HTTPServer(('0.0.0.0', port), http.server.SimpleHTTPRequestHandler)

[httpd, httpsd] = [make_httpd(p) for p in [8080, 8443]]

ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ctx.load_cert_chain('./cert.pem', keyfile='./privatekey.pem')
ctx.check_hostname = False

httpsd.socket = ctx.wrap_socket(sock=httpsd.socket, server_side=True)

for h in [httpd, httpsd]:
    t = threading.Thread(target=launch_httpd, args=(h,))
    t.start()

