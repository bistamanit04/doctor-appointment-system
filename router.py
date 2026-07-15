from controllers.home_controller import HomeController
from controllers.static_controller import StaticController
class Router:
    @staticmethod
    def handle_get(request): 
        if request.path.startswith("/static/"):
            StaticController.serve(request)
            return
        
        routes={
              "/": HomeController.index,
              }
        
        handler = routes.get(request.path)
        
        if handler:
            handler(request)
        else:
            Router.not_found(request)


    @staticmethod
    def handle_post(request):
        Router.not_found(request)

    @staticmethod
    def not_found(request):
        request.send_response(404)
        request.send_header("content-type","text/html")
        request.end_headers()
        
        request.wfile.write(b"<h1> 404 page not found</h1>")