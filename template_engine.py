import os 
from config import TEMPLATE_DIR

class TemplateEngine:

    @staticmethod 
    def render(request,template_name,context=None):
        
        if context is None:
            context={}
        
        file_path= os.path.join(TEMPLATE_DIR,template_name)

        with open(file_path,"r",encoding="utf-8") as file:
            html = file.read()
        
        for key,value in context.items():
            html=html.replace("{{" + key + "}}",str(value))
        

        request.send_response(200)
        request.send_header("content-type","text/html")
        request.end_headers()

        request.wfile.write(html.encode("utf-8"))