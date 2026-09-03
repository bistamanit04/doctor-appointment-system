import secrets


sessions = {}


def create_session(user_type, user_id):

    session_id = secrets.token_hex(16)

    sessions[session_id] = {
        "user_type": user_type,
        "user_id": user_id
    }

    return session_id


def get_session(session_id):

    return sessions.get(session_id)


def delete_session(session_id):

    if session_id in sessions:
        del sessions[session_id]