from rat.server.server import SSLServer


def test_recv_message():
    server = SSLServer(
        "127.0.0.1", 0, "certs/cert.pem", "certs/key.pem", "certs/cert.pem"
    )

    data = [b"5", b"\n", b"hello"]

    class FakeSocket:
        def recv(self, n):
            if data:
                return data.pop(0)
            return b""

    sock = FakeSocket()

    result = server._recv_message(sock)

    assert result == "hello"


def test_recv_invalid_size():
    server = SSLServer(
        "127.0.0.1", 0, "certs/cert.pem", "certs/key.pem", "certs/cert.pem"
    )

    data = [b"x", b"\n"]

    class FakeSocket:
        def recv(self, n):
            if data:
                return data.pop(0)
            return b""

    sock = FakeSocket()

    result = server._recv_message(sock)

    assert result is None
