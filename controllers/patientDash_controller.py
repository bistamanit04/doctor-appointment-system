from database import get_connection
from template_engine import TemplateEngine
from session import get_session


class  patientController:

    @staticmethod
    def dashboard(request):

        cookie = request.headers.get("Cookie", "")

        session_id = None

        for item in cookie.split(";"):
            if item.strip().startswith("session_id="):
                session_id = item.strip().split("=", 1)[1]

        session = get_session(session_id)

        if not session:
            request.send_response(302)
            request.send_header("Location", "/login")
            request.end_headers()
            return

        patient_id = session["user_id"]

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
             SELECT name, email, phone
             FROM patient
            WHERE patient_id = ?
            """, (patient_id,))

        patient = cursor.fetchone()

        connection.close()
        if not patient:
            request.send_response(404)
            request.send_header("Content-Type", "text/html")
            request.end_headers()
            request.wfile.write(
                 b"<h1>Patient not found.</h1>"
          )
            return

        TemplateEngine.render(
        request,
        "patientDashboard.html",
        {
            "title": "Patient Dashboard",
            "patient_id": patient_id,
            "name": patient[0],
            "email": patient[1],
            "phone": patient[2]
            }
            )




