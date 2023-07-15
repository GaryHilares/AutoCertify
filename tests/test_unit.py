import pytest
from app import create_app
from dotenv import load_dotenv


@pytest.fixture
def client():
    load_dotenv()
    app = create_app()
    app.config.update({"TESTING": True})
    yield app.test_client()


def test_login_view(client):
    # Test that log in view is displayed correctly
    response = client.get("/account/login")
    assert b"Log in" in response.data

    # Test that user can't log in with inexistent account
    response = client.post(
        "/account/login",
        data={
            "name": "test",
            "password": "1234",
        },
    )

    assert b"Incorrect credentials" in response.data
