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
                SELECT
                doctor.name,
                doctor.specialization,
                doctor.email,
                doctor.phone,
                doctor.status,
                doctor_bio.profile_image,
                doctor_bio.nmc_no,
                doctor_bio.experience,
                doctor_bio.qualification,
                doctor_bio.location,
                doctor_bio.about,
                doctor_bio.consultation_fee
             FROM doctor
             LEFT JOIN doctor_bio
              ON doctor.doctor_id = doctor_bio.doctor_id
             WHERE doctor.doctor_id = ?
             """, (doctor_id,)
        )
        

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
               "status": doctor[4],
               
               "profile_image": doctor[5] or "static/img/doctor.jpeg",
               "nmc_no": doctor[6] or "",
               "experience": doctor[7] or 0,
               "qualification": doctor[8] or "",
               "location": doctor[9] or "",
               "about": doctor[10] or "",
               "consultation_fee": doctor[11] or 0,
               "doctor": doctor
           })
