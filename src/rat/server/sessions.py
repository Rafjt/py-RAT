from dataclasses import dataclass
import threading


@dataclass
class Session:

    id: int
    sock: object
    hostname: str
    os: str
    user: str
    release: str


class SessionManager:

    def __init__(self):

        self._sessions = {}

        self._counter = 1

        self._lock = threading.Lock()

        self._active_session_id = None

    # -------------------------

    def add_session(
        self,
        sock,
        info,
    ):

        with self._lock:

            session_id = self._counter

            session = Session(
                id=session_id,
                sock=sock,
                hostname=info["hostname"],
                os=info["os"],
                user=info["user"],
                release=info["release"],
            )

            self._sessions[session_id] = session

            self._counter += 1

            return session

    # -------------------------

    def remove_session(self, session_id):

        with self._lock:

            if session_id in self._sessions:

                del self._sessions[session_id]

                if self._active_session_id == session_id:
                    self._active_session_id = None

    # -------------------------

    def list_sessions(self):

        return list(self._sessions.values())

    # -------------------------

    def get_session(
        self,
        session_id,
    ):

        return self._sessions.get(session_id)

    # -------------------------

    def set_active(
        self,
        session_id,
    ):

        if session_id in self._sessions:

            self._active_session_id = session_id

            return True

        return False

    # -------------------------

    def get_active(self):

        if self._active_session_id is None:
            return None

        return self._sessions.get(self._active_session_id)
