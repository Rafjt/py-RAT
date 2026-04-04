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

    while True:

        message = input("client > ")

        client.send(message)


if __name__ == "__main__":
    main()
