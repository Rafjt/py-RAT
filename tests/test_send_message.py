from unittest.mock import MagicMock
from rat.server.server import SSLServer


def test_send_message():
    server = SSLServer(
        "127.0.0.1", 0, "certs/cert.pem", "certs/key.pem", "certs/cert.pem"
    )

    mock_sock = MagicMock()

    server._send_message(mock_sock, "hello")

    calls = mock_sock.sendall.call_args_list

    # premier send = taille
    assert b"5\n" in calls[0][0][0]

    # second send = contenu
    assert b"hello" in calls[1][0][0]
