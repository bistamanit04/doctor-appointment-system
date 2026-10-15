import html
from datetime import date, datetime, timedelta

from template_engine import TemplateEngine
from database import get_connection
from controllers.timeslotController import INACTIVE_APPOINTMENT_STATES


# How many upcoming slots to show on each doctor's card
MAX_SLOTS_SHOWN = 5


def format_slot_label(slot_date, start_time, today):
    """
    "2026-10-16", "14:00"  ->  "Tomorrow, 2:00 PM"
    Built by hand (no %-I) so it also works on Windows.
    """

    slot_day = date.fromisoformat(slot_date)

    if slot_day == today:
        day_label = "Today"
    elif slot_day == today + timedelta(days=1):
        day_label = "Tomorrow"
    else:
        day_label = f"{slot_day.day} {slot_day.strftime('%b')}"

    hour, minute = (int(part) for part in start_time.split(":"))

    suffix = "AM" if hour < 12 else "PM"
    hour_12 = hour % 12 or 12

    return f"{day_label}, {hour_12}:{minute:02d} {suffix}"


def build_slot_chips(doctor_status, slots, today):
    """
    Returns the HTML for one doctor's slot chips. The template engine
    has no nested loops or {% if %}, so this is built here and dropped
    into the card as a single value.
    """

    if doctor_status != "Certified":
        return '<span class="slot-chip slot-none">Not accepting bookings yet</span>'

    chips = []

    for slot_id, slot_date, start_time in slots:

        try:
            label = format_slot_label(slot_date, start_time, today)
        except ValueError:
            continue  # malformed row -- skip rather than break the page

        chips.append(
            f'<span class="slot-chip" data-slot-id="{int(slot_id)}">'
            f'{html.escape(label)}</span>'
        )

    if not chips:
        return '<span class="slot-chip slot-none">No slots available</span>'

    return "".join(chips)


class DoctorController:

    @staticmethod
    def DOClist(request):

        connection = get_connection()

        try:
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

            doctor_rows = cursor.fetchall()

            now = datetime.now()
            today = now.date()
            now_hhmm = now.strftime("%H:%M")

            # Every free, upcoming slot, soonest first. "Free" means
            # marked available AND not held by an active appointment
            # (same rule the Availability page uses for "booked").
            cursor.execute(
                f"""
                SELECT t.doctor_id, t.slot_id, t.date, t.start_time
                FROM time_slot t
                WHERE t.is_available = 1
                  AND t.date >= ?
                  AND NOT EXISTS (
                      SELECT 1 FROM appointment a
                      WHERE a.slot_id = t.slot_id
                        AND a.status NOT IN {INACTIVE_APPOINTMENT_STATES}
                  )
                ORDER BY t.date, t.start_time
                """,
                (today.isoformat(),)
            )

            upcoming = {}

            for doctor_id, slot_id, slot_date, start_time in cursor.fetchall():

                # Today's slots that have already started are gone
                if slot_date == today.isoformat() and start_time <= now_hhmm:
                    continue

                bucket = upcoming.setdefault(doctor_id, [])

                if len(bucket) < MAX_SLOTS_SHOWN:
                    bucket.append((slot_id, slot_date, start_time))

        finally:
            connection.close()

        # Each row gets one extra field at index 13: the slot chips HTML
        doctors = []

        for row in doctor_rows:

            chips_html = build_slot_chips(
                row[5],
                upcoming.get(row[0], []),
                today
            )

            doctors.append(tuple(row) + (chips_html,))

        TemplateEngine.render(
            request,
            "FindDoctor.html",
            {
                "title": "Find Doctors",
                "doctors": doctors
            }
        )