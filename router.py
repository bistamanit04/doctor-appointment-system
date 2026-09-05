from controllers.home_controller import HomeController
from controllers.static_controller import StaticController
from controllers.register_controller import RegisterController
from controllers.login_controller import LoginController
from controllers.patientDash_controller import patientController
from controllers.docdash_controller import DoctorDashController
from controllers.FindDoctor_controller import DoctorController
from controllers.DocProfile_controller import DocProfile
class Router:
    @staticmethod
    
    def handle_get(request):
         
        print("REQUEST PATH:", request.path)
 
        
        if request.path.startswith("/static/"):
            StaticController.serve(request)
            return
        
           # Dynamic doctor profile
        if request.path.startswith("/docprofile/"):
            doctor_id = request.path.replace(
                "/docprofile/",
                "",
                1
            )
            if doctor_id.isdigit():
                DocProfile.profile(
                    request,
                    int(doctor_id)
                )
                return
            Router.not_found(request)
            return
        
        
        
      
        routes={
              "/": HomeController.index,
              "/register":RegisterController.show,
              "/login":LoginController.show,
              "/patient/dashboard":patientController.dashboard,
              "/doctor/dashboard":DoctorDashController.dashboard,
              "/doctors":DoctorController.DOClist,
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