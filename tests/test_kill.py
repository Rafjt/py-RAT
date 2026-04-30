from unittest.mock import MagicMock
from rat.server.server import SSLServer


def create_server():
    return SSLServer(
        host="127.0.0.1",
        port=0,
        server_cert="certs/cert.pem",
        server_key="certs/key.pem",
        client_cert="certs/cert.pem",
    )


def test_kill_valid_session():
    server = create_server()

    mock_sock = MagicMock()

    session = MagicMock()
    session.sock = mock_sock

    server._sessions.add_session = MagicMock(return_value=session)
    server._sessions.get_session = MagicMock(return_value=session)
    server._sessions.remove_session = MagicMock()

    server._handle_kill("kill 1")

    # Vérifie envoi du "exit"
    assert mock_sock.sendall.called

    # Vérifie suppression session
    server._sessions.remove_session.assert_called_with(1)


def test_kill_invalid_id():
    server = create_server()

    server._sessions.get_session = MagicMock(return_value=None)

    # doit pas crash
    server._handle_kill("kill 999")


def test_kill_bad_format():
    server = create_server()

    # doit pas crash
    server._handle_kill("kill")
    server._handle_kill("kill abc")
