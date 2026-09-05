from database import get_connection
from template_engine import TemplateEngine
from session import get_session


class DoctorDashController:

    @staticmethod
    def dashboard(request):

        # Get session cookie
        cookie = request.headers.get("Cookie", "")

        session_id = None

        for item in cookie.split(";"):
            if item.strip().startswith("session_id="):
                session_id = item.strip().split("=", 1)[1]

        # Get session
        session = get_session(session_id)

        # If not logged in
        if not session:
            request.send_response(302)
            request.send_header("Location", "/login")
            request.end_headers()
            return

        # Get doctor ID from session
        doctor_id = session["user_id"]

        # Connect to database
        connection = get_connection()
        cursor = connection.cursor()

        # Get doctor information
        cursor.execute("""
            SELECT name, specialization, email, phone, status
            FROM doctor
            WHERE doctor_id = ?
        """, (doctor_id,))

        doctor = cursor.fetchone()

        connection.close()

        # Doctor not found
        if not doctor:
            request.send_response(404)
            request.send_header("Content-Type", "text/html")
            request.end_headers()

            request.wfile.write(
                b"<h1>Doctor not found.</h1>"
            )

            return

        # Render dashboard
        TemplateEngine.render(
            request,
            "doctorDashboard.html",
            {
                "title": "Doctor Dashboard",
                "doctor_id": doctor_id,
                "name": doctor[0],
                "specialization": doctor[1],
                "email": doctor[2],
                "phone": doctor[3],
                "status": doctor[4]
            }
        )
