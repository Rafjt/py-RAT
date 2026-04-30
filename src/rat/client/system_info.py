# Ce module expose une fonction utilitaire permettant de récupérer
# des informations système de base sur la machine courante.
# Ces informations sont typiquement utilisées pour identifier un client
# lors de la connexion à un serveur.

import platform
import socket
import getpass


def get_system_info():

    return {
        # Nom de la machine sur le réseau
        "hostname": socket.gethostname(),
        # Système d’exploitation (Windows, Linux, Darwin, etc.)
        "os": platform.system(),
        # Version / release de l’OS
        "release": platform.release(),
        # Nom de l’utilisateur courant
        "user": getpass.getuser(),
        # Architecture CPU (x86_64, arm64, etc.)
        "architecture": platform.machine(),
    }
