"""
Declares a blueprint which holds the views for actions related to certificates. All views are
prefixed by `/certificate`.
"""

from flask import Blueprint, request, render_template, send_file, url_for
from flask.blueprints import BlueprintSetupState
from flask.typing import ResponseReturnValue
from flask_bcrypt import Bcrypt
from flask_login import current_user, login_required
from bson.objectid import ObjectId
from bson.errors import InvalidId
from app.certificate_builder import CertificateBuilder
from app.models.certificate import Certificate

certificate_blueprint = Blueprint(
    "certificate", __name__, template_folder="templates", url_prefix="/certificate"
)

# Initialize Flask extensions and later add app configuration
bcrypt = Bcrypt()


@certificate_blueprint.record_once
def on_load(state: BlueprintSetupState) -> None:
    """
    Adds app configuration to Flask extensions.

    Arguments:
        state: A state object created by Flask whose `app` attribute refers to the main Flask
        application.
    """
    bcrypt.init_app(state.app)


@certificate_blueprint.route("/create", methods=["GET", "POST"])
@login_required
def create() -> ResponseReturnValue:
    """
    Creates a new certificate. Accessing this view's route with GET will render a form to create a
    certificate. Accessing this view's route with POST will create a certificate with the arguments
    received.

    Returns:
        The certificate creation view if the route was accessed through GET. Otherwise it returns a
        view that shows whether the certificate creation was successful.
    """
    # If request method is GET, return form
    if request.method == "GET":
        return render_template("create-certificate.html")

    # Retrieve and check POST input
    certificate_name = request.form.get("certificate-name", None)
    certificate_title = request.form.get("certificate-title", None)
    if not certificate_name or not certificate_title:
        return (
            render_template(
                "error.html", message="A field is missing in your request."
            ),
            400,
        )

    # Update database with new certificate
    insert_data = Certificate.create(
        certificate_name, certificate_title, ObjectId(current_user.id_)
    ).save()

    # Return success message
    return render_template(
        "success.html",
        message=f"Certificate with the id {insert_data.inserted_id} created successfully",
    )


@certificate_blueprint.route("/<string:certificate_id>/view", methods=["GET"])
def view(certificate_id: str) -> ResponseReturnValue:
    """
    Renders the information of the certificate whose `_id` matches the path parameter `id`.

    Returns:
        A page displaying the information about the certificate.
    """
    # Retrieve and check GET input
    if not certificate_id:
        return (
            render_template("error.html", message="ID is missing in your request."),
            403,
        )

    # Check that the ID is in valid format and exists and retrieve certificate
    print(certificate_id)
    certificate = Certificate.get_by_id(certificate_id)
    if not certificate:
        return render_template("error.html", message="ID was not found."), 403

    # Check that certifier is valid and retrieve its information
    certifier = certificate.get_certifier()
    if not certifier:
        return (
            render_template(
                "error.html",
                critical_error=True,
                message="Certificate data is corrupt.",
            ),
            500,
        )

    # Return a display of the results
    return render_template(
        "view-certificate.html",
        certificate={
            "id": certificate.id_,
            "name": certificate.name,
            "title": certificate.title,
        },
        certifier={
            "id": certifier.id_,
            "name": certifier.name,
            "url": certifier.url,
        },
        download_url=url_for(
            "certificate.download", certificate_id=str(certificate_id)
        ),
    )


@certificate_blueprint.route("/<string:certificate_id>/download", methods=["GET"])
def download(certificate_id: str) -> ResponseReturnValue:
    """
    Downloads a PDF with the information of the certificate whose `_id` matches the path parameter
    `id`.
    """
    # Retrieve and check GET input
    if not certificate_id:
        return (
            render_template("error.html", message="ID is missing in your request."),
            403,
        )

    # Check that the ID exists and is in correct format and retrieve certificate
    certificate = Certificate.get_by_id(certificate_id)
    if not certificate:
        return render_template("error.html", message="ID was not found."), 403

    # Check that certifier is valid and retrieve its information
    certifier = certificate.get_certifier()
    if not certifier:
        return (
            render_template(
                "error.html",
                critical_error=True,
                message="Certificate data is corrupt.",
            ),
            500,
        )

    # Generate certificate
    certificate_pdf = (
        CertificateBuilder({})
        .draw_template()
        .add_certificate_data(certificate, certifier)
        .add_qrcode(
            url_for(
                "certificate.view", _external=True, certificate_id=str(certificate_id)
            )
        )
        .save()
    )

    # Return PDF
    return send_file(
        certificate_pdf,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="Certificate.pdf",
    )
