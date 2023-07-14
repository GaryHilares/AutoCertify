"""
FILE
    certificates.py
DESCRIPTION
    Declares a blueprint which holds the views for actions related to certificates.
    All views are prefixed by `/certificate`.
"""

from flask import Blueprint, request, render_template, send_file
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
def on_load(state: any) -> None:
    """
    Adds app configuration to Flask extensions.

    Arguments:
        state (any)
            A state object created by Flask whose `app` attribute refers to the main
            Flask application.
    """
    bcrypt.init_app(state.app)


@certificate_blueprint.route("/create", methods=["GET", "POST"])
@login_required
def create_certificate():
    """
    Create a new certificate.

    Accessing this view's route with GET will render a form to create a
    a certificate. Accessing this view's route with POST will create a
    certificate with the arguments received.
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


@certificate_blueprint.route("/view", methods=["GET"])
def view_certificate():
    """
    View a certificate.

    Accessing this view's route with GET will render the information of the certificate
    whose `_id` matches the query parameter `id`.
    """
    # Retrieve and check GET input
    certificate_id = request.args.get("id", None)
    if not certificate_id:
        return (
            render_template("error.html", message="ID is missing in your request."),
            403,
        )

    # Check that the ID is in correct format
    try:
        certificate_id = ObjectId(certificate_id)
    except InvalidId:
        return render_template("error.html", message="The ID's format is invalid."), 403

    # Check that the ID exists and retrieve certificate
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
        download_url=f"{request.host_url}/certificate/download?id={certificate.id_}",
    )


@certificate_blueprint.route("/download", methods=["GET"])
def download_certificate():
    """
    View a certificate.

    Accessing this view's route with GET will download a PDF with the information of
    the certificate whose `_id` matches the query parameter `id`.
    """
    # Retrieve and check GET input
    certificate_id = request.args.get("id", None)
    if not id:
        return (
            render_template("error.html", message="ID is missing in your request."),
            403,
        )

    # Check that the ID is in correct format
    try:
        certificate_id = ObjectId(certificate_id)
    except InvalidId:
        return render_template("error.html", message="The ID's format is invalid."), 403

    # Check that the ID exists and retrieve certificate
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
        .add_qrcode(f"{request.host_url}certificate/view?id={str(id)}")
        .save()
    )

    # Return PDF
    return send_file(
        certificate_pdf,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="Certificate.pdf",
    )
