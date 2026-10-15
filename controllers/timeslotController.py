import json
from datetime import date, datetime
from urllib.parse import parse_qs

from template_engine import TemplateEngine
from database import get_connection
from session import get_session


# Appointments in these states no longer occupy a slot.
INACTIVE_APPOINTMENT_STATES = "('Cancelled', 'Rejected')"


class TimeSlotController:

    # =====================================================
    # HELPERS
    # =====================================================

    @staticmethod
    def _get_session(request):

        cookie = request.headers.get("Cookie", "")

        session_id = None

        for item in cookie.split(";"):

            item = item.strip()

            if item.startswith("session_id="):
                session_id = item.split("=", 1)[1]
                break

        return get_session(session_id)

    @staticmethod
    def _json(request, payload, status=200):

        body = json.dumps(payload).encode("utf-8")

        request.send_response(status)
        request.send_header("Content-Type", "application/json; charset=utf-8")
        request.send_header("Content-Length", str(len(body)))
        request.end_headers()
        request.wfile.write(body)

    @staticmethod
    def _read_form(request):

        content_length = int(request.headers.get("Content-Length", 0))

        body = request.rfile.read(content_length).decode("utf-8")

        parsed = parse_qs(body)

        return {key: values[0].strip() for key, values in parsed.items()}

    @staticmethod
    def _authenticate(request):
        """
        Returns the logged-in doctor's id, or None after sending the
        error response itself. The doctor id ALWAYS comes from the
        session -- never from the form.
        """

        session = TimeSlotController._get_session(request)

        if not session:

            TimeSlotController._json(
                request,
                {
                    "success": False,
                    "message": "Your session has expired. Please log in again.",
                    "redirect": "/login"
                },
                401
            )
            return None

        if session["user_type"] != "doctor":

            TimeSlotController._json(
                request,
                {
                    "success": False,
                    "message": "Only doctors can manage time slots."
                },
                403
            )
            return None

        return session["user_id"]

    @staticmethod
    def _doctor_status(cursor, doctor_id):

        cursor.execute(
            "SELECT status FROM doctor WHERE doctor_id = ?",
            (doctor_id,)
        )

        row = cursor.fetchone()

        return row[0] if row else None

    @staticmethod
    def _parse_slot(form):
        """
        Validates date/start/end. Returns (error, (date, start, end)).
        Times are normalised to zero-padded HH:MM so plain string
        comparison in SQL orders them correctly.
        """

        try:
            slot_date = date.fromisoformat(form.get("date", ""))
        except ValueError:
            return "Enter a valid date.", None

        try:
            start = datetime.strptime(form.get("start_time", ""), "%H:%M")
            end = datetime.strptime(form.get("end_time", ""), "%H:%M")
        except ValueError:
            return "Enter valid start and end times.", None

        if end <= start:
            return "End time must be after start time.", None

        now = datetime.now()

        if slot_date < now.date():
            return "Time slots can't be set in the past.", None

        if slot_date == now.date() and start.time() <= now.time():
            return "That start time has already passed today.", None

        return None, (
            slot_date.isoformat(),
            start.strftime("%H:%M"),
            end.strftime("%H:%M")
        )

    @staticmethod
    def _overlaps(cursor, doctor_id, slot_date, start, end, exclude_slot_id=None):

        query = """
            SELECT 1 FROM time_slot
            WHERE doctor_id = ?
              AND date = ?
              AND start_time < ?
              AND end_time > ?
        """
        params = [doctor_id, slot_date, end, start]

        if exclude_slot_id is not None:
            query += " AND slot_id != ?"
            params.append(exclude_slot_id)

        cursor.execute(query, params)

        return cursor.fetchone() is not None

    @staticmethod
    def _active_bookings(cursor, slot_id):

        cursor.execute(
            f"""
            SELECT COUNT(*) FROM appointment
            WHERE slot_id = ?
              AND status NOT IN {INACTIVE_APPOINTMENT_STATES}
            """,
            (slot_id,)
        )

        return cursor.fetchone()[0]

    # =====================================================
    # GET /doctor/availability
    # =====================================================

    @staticmethod
    def show(request):

        session = TimeSlotController._get_session(request)

        if not session:

            request.send_response(302)
            request.send_header("Location", "/login")
            request.end_headers()
            return

        if session["user_type"] != "doctor":

            request.send_response(403)
            request.send_header("Content-Type", "text/html; charset=utf-8")
            request.end_headers()
            request.wfile.write(b"<h1>Access Denied</h1>")
            return

        doctor_id = session["user_id"]

        connection = get_connection()

        try:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT
                    doctor.name,
                    doctor.specialization,
                    doctor.status,
                    doctor_bio.profile_image
                FROM doctor
                LEFT JOIN doctor_bio
                    ON doctor.doctor_id = doctor_bio.doctor_id
                WHERE doctor.doctor_id = ?
                """,
                (doctor_id,)
            )

            doctor = cursor.fetchone()

            if not doctor:

                request.send_response(404)
                request.send_header("Content-Type", "text/html; charset=utf-8")
                request.end_headers()
                request.wfile.write(b"<h1>Doctor not found</h1>")
                return

            cursor.execute(
                f"""
                SELECT
                    t.slot_id,
                    t.date,
                    t.start_time,
                    t.end_time,
                    t.is_available,
                    (
                        SELECT COUNT(*) FROM appointment a
                        WHERE a.slot_id = t.slot_id
                          AND a.status NOT IN {INACTIVE_APPOINTMENT_STATES}
                    ) AS active_bookings
                FROM time_slot t
                WHERE t.doctor_id = ?
                ORDER BY t.date, t.start_time
                """,
                (doctor_id,)
            )

            rows = cursor.fetchall()

        finally:
            connection.close()

        # slot_id, date, start, end, status
        slots = []

        for slot_id, slot_date, start, end, is_available, bookings in rows:

            if bookings > 0:
                status = "booked"
            elif is_available:
                status = "available"
            else:
                status = "unavailable"

            slots.append((slot_id, slot_date, start, end, status))

        name, specialization, doctor_status, profile_image = doctor

        is_certified = (doctor_status == "Certified")

        if doctor_status == "Rejected":
            notice_text = (
                "Your registration was not approved, so you can't create "
                "time slots. Please contact an administrator."
            )
        else:
            notice_text = (
                "Your account is awaiting verification by an administrator. "
                "please fill up all the info in your profile for verification, WARNING ! insufficient info account will be rejected."
                "You'll be able to create time slots as soon as you're certified."
            )

        TemplateEngine.render(
            request,
            "timeslot.html",
            {
                "title": "Availability",
                "name": name,
                "specialization": specialization,
                "profile_image": profile_image or "/static/img/doctor.jpeg",
                "slots": slots,
                "slot_count": len(slots),
                "notice_display": "none" if is_certified else "flex",
                "notice_text": notice_text,
                "form_display": "block" if is_certified else "none"
            }
        )

    # =====================================================
    # POST /doctor/slots/add
    # =====================================================

    @staticmethod
    def add(request):

        doctor_id = TimeSlotController._authenticate(request)

        if doctor_id is None:
            return

        form = TimeSlotController._read_form(request)

        error, parsed = TimeSlotController._parse_slot(form)

        if error:
            TimeSlotController._json(
                request, {"success": False, "message": error}, 400
            )
            return

        slot_date, start, end = parsed

        connection = get_connection()

        try:
            cursor = connection.cursor()

            # Certification is checked against the DB on every request
            # (not cached in the session) so a revoked doctor is
            # blocked immediately.
            if TimeSlotController._doctor_status(cursor, doctor_id) != "Certified":

                TimeSlotController._json(
                    request,
                    {
                        "success": False,
                        "message": "Only certified doctors can create time slots."
                    },
                    403
                )
                return

            if TimeSlotController._overlaps(
                cursor, doctor_id, slot_date, start, end
            ):

                TimeSlotController._json(
                    request,
                    {
                        "success": False,
                        "message": "This overlaps one of your existing time slots."
                    },
                    409
                )
                return

            cursor.execute(
                """
                INSERT INTO time_slot (doctor_id, date, start_time, end_time)
                VALUES (?, ?, ?, ?)
                """,
                (doctor_id, slot_date, start, end)
            )

            connection.commit()

            slot_id = cursor.lastrowid

        finally:
            connection.close()

        TimeSlotController._json(
            request,
            {
                "success": True,
                "slot_id": slot_id,
                "message": "Time slot added."
            }
        )

    # =====================================================
    # POST /doctor/slots/update
    # =====================================================

    @staticmethod
    def update(request):

        doctor_id = TimeSlotController._authenticate(request)

        if doctor_id is None:
            return

        form = TimeSlotController._read_form(request)

        try:
            slot_id = int(form.get("slot_id", ""))
        except ValueError:
            TimeSlotController._json(
                request, {"success": False, "message": "Invalid slot."}, 400
            )
            return

        status = form.get("status", "available")

        if status not in ("available", "unavailable"):
            TimeSlotController._json(
                request, {"success": False, "message": "Invalid status."}, 400
            )
            return

        error, parsed = TimeSlotController._parse_slot(form)

        if error:
            TimeSlotController._json(
                request, {"success": False, "message": error}, 400
            )
            return

        slot_date, start, end = parsed

        connection = get_connection()

        try:
            cursor = connection.cursor()

            # Ownership: the slot must belong to THIS doctor.
            cursor.execute(
                "SELECT 1 FROM time_slot WHERE slot_id = ? AND doctor_id = ?",
                (slot_id, doctor_id)
            )

            if not cursor.fetchone():

                TimeSlotController._json(
                    request,
                    {"success": False, "message": "Time slot not found."},
                    404
                )
                return

            if TimeSlotController._doctor_status(cursor, doctor_id) != "Certified":

                TimeSlotController._json(
                    request,
                    {
                        "success": False,
                        "message": "Only certified doctors can manage time slots."
                    },
                    403
                )
                return

            if TimeSlotController._active_bookings(cursor, slot_id) > 0:

                TimeSlotController._json(
                    request,
                    {
                        "success": False,
                        "message": "This slot has a booked appointment and can't be changed."
                    },
                    409
                )
                return

            if TimeSlotController._overlaps(
                cursor, doctor_id, slot_date, start, end, exclude_slot_id=slot_id
            ):

                TimeSlotController._json(
                    request,
                    {
                        "success": False,
                        "message": "This overlaps one of your existing time slots."
                    },
                    409
                )
                return

            cursor.execute(
                """
                UPDATE time_slot
                SET date = ?, start_time = ?, end_time = ?, is_available = ?
                WHERE slot_id = ? AND doctor_id = ?
                """,
                (
                    slot_date,
                    start,
                    end,
                    1 if status == "available" else 0,
                    slot_id,
                    doctor_id
                )
            )

            connection.commit()

        finally:
            connection.close()

        TimeSlotController._json(
            request, {"success": True, "message": "Time slot updated."}
        )

    # =====================================================
    # POST /doctor/slots/delete
    # =====================================================

    @staticmethod
    def delete(request):

        doctor_id = TimeSlotController._authenticate(request)

        if doctor_id is None:
            return

        form = TimeSlotController._read_form(request)

        try:
            slot_id = int(form.get("slot_id", ""))
        except ValueError:
            TimeSlotController._json(
                request, {"success": False, "message": "Invalid slot."}, 400
            )
            return

        connection = get_connection()

        try:
            cursor = connection.cursor()

            cursor.execute(
                "SELECT 1 FROM time_slot WHERE slot_id = ? AND doctor_id = ?",
                (slot_id, doctor_id)
            )

            if not cursor.fetchone():

                TimeSlotController._json(
                    request,
                    {"success": False, "message": "Time slot not found."},
                    404
                )
                return

            # Any appointment row -- even a cancelled one -- still points
            # at this slot, and SQLite doesn't enforce foreign keys by
            # default, so deleting would silently orphan it.
            cursor.execute(
                "SELECT COUNT(*) FROM appointment WHERE slot_id = ?",
                (slot_id,)
            )

            if cursor.fetchone()[0] > 0:

                TimeSlotController._json(
                    request,
                    {
                        "success": False,
                        "message": (
                            "This slot has appointment history and can't be "
                            "deleted. Mark it unavailable instead."
                        )
                    },
                    409
                )
                return

            cursor.execute(
                "DELETE FROM time_slot WHERE slot_id = ? AND doctor_id = ?",
                (slot_id, doctor_id)
            )

            connection.commit()

        finally:
            connection.close()

        TimeSlotController._json(
            request, {"success": True, "message": "Time slot deleted."}
        )