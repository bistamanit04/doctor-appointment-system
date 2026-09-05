from template_engine import TemplateEngine
from database import get_connection

class DoctorController:
    @staticmethod
    def DOClist(request):
        
        connection=get_connection()
        cursor=connection.cursor()
        
        cursor.execute("""
                       select doctor_id, name,specialization,email,phone 
                       FROM doctor
                       ORDER by name
        """)
        doctors= cursor.fetchall()
        connection.close()
        
        TemplateEngine.render(
            request,
            "FindDoctor.html",
            {
                "title":"FIND UR DOCTOR",
                "doctors":doctors
            }
        )  