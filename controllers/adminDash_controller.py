
from template_engine import TemplateEngine
from database import get_connection
from session import get_session


class AdminDashboardController:

    @staticmethod
    def dashboard(request):

        # =====================================================
        # GET SESSION COOKIE
        # =====================================================

        cookie = request.headers.get("Cookie", "")

        session_id = None

        for item in cookie.split(";"):

            item = item.strip()

            if item.startswith("session_id="):

                session_id = item.split("=", 1)[1]

                break


        # =====================================================
        # CHECK SESSION
        # =====================================================

        session = get_session(session_id)

        if not session:

            request.send_response(302)

            request.send_header(
                "Location",
                "/admin/login"
            )

            request.end_headers()

            return


        # =====================================================
        # CHECK USER TYPE
        # =====================================================

        if session.get("user_type") != "admin":

            request.send_response(302)

            request.send_header(
                "Location",
                "/admin/login"
            )

            request.end_headers()

            return


        # =====================================================
        # GET ADMIN ID
        # =====================================================

        admin_id = session.get("user_id")


        # =====================================================
        # DATABASE CONNECTION
        # =====================================================

        connection = get_connection()

        cursor = connection.cursor()


        # =====================================================
        # GET ADMIN INFORMATION
        # =====================================================

        cursor.execute(
            """
            SELECT
                name,
                email
            FROM admin
            WHERE admin_id = ?
            """,
            (admin_id,)
        )

        admin = cursor.fetchone()


        # =====================================================
        # ADMIN NOT FOUND
        # =====================================================

        if not admin:

            connection.close()

            request.send_response(302)

            request.send_header(
                "Location",
                "/admin/login"
            )

            request.end_headers()

            return


        admin_name = admin[0]


        # =====================================================
        # DOCTOR COUNTS
        # =====================================================


        # Total doctors

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM doctor
            """
        )

        total_doctors = cursor.fetchone()[0]


        # Pending doctors

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM doctor
            WHERE status = 'Pending'
            """
        )

        pending_doctors = cursor.fetchone()[0]


        # Certified doctors

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM doctor
            WHERE status = 'Certified'
            """
        )

        certified_doctors = cursor.fetchone()[0]


        # Rejected doctors

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM doctor
            WHERE status = 'Rejected'
            """
        )

        rejected_doctors = cursor.fetchone()[0]


        # =====================================================
        # PENDING DOCTORS
        # =====================================================

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
                doctor_bio.nmc_no

            FROM doctor

            LEFT JOIN doctor_bio
                ON doctor.doctor_id = doctor_bio.doctor_id

            WHERE doctor.status = 'Pending'

            ORDER BY doctor.doctor_id DESC
            """
        )

        pending_list = cursor.fetchall()


        # =====================================================
        # CERTIFIED DOCTORS
        # =====================================================

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
                doctor_bio.nmc_no

            FROM doctor

            LEFT JOIN doctor_bio
                ON doctor.doctor_id = doctor_bio.doctor_id

            WHERE doctor.status = 'Certified'

            ORDER BY doctor.doctor_id DESC
            """
        )

        certified_list = cursor.fetchall()


        # =====================================================
        # REJECTED DOCTORS
        # =====================================================

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
                doctor_bio.nmc_no

            FROM doctor

            LEFT JOIN doctor_bio
                ON doctor.doctor_id = doctor_bio.doctor_id

            WHERE doctor.status = 'Rejected'

            ORDER BY doctor.doctor_id DESC
            """
        )

        rejected_list = cursor.fetchall()


        # =====================================================
        # VERIFICATION PERCENTAGE
        # =====================================================

        if total_doctors > 0:

            verified_percent = round(
                (certified_doctors / total_doctors) * 100
            )

        else:

            verified_percent = 0


        # =====================================================
        # CLOSE DATABASE
        # =====================================================

        connection.close()


        # =====================================================
        # RENDER ADMIN DASHBOARD
        # =====================================================

        TemplateEngine.render(
            request,
            "admin_dashboard.html",
            {
                "title": "Admin Dashboard",

                "admin_name": admin_name,

                # Counts
                "total_doctors": total_doctors,
                "pending_doctors": pending_doctors,
                "certified_doctors": certified_doctors,
                "rejected_doctors": rejected_doctors,

                # Progress
                "verified_percent": verified_percent,

                # Doctor lists
                "pending_list": pending_list,
                "certified_list": certified_list,
                "rejected_list": rejected_list
            }
        )
