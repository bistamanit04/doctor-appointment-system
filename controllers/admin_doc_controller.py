from urllib.parse import parse_qs

from database import get_connection
from session import get_session


class AdminDoctorController:

    @staticmethod
    def certify(request):
        print("REJECT METHOD CALLED")

        # Get session cookie
        cookie = request.headers.get("Cookie", "")

        session_id = None

        for item in cookie.split(";"):

            item = item.strip()

            if item.startswith("session_id="):

                session_id = item.split("=", 1)[1]

                break   


        # Check session
        session = get_session(session_id)

        if not session:

            request.send_response(302)
            request.send_header(
                "Location",
                "/admin/login"
            )
            request.end_headers()

            return


        # Make sure logged-in user is admin
        if session.get("user_type") != "admin":

            request.send_response(302)
            request.send_header(
                "Location",
                "/admin/login"
            )
            request.end_headers()

            return


        # Read form data
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


        # Check doctor ID
        if not doctor_id.isdigit():

            request.send_response(302)
            request.send_header(
                "Location",
                "/admin/dashboard"
            )
            request.end_headers()

            return


        doctor_id = int(doctor_id)


        # Update doctor status
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


        # Return to dashboard
        request.send_response(302)
        request.send_header(
            "Location",
            "/admin/dashboard"
        )
        request.end_headers()


    @staticmethod
    def reject(request):

        # Get session cookie
        cookie = request.headers.get("Cookie", "")

        session_id = None

        for item in cookie.split(";"):

            item = item.strip()

            if item.startswith("session_id="):

                session_id = item.split("=", 1)[1]

                break


        # Check session
        session = get_session(session_id)

        if not session:

            request.send_response(302)
            request.send_header(
                "Location",
                "/admin/login"
            )
            request.end_headers()

            return


        # Make sure logged-in user is admin
        if session.get("user_type") != "admin":

            request.send_response(302)
            request.send_header(
                "Location",
                "/admin/login"
            )
            request.end_headers()

            return


        # Read form data
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


        # Check doctor ID
        if not doctor_id.isdigit():

            request.send_response(302)
            request.send_header(
                "Location",
                "/admin/dashboard"
            )
            request.end_headers()

            return


        doctor_id = int(doctor_id)


        # Update doctor status
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


        # Return to dashboard
        request.send_response(302)
        request.send_header(
            "Location",
            "/admin/dashboard"
        )
        request.end_headers()