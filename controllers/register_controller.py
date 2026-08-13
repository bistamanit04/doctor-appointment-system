from template_engine import TemplateEngine
class RegisterController:

    @staticmethod
    def show(request):
           TemplateEngine.render(
            request,
            "register.html",
            {
                "title": "Create Account"
            }
                )
   
    @staticmethod
    def register(request):

     print("REGISTER POST RECEIVED")

     content_length = int(
        request.headers.get("Content-Length", 0)
     )

     print("Content-Length:", content_length)

     data = request.rfile.read(content_length)

     print("DATA:", data)