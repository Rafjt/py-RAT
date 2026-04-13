from server.server import SSLServer


def main():

    server = SSLServer(
        host="0.0.0.0",
        port=8888,
        server_cert="../../certs/cert.pem",
        server_key="../../certs/key.pem",
        client_cert="../../certs/cert.pem",
    )

    server.start()


if __name__ == "__main__":
    main()
