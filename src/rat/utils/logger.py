# Module de logging centralisé pour l'application py-RAT

import logging
from pathlib import Path


def setup_logger():
    # Récupère le chemin du dossier courant du fichier logger.py
    base_dir = Path(__file__).resolve().parent

    # Définit le fichier de log (rat.log dans le même dossier)
    log_path = base_dir / "rat.log"

    # Création / récupération du logger principal de l'application
    logger = logging.getLogger("rat")

    # Niveau de log global (INFO et plus graves)
    logger.setLevel(logging.INFO)

    # Handler qui écrit les logs dans un fichier
    handler = logging.FileHandler(log_path)

    # Format des logs : timestamp + niveau + message
    formatter = logging.Formatter("[%(asctime)s] - %(levelname)s: %(message)s")

    # Application du format au handler
    handler.setFormatter(formatter)

    # Ajout du handler au logger
    logger.addHandler(handler)

    # Retourne le logger configuré pour être utilisé dans toute l'app
    return logger
