import re
from datetime import date
from urllib.parse import parse_qs, quote_plus

from template_engine import TemplateEngine
from database import get_connection, hash_password


EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
NAME_RE = re.compile(r"^[A-Za-z ]{2,}$")


class RegisterController:

    @staticmethod
    def show(request):

        query = getattr(request, "query", {})
        error = query.get("error", [""])[0]

        TemplateEngine.render(
            request,
            "register.html",
            {
                "title": "Create Account",
                "error": error,
                "error_display": "flex" if error else "none"
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
        name = form_data.get("name", [""])[0].strip()
        email = form_data.get("email", [""])[0].strip()
        phone = form_data.get("phone", [""])[0].strip()
        date_of_birth = form_data.get("date_of_birth", [""])[0].strip()
        gender = form_data.get("gender", [""])[0].strip()
        address = form_data.get("address", [""])[0].strip()
        specialization = form_data.get("specialization", [""])[0].strip()
        password = form_data.get("password", [""])[0]
        confirm_password = form_data.get("confirm_password", [""])[0]
        terms = form_data.get("terms", [""])[0]

        # -----------------------------
        # VALIDATION
        # -----------------------------

        errors = []

        if account not in ("patient", "doctor"):
            RegisterController.redirect_error(request, "Invalid account type.")
            return

        if not NAME_RE.match(name):
            errors.append("Enter a valid full name (letters only, at least 2 characters).")

        if not EMAIL_RE.match(email):
            errors.append("Enter a valid email address.")

        phone_digits = re.sub(r"\D", "", phone)
        if not (7 <= len(phone_digits) <= 15):
            errors.append("Enter a valid phone number (7-15 digits).")

        if len(password) < 6 or not re.search(r"[A-Za-z]", password) or not re.search(r"[0-9]", password):
            errors.append("Password must be at least 6 characters and include a letter and a number.")

        if password != confirm_password:
            errors.append("Passwords do not match.")

        if terms != "on":
            errors.append("You must agree to the Terms & Conditions.")

        if account == "patient":

            if not gender:
                errors.append("Please select a gender.")

            if not address:
                errors.append("Enter your address.")

            if date_of_birth:
                try:
                    dob = date.fromisoformat(date_of_birth)
                    if dob > date.today():
                        errors.append("Date of birth cannot be in the future.")
                except ValueError:
                    errors.append("Enter a valid date of birth.")
            else:
                errors.append("Enter your date of birth.")

        else:  # doctor

            if not specialization:
                errors.append("Please select a specialization.")

        # Stop here if any basic validation failed -- avoid touching the DB
        if errors:
            RegisterController.redirect_error(request, "; ".join(errors))
            return

        connection = get_connection()
        cursor = connection.cursor()

        # -----------------------------
        # UNIQUENESS CHECK (across both tables)
        # -----------------------------

        cursor.execute(
            "SELECT 1 FROM patient WHERE email = ? UNION SELECT 1 FROM doctor WHERE email = ?",
            (email, email)
        )

        if cursor.fetchone():
            connection.close()
            RegisterController.redirect_error(request, "An account with that email already exists.")
            return

        hashed_password = hash_password(password)

        # -----------------------------
        # INSERT
        # -----------------------------

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
                hashed_password
            ))

        else:  # doctor

            cursor.execute("""
                INSERT INTO doctor
                (name, specialization, email, phone, password)
                VALUES (?, ?, ?, ?, ?)
            """, (
                name,
                specialization,
                email,
                phone,
                hashed_password
            ))

        # Registration successful -- commit/close for BOTH account types
        connection.commit()
        connection.close()

        request.send_response(302)
        request.send_header("Location", "/login")
        request.end_headers()
        return

    @staticmethod
    def redirect_error(request, error):

        request.send_response(302)

        request.send_header(
            "Location",
            f"/register?error={quote_plus(error)}"
        )

        request.end_headers()