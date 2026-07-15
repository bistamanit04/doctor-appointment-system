from template_engine import TemplateEngine


class HomeController:

    @staticmethod
    def index(request):

        
     TemplateEngine.render(
        request,
        "index.html",
        {
           "title":"doctor appointment system",
           "username":"Guest"
        }
        )