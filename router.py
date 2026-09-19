from controllers.home_controller import HomeController
from controllers.static_controller import StaticController
from controllers.register_controller import RegisterController
from controllers.login_controller import LoginController
from controllers.patientDash_controller import patientController
from controllers.docdash_controller import DoctorDashController
from controllers.FindDoctor_controller import DoctorController
from controllers.DocProfile_controller import DocProfile
from urllib.parse import urlparse, parse_qs
from controllers.docbio_controller import DoctorBioController
from controllers.adminLogin_controller import AdminLoginController
from controllers.adminDash_controller import AdminDashboardController
from controllers.admin_doc_controller import AdminDoctorController


class Router:

    @staticmethod
    def handle_get(request):

        parsed = urlparse(request.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        request.query = query

        print("REQUEST PATH:", path, "| QUERY:", query)

        if path.startswith("/static/"):
            StaticController.serve(request)
            return

        # Dynamic doctor profile
        if path.startswith("/docprofile/"):
            doctor_id = path.replace(
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

        routes = {
            "/": HomeController.index,
            "/register": RegisterController.show,
            "/login": LoginController.show,
            "/patient/dashboard": patientController.dashboard,
            "/doctor/dashboard": DoctorDashController.dashboard,
            "/doctors": DoctorController.DOClist,
            "/doctor/profile":DoctorBioController.show,
            "/admin/login":AdminLoginController.show,
            "/admin/dashboard":AdminDashboardController.dashboard,
            
        }

        handler = routes.get(path)

        if handler:
            handler(request)
        else:
            Router.not_found(request)

    @staticmethod
    def handle_post(request):

        parsed = urlparse(request.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        request.query = query

        routes = {
            "/register": RegisterController.register,
            "/login": LoginController.login,
            "/doctor/profile/save":DoctorBioController.save,
            "/admin/login":AdminLoginController.login,
            "/admin/doctor/certify":AdminDoctorController.certify,
            "/admin/doctor/reject":AdminDoctorController.reject,
            
        }

        handler = routes.get(path)

        if handler:
            handler(request)
        else:
            Router.not_found(request)

    @staticmethod
    def not_found(request):
        request.send_response(404)
        request.send_header("content-type", "text/html")
        request.end_headers()

        request.wfile.write(b"<h1> 404 page not found</h1>")