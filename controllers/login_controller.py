from urllib.parse import parse_qs
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
            request.headers.get("Content-Length", 0)
        )

        data = request.rfile.read(content_length)

        form_data = parse_qs(
            data.decode("utf-8")
        )

        account = form_data.get(
            "account", ["patient"]
        )[0]

        email = form_data.get(
            "email", [""]
        )[0]

        password = form_data.get(
            "password", [""]
        )[0]

        password = hash_password(password)

        connection = get_connection()
        cursor = connection.cursor()

        if account == "patient":

            cursor.execute("""
                SELECT patient_id, name
                FROM patient
                WHERE email = ? AND password = ?
            """, (email, password))

        elif account == "doctor":

            cursor.execute("""
                SELECT doctor_id, name, status
                FROM doctor
                WHERE email = ? AND password = ?
            """, (email, password))

        elif account == "admin":

            connection.close()

            request.send_response(200)
            request.send_header(
                "Content-Type",
                "text/html"
            )
            request.end_headers()

            request.wfile.write(
                b"<h1>Admin login is not implemented yet.</h1>"
            )

            return

        result = cursor.fetchone()

        connection.close()

        # LOGIN SUCCESS
        if result:
           user_id = result[0]

           session_id = create_session(
           account,
           user_id
         )
           request.send_response(302)
           
           if account == "patient":
              request.send_header(
              "Location",
              "/patient/dashboard"
             )
              
           elif account == "doctor":
              request.send_header(
            "Location",
            "/doctor/dashboard"
             )

           else:
            request.send_header(
            "Location",
            "/login"
          )

           request.send_header(
             "Set-Cookie",
             f"session_id={session_id}; Path=/"
             )

           request.end_headers()

# LOGIN FAILED
        else:
        
         request.send_response(401)

        request.send_header(
         "Content-Type",
        "text/html"
        )

        request.end_headers()

        request.wfile.write(
        b"<h1>Invalid email or password.</h1>"
    )