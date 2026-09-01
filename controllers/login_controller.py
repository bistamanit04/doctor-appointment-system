from urllib.parse import parse_qs

from template_engine import TemplateEngine
from database import get_connection, hash_password


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
        # Get request body length
        content_length = int(
            request.headers.get("Content-Length", 0)
        )

        # Read submitted form data
        data = request.rfile.read(content_length)

        

        # Convert form data into dictionary
        form_data = parse_qs(
            data.decode("utf-8")
        )

        # Get account type
        account = form_data.get(
            "account",
            ["patient"]
        )[0]

        # Get email
        email = form_data.get(
            "email",
            [""]
        )[0]

        # Get password
        password = form_data.get(
            "password",
            [""]
        )[0]


        # Hash entered password
        hashed_password = hash_password(password)

        # Connect to database
        connection = get_connection()
        cursor = connection.cursor()

        # Patient login
        if account == "patient":

            cursor.execute("""
                SELECT patient_id, name
                FROM patient
                WHERE email = ? AND password = ?
            """, (
                email,
                hashed_password
            ))

        # Doctor login
        elif account == "doctor":

            cursor.execute("""
                SELECT doctor_id, name, status
                FROM doctor
                WHERE email = ? AND password = ?
            """, (
                email,
                hashed_password
            ))

        # Admin login
        elif account == "admin":

            connection.close()

            request.send_response(200)

            request.send_header(
                "Content-Type",
                "text/html"
            )

            request.end_headers()

            request.wfile.write(
                b"""
                <h1>Admin Login</h1>
                <p>Admin login will be implemented later.</p>
                """
            )

            return

        else:

            connection.close()

            request.send_response(400)

            request.send_header(
                "Content-Type",
                "text/html"
            )

            request.end_headers()

            request.wfile.write(
                b"<h1>Invalid account type.</h1>"
            )

            return

        # Get matching user
        result = cursor.fetchone()

        print("DATABASE RESULT:", result)

        connection.close()

        # Login successful
        if result:

            print("LOGIN SUCCESSFUL")

            request.send_response(200)

            request.send_header(
                "Content-Type",
                "text/html"
            )

            request.end_headers()

            request.wfile.write(
                f"""
                <h1>Login successful!</h1>
                <p>Welcome, {result[1]}!</p>
                """.encode("utf-8")
            )

        # Login failed
        else:

            print("LOGIN FAILED")

            request.send_response(401)

            request.send_header(
                "Content-Type",
                "text/html"
            )

            request.end_headers()

            request.wfile.write(
                b"""
                <h1>Invalid email or password.</h1>
                <p>Please check your credentials and try again.</p>
                """
            )