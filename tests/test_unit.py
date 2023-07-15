import pytest
from app import create_app
from dotenv import load_dotenv
from tests.mocks.mock_user import MockUser


@pytest.fixture
def client():
    load_dotenv()
    app = create_app()
    app.config.update({"TESTING": True})
    yield app.test_client()


def test_login_view(mocker, client) -> None:
    """
    Tests the login functionality (/account/login).

    Args:
        mocker: A mocking interface provided by `pytest-mock`.
        client: A Flask test client provided by a `pytest`'s fixture.
    Raises:
        AssertionError: If any of the tests fails.
    """
    # Mock that always
    mocker.patch("app.models.user.User.get_by_name", wraps=MockUser.get_by_name)

    # Test that log in view is displayed correctly
    response = client.get("/account/login")
    assert b"Log in" in response.data

    # Test that user can't log in with inexistent account
    response = client.post(
        "/account/login",
        data={
            "name": "someuser",
            "password": "incorrectpassword",
        },
    )
    assert b"Incorrect credentials" in response.data

    # Test that user can log in with inexistent account
    response = client.post(
        "/account/login",
        data={
            "name": "someuser",
            "password": "1234",
        },
    )
    assert b"Success" in response.data
