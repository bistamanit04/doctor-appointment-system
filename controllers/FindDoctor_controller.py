from template_engine import TemplateEngine
from database import get_connection


class DoctorController:

    @staticmethod
    def DOClist(request):

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
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
            WHERE doctor.status IN ('Pending', 'Certified')
            ORDER BY doctor.name
        """)

        doctors = cursor.fetchall()

        connection.close()

        TemplateEngine.render(
            request,
            "FindDoctor.html",
            {
                "title": "Find Doctors",
                "doctors": doctors
            }
        )