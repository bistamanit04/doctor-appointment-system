import secrets
from datetime import datetime, timedelta

from database import get_connection


# How long a session stays valid after it's created.
SESSION_LIFETIME = timedelta(hours=24)


def create_session(user_type, user_id):

    session_id = secrets.token_hex(16)

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO sessions (session_id, user_type, user_id)
        VALUES (?, ?, ?)
        """,
        (session_id, user_type, user_id)
    )

    connection.commit()
    connection.close()

    return session_id


def get_session(session_id):

    if not session_id:
        return None

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT user_type, user_id, created_at
        FROM sessions
        WHERE session_id = ?
        """,
        (session_id,)
    )

    row = cursor.fetchone()

    if not row:
        connection.close()
        return None

    # -----------------------------
    # CHECK EXPIRY
    # -----------------------------
    # SQLite's CURRENT_TIMESTAMP is stored as UTC text like
    # "2026-09-23 14:05:00" -- parse it and compare against now.

    created_at = datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S")
    age = datetime.utcnow() - created_at

    if age > SESSION_LIFETIME:

        # Session has expired -- delete it so it can't be
        # reused, and tell the caller there's no valid session.
        cursor.execute(
            "DELETE FROM sessions WHERE session_id = ?",
            (session_id,)
        )
        connection.commit()
        connection.close()

        return None

    connection.close()

    return {
        "user_type": row[0],
        "user_id": row[1]
    }


def delete_session(session_id):

    if not session_id:
        return

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM sessions
        WHERE session_id = ?
        """,
        (session_id,)
    )

    connection.commit()
    connection.close()