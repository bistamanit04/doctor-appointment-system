from urllib.parse import parse_qs

from template_engine import TemplateEngine
from database import get_connection
from session import get_session


class DoctorBioController:

    @staticmethod
    def show(request):

        # GET SESSION ID
        cookie = request.headers.get(
            "Cookie",
            ""
        )

        session_id = None

        for item in cookie.split(";"):

            item = item.strip()

            if item.startswith("session_id="):

                session_id = item.split(
                    "=",
                    1
                )[1]

                break

        # CHECK SESSION
       

        session = get_session(session_id)

        if not session:

            request.send_response(302)

            request.send_header(
                "Location",
                "/login"
            )

            request.end_headers()

            return


    
        # CHECK DOCTOR

        if session["user_type"] != "doctor":

            request.send_response(403)

            request.send_header(
                "Content-Type",
                "text/html"
            )

            request.end_headers()

            request.wfile.write(
                b"<h1>Access Denied</h1>"
            )

            return


        doctor_id = session["user_id"]


       
        # GET EXISTING BIO

        connection = get_connection()

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                bio_id,
                profile_image,
                nmc_no,
                experience,
                qualification,
                location,
                about,
                consultation_fee
            FROM doctor_bio
            WHERE doctor_id = ?
            """,
            (doctor_id,)
        )

        bio = cursor.fetchone()

        connection.close()


      
        # SHOW FORM

        TemplateEngine.render(
            request,
            "doctor_bio.html",
            {
                "title": "Doctor Profile",
                "bio": bio
            }
        )


    @staticmethod
    def save(request):

  
        # GET SESSION

        cookie = request.headers.get(
            "Cookie",
            ""
        )

        session_id = None

        for item in cookie.split(";"):

            item = item.strip()

            if item.startswith("session_id="):

                session_id = item.split(
                    "=",
                    1
                )[1]

                break


        session = get_session(session_id)


  
        # CHECK SESSION

        if not session:

            request.send_response(302)

            request.send_header(
                "Location",
                "/login"
            )

            request.end_headers()

            return


      
        # CHECK DOCTOR

        if session["user_type"] != "doctor":

            request.send_response(403)

            request.send_header(
                "Content-Type",
                "text/html"
            )

            request.end_headers()

            request.wfile.write(
                b"<h1>Access Denied</h1>"
            )

            return


        doctor_id = session["user_id"]


     
        # READ FORM

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


        nmc_no = form_data.get(
            "nmc_no",
            [""]
        )[0].strip()

        experience = form_data.get(
            "experience",
            ["0"]
        )[0].strip()

        qualification = form_data.get(
            "qualification",
            [""]
        )[0].strip()

        location = form_data.get(
            "location",
            [""]
        )[0].strip()

        about = form_data.get(
            "about",
            [""]
        )[0].strip()

        consultation_fee = form_data.get(
            "consultation_fee",
            ["0"]
        )[0].strip()


      
        # BASIC VALIDATION

        if not nmc_no:

            TemplateEngine.render(
                request,
                "doctor_bio.html",
                {
                    "title": "Doctor Profile",
                    "error": "NMC number is required."
                }
            )

            return


    
        # SAVE BIO

        connection = get_connection()

        cursor = connection.cursor()


        # Check whether bio already exists

        cursor.execute(
            """
            SELECT bio_id
            FROM doctor_bio
            WHERE doctor_id = ?
            """,
            (doctor_id,)
        )

        existing_bio = cursor.fetchone()


        if existing_bio:

            # UPDATE

            cursor.execute(
                """
                UPDATE doctor_bio
                SET
                    nmc_no = ?,
                    experience = ?,
                    qualification = ?,
                    location = ?,
                    about = ?,
                    consultation_fee = ?
                WHERE doctor_id = ?
                """,
                (
                    nmc_no,
                    experience,
                    qualification,
                    location,
                    about,
                    consultation_fee,
                    doctor_id
                )
            )

        else:

            # INSERT

            cursor.execute(
                """
                INSERT INTO doctor_bio (
                    doctor_id,
                    nmc_no,
                    experience,
                    qualification,
                    location,
                    about,
                    consultation_fee
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    doctor_id,
                    nmc_no,
                    experience,
                    qualification,
                    location,
                    about,
                    consultation_fee
                )
            )


        connection.commit()

        connection.close()


        # REDIRECT TO DOCTOR DASHBOARD

        request.send_response(302)

        request.send_header(
            "Location",
            "/doctor/dashboard"
        )

        request.end_headers()
