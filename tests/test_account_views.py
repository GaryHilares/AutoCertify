import pytest
from app import create_app
from dotenv import load_dotenv
from flask.testing import FlaskClient
from pytest_mock import MockerFixture
from tests.mocks.mock_user import MockUser
from tests.mocks.mock_utils import MockUtils


@pytest.fixture
def client() -> FlaskClient:
    """
    Configures the application and creates a testing `FlaskClient` from it.

    Returns:
        A testing `FlaskClient` that can be used in tests through fixtures.
    """
    load_dotenv()
    app = create_app()
    app.config.update({"TESTING": True})
    yield app.test_client()


def test_login_view(mocker: MockerFixture, client: FlaskClient) -> None:
    """
    Tests the login functionality (located at /account/login).

    Args:
        mocker: A mocking interface provided by `pytest-mock`.
        client: A Flask test client provided by a `pytest`'s fixture.
    Raises:
        AssertionError: If any of the tests fails.
    """
    # Mock required functions from the User class
    mocker.patch("app.models.user.User.get_by_name", wraps=MockUser.get_by_name)

    # Test that log in view is displayed correctly
    response = client.get("/account/login")
    assert b"Log in" in response.data

    # Test that user can't login without username or password
    response = client.post("/account/login")
    assert b"Error" in response.data

    # Test that user can't log in with inexistent account
    response = client.post(
        "/account/login",
        data={
            "name": "someuser",
            "password": "incorrectpassword",
        },
    )
    assert b"Incorrect credentials" in response.data

    # Test that user can log in with right credentials
    response = client.post(
        "/account/login",
        data={
            "name": "someuser",
            "password": "1234",
        },
    )
    assert b"Success" in response.data


def test_register_view(mocker: MockerFixture, client: FlaskClient) -> None:
    """
    Tests the register functionality (located at /account/register).

    Args:
        mocker: A mocking interface provided by `pytest-mock`.
        client: A Flask test client provided by a `pytest`'s fixture.
    Raises:
        AssertionError: If any of the tests fails.
    """
    # Mock required functions from the User class
    mocker.patch("app.models.user.User.create", wraps=MockUser.create)
    mocker.patch("app.models.user.User.get_by_name", wraps=MockUser.get_by_name)

    # Test that log in view is displayed correctly
    response = client.get("/account/register")
    assert b"Register" in response.data

    # Test that user can't register without a password
    response = client.post("/account/register", data={"name": "newuser"})
    assert b"Error" in response.data

    # Test that user can't register with a password with invalid characters
    response = client.post(
        "/account/register", data={"name": "newuser", "password": "μ's-is-the-best"}
    )
    assert b"Error" in response.data

    # Test that user can't register with a password that is too short
    response = client.post(
        "/account/register",
        data={
            "name": "newuser",
            "password": "123",
        },
    )
    assert b"Error" in response.data

    # Test that user can't register with a password that is too short
    response = client.post(
        "/account/register",
        data={
            "name": "newuser",
            "password": "12345678901234567890123456789012345678901234567890.50",
        },
    )
    assert b"Error" in response.data

    # Test that user can't register with username that already exists
    response = client.post(
        "/account/register", data={"name": "someuser", "password": "1234"}
    )
    assert b"Error" in response.data

    # Test that user can register
    response = client.post(
        "/account/register", data={"name": "newuser", "password": "newpassword"}
    )
    assert b"Success" in response.data


def test_verification_view(mocker: MockerFixture, client: FlaskClient) -> None:
    """
    Tests the verification functionality (/account/verify).

    Args:
        mocker: A mocking interface provided by `pytest-mock`.
        client: A Flask test client provided by a `pytest`'s fixture.
    Raises:
        AssertionError: If any of the tests fails.
    """
    mocker.patch("app.utils.Utils.check_metadata", wraps=MockUtils.check_metadata)
    mocker.patch("app.models.user.User.get_by_id", wraps=MockUser.get_by_id)
    mocker.patch("app.models.user.User.get_by_name", wraps=MockUser.get_by_name)

    # Check that endpoint cannot be accessed without getting logged in
    response = client.get("/account/verify")
    assert response.status_code == 302

    # Logins are kept within this block
    with client.application.test_request_context():
        # Log in into "anotheruser", who has not set a website for verification
        response = client.post(
            "/account/login", data={"name": "anotheruser", "password": "1234"}
        )
        assert b"Success" in response.data

        # Test that verification view is displayed correctly
        response = client.get("/account/verify")
        assert b"Verify" in response.data

        # Test that account cannot be verified without an URL
        response = client.post("/account/verify")
        assert b"Error" in response.data

        # Test that account cannot be verified with a non-existent URL
        response = client.post("/account/verify", data={"url": "doesnotexi.st"})
        assert b"Error" in response.data

        # Test that account cannot be verified with valid URL that does not have correct metadata
        response = client.post("/account/verify", data={"url": "example.com"})
        assert b"Error" in response.data

    # Logins are kept within this block
    with client.application.test_request_context():
        # Log in into "someuser", who has set "example.com" appropiately for verification
        response = client.post(
            "/account/login", data={"name": "someuser", "password": "1234"}
        )
        assert b"Success" in response.data

        # Test that verification view is displayed correctly
        response = client.get("/account/verify")
        assert b"Verify" in response.data

        # Test that account can be verified
        response = client.post("/account/verify", data={"url": "example.com"})
