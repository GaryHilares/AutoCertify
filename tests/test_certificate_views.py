"""
Includes tests for the views under /certificate/ (certificate.* endpoints) of the Certificate
Automation Flask app. To collect and run these tests, you should use `pytest`'s test discovery.
"""
from types import SimpleNamespace
from flask.testing import FlaskClient
from pytest_mock import MockerFixture
from tests.mocks.mock_user import MockUser
from tests.mocks.mock_certificate import MockCertificate


def test_create_view(mocker: MockerFixture, client: FlaskClient) -> None:
    """
    Tests the certificate creation functionality (located at /certificate/create).

    Args:
        mocker: A mocking interface provided by `pytest-mock`.
        client: A Flask test client provided by a `pytest`'s fixture.
    Raises:
        AssertionError: If any of the tests fails.
    """
    # Mock required functions
    mocker.patch("app.models.user.User.get_by_id", wraps=MockUser.get_by_id)
    mocker.patch("app.models.user.User.get_by_name", wraps=MockUser.get_by_name)
    mocker.patch(
        "app.models.certificate.Certificate.create", wraps=MockCertificate.create
    )

    # Test that create view cannot be seen without logging in
    response = client.get("/certificate/create")
    assert response.status_code == 302

    with client.application.test_request_context():
        # Log in as "someuser"
        response = client.post(
            "/account/login", data={"name": "someuser", "password": "1234"}
        )
        assert b"Success" in response.data

        # Check that user can't create a certificate without a name or title
        response = client.post(
            "/certificate/create", data={"certificate-title": "sometitle"}
        )
        assert b"Error" in response.data

        # Check that user can create a certificate with name and title
        response = client.post(
            "/certificate/create",
            data={"certificate-name": "goodperson", "certificate-title": "sometitle"},
        )
        assert b"Success" in response.data


def test_view_view(mocker: MockerFixture, client: FlaskClient) -> None:
    """
    Tests the certificate viewing functionality (located at
    /certificate/<string:certificate_id>/view).

    Args:
        mocker: A mocking interface provided by `pytest-mock`.
        client: A Flask test client provided by a `pytest`'s fixture.
    Raises:
        AssertionError: If any of the tests fails.
    """
    # Mock required functions
    mocker.patch(
        "app.models.certificate.Certificate.get_by_id", wraps=MockCertificate.get_by_id
    )

    # Test that a view with a non-existent id cannot be seen
    response = client.get("/certificate/idthatdoesnotexist/view")
    assert response.status_code == 403

    # Test that appropiate view can be seen without logging in
    response = client.get("/certificate/anid/view")
    assert response.status_code == 200


def test_download_view(mocker: MockerFixture, client: FlaskClient) -> None:
    """
    Tests the certificate downloading functionality (located at
    /certificate/<string:certificate_id>/download).

    Args:
        mocker: A mocking interface provided by `pytest-mock`.
        client: A Flask test client provided by a `pytest`'s fixture.
    Raises:
        AssertionError: If any of the tests fails.
    """
    # Mock required functions from the User class
    mocker.patch("app.models.user.User.get_by_id", wraps=MockUser.get_by_id)
    mocker.patch(
        "app.models.certificate.Certificate.get_by_id", wraps=MockCertificate.get_by_id
    )

    # TODO: Mock app.certificate_builder.CertificateBuilder

    # Test that a view with a non-existent id cannot be seen
    response = client.get("/certificate/idthatdoesnotexist/download")
    assert response.status_code == 403

    # Test that appropiate view can be seen without logging in
    response = client.get("/certificate/anid/download")
    assert response.status_code == 200
