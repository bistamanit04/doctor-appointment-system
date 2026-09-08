from template_engine import TemplateEngine
from database import get_connection

class HomeController:
   
   @staticmethod
   def index(request):
      connection=get_connection()
      cursor =connection.cursor()
      cursor.execute("""
               SELECT doctor_id,name,specialization
               FROM doctor 
               ORDER by doctor_id DESC
               limit 3
               """)
      
      doctors=cursor.fetchall()
      connection.close()
      
      TemplateEngine.render(
         request,
         "index.html",
         {
            "title":"doctor appointment system",
            "username":"Guest",
            "doctors": doctors
         }
      )