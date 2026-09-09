   
from database import get_connection
class DoctorModel:

    
    # GET DOCTOR BY ID
   

    @staticmethod
    def get_by_id(doctor_id):

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                d.doctor_id,
                d.name,
                d.email,
                d.phone,
                d.specialization,

                b.bio_id,
                b.profile_image,
                b.nmc_no,
                b.experience,
                b.qualification,
                b.location,
                b.about,
                b.consultation_fee

            FROM doctor d

            LEFT JOIN doctor_bio b
                ON d.doctor_id = b.doctor_id

            WHERE d.doctor_id = ?
            """,
            (doctor_id,)
        )

        doctor = cursor.fetchone()

        connection.close()

        return doctor



    # GET ALL DOCTORS
   
    @staticmethod
    def get_all():

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                d.doctor_id,
                d.name,
                d.email,
                d.phone,
                d.specialization,

                b.bio_id,
                b.profile_image,
                b.nmc_no,
                b.experience,
                b.qualification,
                b.location,
                b.about,
                b.consultation_fee

            FROM doctor d

            LEFT JOIN doctor_bio b
                ON d.doctor_id = b.doctor_id

            ORDER BY d.name
            """
        )

        doctors = cursor.fetchall()

        connection.close()

        return doctors


   
    # GET DOCTOR BIO
    @staticmethod
    def get_bio(doctor_id):

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                bio_id,
                doctor_id,
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

        return bio


    
    # CHECK IF BIO EXISTS
    @staticmethod
    def bio_exists(doctor_id):

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT bio_id
            FROM doctor_bio
            WHERE doctor_id = ?
            """,
            (doctor_id,)
        )

        result = cursor.fetchone()

        connection.close()

        return result is not None
