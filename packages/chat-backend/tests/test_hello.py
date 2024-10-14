"""Hello unit test module."""

from chat_backend.hello import hello


def test_hello():
    """Test the hello function."""
    assert hello() == "Hello chat-backend"
