from rat.commands.command_registry import CommandRegistry


class DummyClient:
    pass


def test_registry_contains_commands():
    registry = CommandRegistry(DummyClient())

    # adapte selon tes commandes réelles
    expected_commands = [
        "help",
        "download",
        "ipconfig",
        "keylogger",
        "upload",
        "screenshot",
        "search",
        "hashdump",
        "shell",
        "record_audio",
        "webcam_snapshot",
        "webcam_stream",
    ]

    for cmd in expected_commands:
        assert registry.get(cmd) is not None


def test_registry_get_unknown_command():
    registry = CommandRegistry(DummyClient())

    assert registry.get("unknown") is None


def test_register_override():
    registry = CommandRegistry(DummyClient())

    class FakeCommand:
        name = "help"

    fake = FakeCommand()
    registry.register(fake)

    assert registry.get("help") == fake
