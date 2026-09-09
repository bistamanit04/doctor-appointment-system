from urllib.parse import parse_qs

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

  
        # GET DOCTOR ID
     

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

        # ------------------------------------------------------
        # DOCTOR DATA
        #
        # 0  doctor_id
        # 1  name
        # 2  email
        # 3  phone
        # 4  specialization
        #
        # 5  bio_id
        # 6  profile_image
        # 7  nmc_no
        # 8  experience
        # 9  qualification
        # 10 location
        # 11 about
        # 12 consultation_fee
        # ------------------------------------------------------

        TemplateEngine.render(
            request,
            "doctor_bio.html",
            {
                "title": "Doctor Profile",

                "name": doctor[1],

                "specialization": doctor[4],

                "profile_image":
                    doctor[6]
                    or "static/img/doctor.jpeg",

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
                "text/html; charset=utf-8"
            )
            request.end_headers()

            request.wfile.write(
                b"<h1>Access Denied</h1>"
            )

            return

        doctor_id = session["user_id"]

        # READ FORM DATA
     

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

      
        # GET FORM VALUES
   

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

            request.send_response(302)

            request.send_header(
                "Location",
                "/doctor/profile?error=NMC+number+is+required"
            )

            request.end_headers()

            return

      
        # DATABASE
    

        connection = get_connection()

        cursor = connection.cursor()

        # CHECK BIO
  

        cursor.execute(
            """
            SELECT bio_id
            FROM doctor_bio
            WHERE doctor_id = ?
            """,
            (doctor_id,)
        )

        existing_bio = cursor.fetchone()

    
        # UPDATE
        
        if existing_bio:

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

      
        # INSERT
  

        else:

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

      
        # REDIRECT
     

        request.send_response(302)

        request.send_header(
            "Location",
            "/doctor/dashboard"
        )

        request.end_headers()
