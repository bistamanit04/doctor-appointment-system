from template_engine import TemplateEngine
from database import get_connection


class DocProfile:

    @staticmethod
    def profile(request, doctor_id):

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT doctor_id, name, specialization, email, phone, status
            FROM doctor
            WHERE doctor_id = ?
        """, (doctor_id,))

        doctor = cursor.fetchone()

        connection.close()

        if not doctor:
            request.send_response(404)
            request.send_header(
                "Content-Type",
                "text/html"
            )
            request.end_headers()

            request.wfile.write(
                b"<h1>Doctor not found.</h1>"
            )

            return

        TemplateEngine.render(
            request,
            "DocProf.html",
            {
                "title": "Doctor Profile",
                "doctor_id": doctor[0],
                "name": doctor[1],
                "specialization": doctor[2],
                "email": doctor[3],
                "phone": doctor[4],
                "status": doctor[5]
            }
        )