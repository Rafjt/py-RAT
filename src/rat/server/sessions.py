# Ce module gère les sessions actives du serveur.
# Chaque session correspond à un client connecté (socket + infos système).
# Il permet de créer, stocker, lister et sélectionner une session active.

from dataclasses import dataclass
import threading


# Représente une session individuelle avec un client connecté
@dataclass
class Session:

    id: int  # identifiant unique de la session
    sock: object  # socket réseau associé au client
    hostname: str  # nom de la machine cliente
    os: str  # système d'exploitation du client
    user: str  # utilisateur connecté côté client
    release: str  # version du système


class SessionManager:

    def __init__(self):

        # Dictionnaire des sessions actives {id: Session}
        self._sessions = {}

        # Compteur pour générer des IDs uniques de session
        self._counter = 1

        # Lock pour sécuriser l’accès multi-thread aux sessions
        self._lock = threading.Lock()

        # ID de la session actuellement "active" (utilisée par défaut pour les commandes)
        self._active_session_id = None

    # Ajoute une nouvelle session client au registre
    def add_session(
        self,
        sock,
        info,
    ):

        with self._lock:

            session_id = self._counter

            # Création de l'objet Session à partir des infos client
            session = Session(
                id=session_id,
                sock=sock,
                hostname=info["hostname"],
                os=info["os"],
                user=info["user"],
                release=info["release"],
            )

            self._sessions[session_id] = session

            # Incrément pour la prochaine session
            self._counter += 1

            return session

    # Supprime une session du gestionnaire
    def remove_session(self, session_id):

        with self._lock:

            if session_id in self._sessions:

                del self._sessions[session_id]

                # Si la session supprimée était active, on reset l’état actif
                if self._active_session_id == session_id:
                    self._active_session_id = None

    # Retourne la liste de toutes les sessions actives
    def list_sessions(self):

        return list(self._sessions.values())

    # Récupère une session spécifique par son ID
    def get_session(
        self,
        session_id,
    ):

        return self._sessions.get(session_id)

    # Définit la session active (celle ciblée par défaut pour les commandes)
    def set_active(
        self,
        session_id,
    ):

        if session_id in self._sessions:

            self._active_session_id = session_id

            return True

        return False

    # Retourne la session actuellement active
    def get_active(self):

        if self._active_session_id is None:
            return None

        return self._sessions.get(self._active_session_id)
