from urllib.parse import quote_plus, parse_qs

from template_engine import TemplateEngine
from database import get_connection, hash_password
from session import create_session


class AdminLoginController:

    @staticmethod
    def show(request):

        TemplateEngine.render(
            request,
            "admin_login.html",
            {
                "title": "Admin Login",
                "error": "",
                "error_display": "none"
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

        # BASIC VALIDATION

        if not email:

            AdminLoginController.redirect_error(
                request,
                "Please enter your email."
            )

            return

        if len(password) < 6:

            AdminLoginController.redirect_error(
                request,
                "Password must be at least 6 characters."
            )

            return

        hashed_password = hash_password(password)

        connection = get_connection()
        cursor = connection.cursor()

        # CHECK ADMIN

        cursor.execute(
            """
            SELECT admin_id, name
            FROM admin
            WHERE email = ?
            AND password = ?
            """,
            (
                email,
                hashed_password
            )
        )

        admin = cursor.fetchone()

        if admin:

            connection.close()

            session_id = create_session(
                "admin",
                admin[0]
            )

            request.send_response(302)

            request.send_header(
                "Location",
                "/admin/dashboard"
            )

            request.send_header(
                "Set-Cookie",
                f"session_id={session_id}; Path=/"
            )

            request.end_headers()

            return

        # INVALID LOGIN

        connection.close()

        AdminLoginController.redirect_error(
            request,
            "Invalid admin email or password."
        )

    @staticmethod
    def redirect_error(request, error):

        request.send_response(302)

        request.send_header(
            "Location",
            f"/admin/login?error={quote_plus(error)}"
        )

        request.end_headers()