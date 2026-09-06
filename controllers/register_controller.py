
from urllib.parse import parse_qs
from template_engine import TemplateEngine
from database import get_connection,hash_password

class RegisterController:

    @staticmethod
    def show(request):
        TemplateEngine.render(
            request,
            "register.html",
            {
                "title": "Create Account"
            }
        )

    @staticmethod
    def register(request):

        content_length = int(
            request.headers.get("Content-Length", 0)
        )

        data = request.rfile.read(content_length)

        form_data = parse_qs(data.decode("utf-8"))

        account = form_data.get("account", ["patient"])[0]
        name = form_data.get("name", [""])[0]
        email = form_data.get("email", [""])[0]
        phone = form_data.get("phone", [""])[0]
        date_of_birth = form_data.get("date_of_birth", [""])[0]
        gender = form_data.get("gender", [""])[0]
        address = form_data.get("address", [""])[0]
        password = form_data.get("password", [""])[0]
        password=hash_password(password)

        connection = get_connection()
        cursor = connection.cursor()

        if account == "patient":

            cursor.execute("""
                INSERT INTO patient
                (name, email, phone, date_of_birth, gender, address, password)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                name,
                email,
                phone,
                date_of_birth,
                gender,
                address,
                password
            ))

        elif account == "doctor":

            specialization = form_data.get(
                "specialization", [""]
            )[0]

            cursor.execute("""
                INSERT INTO doctor
                (name, specialization, email, phone, password)
                VALUES (?, ?, ?, ?, ?)
            """, (
                name,
                specialization,
                email,
                phone,
                password
            ))

      # Registration successful

            connection.commit()
            connection.close()
        
        request.send_response(302)
        request.send_header("Location", "/login")
        request.end_headers()
        return
        
    

     
