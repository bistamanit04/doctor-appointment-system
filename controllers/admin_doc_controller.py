
from urllib.parse import parse_qs

from database import get_connection
from session import get_session
from template_engine import TemplateEngine


class AdminDoctorController:

    # ==============================
    # CERTIFY DOCTOR
    # ==============================

    @staticmethod
    def certify(request):

        # GET SESSION
        cookie = request.headers.get("Cookie", "")

        session_id = None

        for item in cookie.split(";"):
            item = item.strip()

            if item.startswith("session_id="):
                session_id = item.split("=", 1)[1]
                break

        # CHECK SESSION
        session = get_session(session_id)

        if not session:
            request.send_response(302)
            request.send_header(
                "Location",
                "/admin/login"
            )
            request.end_headers()
            return

        # CHECK ADMIN
        if session.get("user_type") != "admin":
            request.send_response(302)
            request.send_header(
                "Location",
                "/admin/login"
            )
            request.end_headers()
            return

        # READ FORM DATA
        content_length = int(
            request.headers.get(
                "Content-Length",
                0
            )
        )

        data = request.rfile.read(content_length)

        form_data = parse_qs(
            data.decode("utf-8")
        )

        doctor_id = form_data.get(
            "doctor_id",
            [""]
        )[0]

        # CHECK DOCTOR ID
        if not doctor_id.isdigit():

            request.send_response(302)
            request.send_header(
                "Location",
                "/admin/dashboard"
            )
            request.end_headers()
            return

        doctor_id = int(doctor_id)

        # UPDATE DOCTOR STATUS
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE doctor
            SET status = 'Certified'
            WHERE doctor_id = ?
            AND status = 'Pending'
            """,
            (doctor_id,)
        )

        connection.commit()
        connection.close()

        # REDIRECT
        request.send_response(302)
        request.send_header(
            "Location",
            "/admin/dashboard"
        )
        request.end_headers()


    # ==============================
    # REJECT DOCTOR
    # ==============================

    @staticmethod
    def reject(request):

        # GET SESSION
        cookie = request.headers.get("Cookie", "")

        session_id = None

        for item in cookie.split(";"):
            item = item.strip()

            if item.startswith("session_id="):
                session_id = item.split("=", 1)[1]
                break

        # CHECK SESSION
        session = get_session(session_id)

        if not session:
            request.send_response(302)
            request.send_header(
                "Location",
                "/admin/login"
            )
            request.end_headers()
            return

        # CHECK ADMIN
        if session.get("user_type") != "admin":
            request.send_response(302)
            request.send_header(
                "Location",
                "/admin/login"
            )
            request.end_headers()
            return

        # READ FORM DATA
        content_length = int(
            request.headers.get(
                "Content-Length",
                0
            )
        )

        data = request.rfile.read(content_length)

        form_data = parse_qs(
            data.decode("utf-8")
        )

        doctor_id = form_data.get(
            "doctor_id",
            [""]
        )[0]

        # CHECK DOCTOR ID
        if not doctor_id.isdigit():

            request.send_response(302)
            request.send_header(
                "Location",
                "/admin/dashboard"
            )
            request.end_headers()
            return

        doctor_id = int(doctor_id)

        # UPDATE DOCTOR STATUS
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE doctor
            SET status = 'Rejected'
            WHERE doctor_id = ?
            AND status = 'Pending'
            """,
            (doctor_id,)
        )

        connection.commit()
        connection.close()

        # REDIRECT
        request.send_response(302)
        request.send_header(
            "Location",
            "/admin/dashboard"
        )
        request.end_headers()


    # ==============================
    # VIEW DOCTOR PROFILE
    # ==============================

    @staticmethod
    def profile(request, doctor_id):

        # GET SESSION
        cookie = request.headers.get("Cookie", "")

        session_id = None

        for item in cookie.split(";"):
            item = item.strip()

            if item.startswith("session_id="):
                session_id = item.split("=", 1)[1]
                break

        # CHECK SESSION
        session = get_session(session_id)

        if not session:
            request.send_response(302)
            request.send_header(
                "Location",
                "/admin/login"
            )
            request.end_headers()
            return

        # CHECK ADMIN
        if session.get("user_type") != "admin":
            request.send_response(302)
            request.send_header(
                "Location",
                "/admin/login"
            )
            request.end_headers()
            return

        # DATABASE
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                doctor.doctor_id,
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
            """,
            (doctor_id,)
        )

        doctor = cursor.fetchone()

        connection.close()

        # DOCTOR NOT FOUND
        if not doctor:

            request.send_response(404)

            request.send_header(
                "Content-Type",
                "text/html"
            )

            request.end_headers()

            request.wfile.write(
                b"<h1>Doctor not found</h1>"
            )

            return

        # RENDER PAGE
        TemplateEngine.render(
            request,
            "admin_doctor_profile.html",
            {
                "title": "Doctor Profile",
                "doctor": doctor
            }
        )
