from template_engine import TemplateEngine
from database import get_connection


class DocProfile:

    @staticmethod
    def profile(request, doctor_id):

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
                        SELECT
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
                     """, (doctor_id,)
                )
                

        doctor = cursor.fetchone()

        connection.close()

        if not doctor:
            request.send_response(404)
            request.send_header(
                "Content-Type",
                "text/html"
            )
            request.end_headers()

            request.wfile.write(
                b"<h1>Doctor not found.</h1>"
            )

            return

        TemplateEngine.render(
            request,
            "DocProf.html",
            {
                "title": "Doctor Dashboard",
                "doctor_id": doctor_id,
                "name": doctor[0],
                "specialization": doctor[1],
                "email": doctor[2],
                "phone": doctor[3],
                "status": doctor[4],
                "profile_image": doctor[5] or "static/img/doctor.jpeg",
                "nmc_no": doctor[6] or "",
                "experience": doctor[7] or 0,
                "qualification": doctor[8] or "",
                "location": doctor[9] or "",
                "about": doctor[10] or "",
                "consultation_fee": doctor[11] or 0,
                "doctor": doctor
                }
            )