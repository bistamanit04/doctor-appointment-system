
from urllib.parse import quote_plus, parse_qs

from template_engine import TemplateEngine
from database import get_connection, hash_password
from session import create_session


class LoginController:

    @staticmethod
    def show(request):

        TemplateEngine.render(
            request,
            "login.html",
            {
                "title": "Login"
            }
        )

    @staticmethod
    def login(request):

        content_length = int(
            request.headers.get(
                "Content-Length",
                0
            )
        )

        data = request.rfile.read(
            content_length
        )

        form_data = parse_qs(
            data.decode("utf-8")
        )

        email = form_data.get(
            "email",
            [""]
        )[0].strip()

        password = form_data.get(
            "password",
            [""]
        )[0]

        # -----------------------------
        # BASIC VALIDATION
        # -----------------------------

        if not email:

            LoginController.redirect_error(
                request,
                "Please enter your email."
            )

            return

        if len(password) < 6:

            LoginController.redirect_error(
                request,
                "Password must be at least 6 characters."
            )

            return

        hashed_password = hash_password(
            password
        )

        connection = get_connection()
        cursor = connection.cursor()

        # -----------------------------
        # CHECK PATIENT
        # -----------------------------

        cursor.execute(
            """
            SELECT patient_id, name
            FROM patient
            WHERE email = ?
            AND password = ?
            """,
            (
                email,
                hashed_password
            )
        )

        patient = cursor.fetchone()

        if patient:

            connection.close()

            session_id = create_session(
                "patient",
                patient[0]
            )

            request.send_response(302)

            request.send_header(
                "Location",
                "/patient/dashboard"
            )

            request.send_header(
                "Set-Cookie",
                f"session_id={session_id}; Path=/"
            )

            request.end_headers()

            return

        # -----------------------------
        # CHECK DOCTOR
        # -----------------------------

        cursor.execute(
            """
            SELECT doctor_id, name, status
            FROM doctor
            WHERE email = ?
            AND password = ?
            """,
            (
                email,
                hashed_password
            )
        )

        doctor = cursor.fetchone()

        if doctor:

            connection.close()

            session_id = create_session(
                "doctor",
                doctor[0]
            )

            request.send_response(302)

            request.send_header(
                "Location",
                "/doctor/dashboard"
            )

            request.send_header(
                "Set-Cookie",
                f"session_id={session_id}; Path=/"
            )

            request.end_headers()

            return

        # -----------------------------
        # INVALID LOGIN
        # -----------------------------'
      
        connection.close()
 
        LoginController.redirect_error(
            request,
            "Invalid email or password."
        )
 
        return
 
    @staticmethod
    def redirect_error(request, error):
 
        request.send_response(302)
 
        request.send_header(
            "Location",
            f"/login?error={quote_plus(error)}"
        )
 
        request.end_headers()
 
    @staticmethod
    def show_error(request, error):
 
        TemplateEngine.render(
            request,
            "login.html",
            {
                "title": "Login",
                "error": error,
                "error_display": "block"
            }
        )
 