class SessionManager:

    def __init__(self):

        self.sessions = {}

        self.counter = 1

        self.current_session = None

    def add(self, sock, client_info):

        session_id = self.counter

        self.sessions[session_id] = {
            "socket": sock,
            "info": client_info,
        }

        self.counter += 1

        print("TOTAL SESSIONS:", len(self.sessions))
        return session_id

    def remove(self, session_id):

        if session_id in self.sessions:

            self.sessions[session_id]["socket"].close()

            del self.sessions[session_id]

    def list_sessions(self):

        if not self.sessions:
            print("No active sessions")

            return

        for sid, session in self.sessions.items():
            info = session["info"]

            print(f"[{sid}] " f"{info['hostname']} " f"{info['os']} " f"{info['user']}")

    def interact(self, session_id):

        if session_id not in self.sessions:
            print("Session not found")
            return

        self.current_session = session_id

        print(f"Interacting with session {session_id}")
