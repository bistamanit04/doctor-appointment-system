from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from router import Router
from config import HOST,PORT


class Myserver(BaseHTTPRequestHandler):


    def do_GET(self):
        Router.handle_get(self)

    def do_POST(self):
        Router.handle_post(self)

   


server = ThreadingHTTPServer((HOST, PORT), Myserver)
print(f"server running at http://{HOST}:{PORT}")
server.serve_forever()

