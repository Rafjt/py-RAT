import pytest
from rat.commands.search import SearchCommand


@pytest.fixture
def search_cmd():
    return SearchCommand()


def test_search_finds_file(search_cmd, tmp_path):

    # Arrange
    test_file = tmp_path / "password_notes.txt"
    test_file.write_text("secret")

    # Act
    result = search_cmd.execute(f"password {tmp_path}")

    # Assert
    assert "password_notes.txt" in result


def test_search_multiple_matches(search_cmd, tmp_path):

    (tmp_path / "config.json").write_text("a")
    (tmp_path / "app_config.yaml").write_text("b")

    result = search_cmd.execute(f"config {tmp_path}")

    assert "config.json" in result
    assert "app_config.yaml" in result


def test_search_no_results(search_cmd, tmp_path):

    (tmp_path / "file.txt").write_text("data")

    result = search_cmd.execute(f"password {tmp_path}")

    assert result == "No files found"


def test_search_invalid_path(search_cmd):

    result = search_cmd.execute("password /this/path/does/not/exist")

    assert result == "Path not found"


def test_search_usage_when_no_args(search_cmd):

    result = search_cmd.execute("")

    assert "Usage" in result
