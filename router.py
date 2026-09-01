from controllers.home_controller import HomeController
from controllers.static_controller import StaticController
from controllers.register_controller import RegisterController
from controllers.login_controller import LoginController
class Router:
    @staticmethod
    def handle_get(request): 
        if request.path.startswith("/static/"):
            StaticController.serve(request)
            return
        
        routes={
              "/": HomeController.index,
              "/register":RegisterController.show,
              "/login":LoginController.show,
              }
        
        handler = routes.get(request.path)
        
        if handler:
            handler(request)
        else:
            Router.not_found(request)


    @staticmethod
    def handle_post(request):

     routes = {
        "/register": RegisterController.register,
        "/login": LoginController.login,
     }

     handler = routes.get(request.path)

     if handler:
      
        handler(request)
     else:
       
        Router.not_found(request)


 

    @staticmethod
    def not_found(request):   
        request.send_response(404)
        request.send_header("content-type","text/html")
        request.end_headers()
        
        request.wfile.write(b"<h1> 404 page not found</h1>")