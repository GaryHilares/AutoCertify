from flask.testing import FlaskClient
import pytest
from app import create_app
from dotenv import load_dotenv


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
