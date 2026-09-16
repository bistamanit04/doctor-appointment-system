import os
import re
import uuid

from template_engine import TemplateEngine
from database import get_connection
from session import get_session
from models.doctor_model import DoctorModel


class DoctorBioController:

   
    # GET /doctor/profile
    @staticmethod
    def show(request):

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
            request.send_header("Location", "/login")
            request.end_headers()
            return

        # CHECK DOCTOR
        if session["user_type"] != "doctor":

            request.send_response(403)
            request.send_header(
                "Content-Type",
                "text/html; charset=utf-8"
            )
            request.end_headers()

            request.wfile.write(
                b"<h1>Access Denied</h1>"
            )

            return

        doctor_id = session["user_id"]

        # GET DOCTOR + BIO
        doctor = DoctorModel.get_by_id(doctor_id)

        if not doctor:

            request.send_response(404)
            request.send_header(
                "Content-Type",
                "text/html; charset=utf-8"
            )
            request.end_headers()

            request.wfile.write(
                b"<h1>Doctor not found</h1>"
            )

            return

        TemplateEngine.render(
            request,
            "doctor_bio.html",
            {
                "title": "Doctor Profile",

                "name": doctor[1],

                "specialization": doctor[4],

                "profile_image":
                    doctor[6]
                    or "/static/img/doctor.jpeg",

                "nmc_no":
                    doctor[7]
                    or "",

                "experience":
                    doctor[8]
                    if doctor[8] is not None
                    else 0,

                "qualification":
                    doctor[9]
                    or "",

                "location":
                    doctor[10]
                    or "",

                "about":
                    doctor[11]
                    or "",

                "consultation_fee":
                    doctor[12]
                    if doctor[12] is not None
                    else 0,

                "error": "",

                "error_display": "none"
            }
        )


    # POST /doctor/profile/save
    @staticmethod
    def save(request):

   
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
                "/login"
            )
            request.end_headers()

            return

      
        # CHECK DOCTOR
        if session["user_type"] != "doctor":

            request.send_response(403)
            request.send_header(
                "Content-Type",
                "text/html; charset=utf-8"
            )
            request.end_headers()

            request.wfile.write(
                b"<h1>Access Denied</h1>"
            )

            return

        doctor_id = session["user_id"]

       
        # READ REQUEST BODY
        content_length = int(
            request.headers.get(
                "Content-Length",
                0
            )
        )

        body = request.rfile.read(content_length)

        content_type = request.headers.get(
            "Content-Type",
            ""
        )

       
        # PARSE FORM DATA
        fields, uploaded_file = DoctorBioController.parse_multipart(
            body,
            content_type
        )
      
        # GET VALUES
        nmc_no = fields.get(
            "nmc_no",
            ""
        ).strip()

        experience = fields.get(
            "experience",
            "0"
        ).strip()

        qualification = fields.get(
            "qualification",
            ""
        ).strip()

        location = fields.get(
            "location",
            ""
        ).strip()

        about = fields.get(
            "about",
            ""
        ).strip()

        consultation_fee = fields.get(
            "consultation_fee",
            "0"
        ).strip()
        
        # VALIDATION
        if not nmc_no:

            request.send_response(302)

            request.send_header(
                "Location",
                "/doctor/profile?error=NMC+number+is+required"
            )

            request.end_headers()

            return

        try:
            experience = int(experience)

            if experience < 0 or experience > 70:
                raise ValueError

        except ValueError:

            request.send_response(302)

            request.send_header(
                "Location",
                "/doctor/profile?error=Invalid+experience"
            )

            request.end_headers()

            return

        try:
            consultation_fee = float(
                consultation_fee
            )

            if consultation_fee < 0:
                raise ValueError

        except ValueError:

            request.send_response(302)

            request.send_header(
                "Location",
                "/doctor/profile?error=Invalid+consultation+fee"
            )

            request.end_headers()

            return

        
        # DATABASE
        connection = get_connection()

        cursor = connection.cursor()

        # CHECK EXISTING BIO
        cursor.execute(
            """
            SELECT bio_id, profile_image
            FROM doctor_bio
            WHERE doctor_id = ?
            """,
            (doctor_id,)
        )

        existing_bio = cursor.fetchone()

        old_image = None

        if existing_bio:
            old_image = existing_bio[1]

        
        # HANDLE IMAGE
        profile_image = old_image

        if uploaded_file:

            original_filename = uploaded_file["filename"]

            file_data = uploaded_file["data"]

            # Check extension
            extension = os.path.splitext(
                original_filename
            )[1].lower()

            allowed_extensions = [
                ".jpg",
                ".jpeg",
                ".png",
                ".webp"
            ]

            if extension not in allowed_extensions:

                connection.close()

                request.send_response(302)

                request.send_header(
                    "Location",
                    "/doctor/profile?error=Invalid+image+type"
                )

                request.end_headers()

                return

            # Check file size
            if len(file_data) > 2 * 1024 * 1024:

                connection.close()

                request.send_response(302)

                request.send_header(
                    "Location",
                    "/doctor/profile?error=Image+must+be+2MB+or+smaller"
                )

                request.end_headers()

                return

            
            # CREATE UPLOAD DIRECTORY
            upload_directory = os.path.join(
                "static",
                "uploads"
            )

            os.makedirs(
                upload_directory,
                exist_ok=True
            )

            
            # CREATE UNIQUE FILE NAME
            filename = (
                "doctor_"
                + str(doctor_id)
                + "_"
                + uuid.uuid4().hex
                + extension
            )

            file_path = os.path.join(
                upload_directory,
                filename
            )

            
            # SAVE IMAGE
            with open(
                file_path,
                "wb"
            ) as image_file:

                image_file.write(
                    file_data
                )
            # Store URL/path in database
            profile_image = (
                "/static/uploads/"
                + filename
            )

      
        # UPDATE EXISTING BIO
        if existing_bio:

            cursor.execute(
                """
                UPDATE doctor_bio
                SET
                    profile_image = ?,
                    nmc_no = ?,
                    experience = ?,
                    qualification = ?,
                    location = ?,
                    about = ?,
                    consultation_fee = ?
                WHERE doctor_id = ?
                """,
                (
                    profile_image,
                    nmc_no,
                    experience,
                    qualification,
                    location,
                    about,
                    consultation_fee,
                    doctor_id
                )
            )

    
        # CREATE NEW BIO
        else:
            cursor.execute(
                """
                INSERT INTO doctor_bio (
                    doctor_id,
                    profile_image,
                    nmc_no,
                    experience,
                    qualification,
                    location,
                    about,
                    consultation_fee
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    doctor_id,
                    profile_image,
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

       
        # SUCCESS
        request.send_response(302)

        request.send_header(
            "Location",
            "/doctor/dashboard"
        )
        request.end_headers()


    # MULTIPART PARSER
    @staticmethod
    def parse_multipart(body, content_type):

        fields = {}

        uploaded_file = None
        # Get boundary
        match = re.search(
            r'boundary="?([^";]+)"?',
            content_type
        )
        if not match:
            return fields, uploaded_file

        boundary = match.group(1).encode()

        delimiter = b"--" + boundary

        parts = body.split(delimiter)

        for part in parts:

            if not part or part in (b"--\r\n", b"--"):
                continue

            part = part.strip(b"\r\n")

            if b"\r\n\r\n" not in part:
                continue
            headers, content = part.split(
                b"\r\n\r\n",
                1
            )
            headers_text = headers.decode(
                "utf-8",
                errors="ignore"
            )

         
            # GET FIELD NAME
            name_match = re.search(
                r'name="([^"]+)"',
                headers_text
            )

            if not name_match:
                continue

            field_name = name_match.group(1)

            # FILE
            filename_match = re.search(
                r'filename="([^"]*)"',
                headers_text
            )
            if filename_match:
                filename = filename_match.group(1)
                if filename:
                    uploaded_file = {
                        "filename": os.path.basename(
                            filename
                        ),
                        "data": content
                    }

             # NORMAL FIELD
            else:
                value = content.decode(
                    "utf-8",
                    errors="ignore"
                )

                fields[field_name] = value

        return fields, uploaded_file