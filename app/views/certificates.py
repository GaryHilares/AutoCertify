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
import requests
from bson.objectid import ObjectId
from bson.errors import InvalidId
from app.certificate_builder import CertificateBuilder
from app.utils import get_database

certificates_blueprint = Blueprint(
    "certificates", __name__, template_folder="templates", url_prefix="/certificate"
)

# Initialize Flask extensions and later add app configuration
bcrypt = Bcrypt()


@certificates_blueprint.record_once
def on_load(state: any) -> None:
    """
    Adds app configuration to Flask extensions.

    Arguments:
        state (any)
            A state object created by Flask whose `app` attribute refers to the main
            Flask application.
    """
    bcrypt.init_app(state.app)


@certificates_blueprint.route("/create", methods=["GET", "POST"])
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

    # Retrieve certifier and check that its credentials are correct
    database = get_database()

    # Update database with new certificate
    insert_data = database["certificate-list"].insert_one(
        {
            "name": certificate_name,
            "title": certificate_title,
            "certifier_id": ObjectId(current_user.id),
        }
    )

    # Return success message
    return render_template(
        "success.html",
        message=f"Certificate with the id {insert_data.inserted_id} created successfully",
    )


@certificates_blueprint.route("/view", methods=["GET"])
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
    database = get_database()
    certificate = database["certificate-list"].find_one({"_id": certificate_id})
    if not certificate:
        return render_template("error.html", message="ID was not found."), 403

    # Check that certifier is valid and retrieve its information
    certifier = database["certifiers"].find_one({"_id": certificate["certifier_id"]})
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
            "id": certificate["_id"],
            "name": certificate["name"],
            "title": certificate["title"],
        },
        certifier={
            "id": certifier["_id"],
            "name": certifier["name"],
            "url": certifier["url"],
        },
        download_url=f'{request.host_url}/certificate/download?id={certificate["_id"]}',
    )


@certificates_blueprint.route("/download", methods=["GET"])
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
    database = get_database()
    certificate = database["certificate-list"].find_one({"_id": certificate_id})
    if not certificate:
        return render_template("error.html", message="ID was not found."), 403

    # Check that certifier is valid and retrieve its information
    certifier = database["certifiers"].find_one({"_id": certificate["certifier_id"]})
    if not certifier:
        return (
            render_template(
                "error.html",
                critical_error=True,
                message="Certificate data is corrupt.",
            ),
            500,
        )

    settings = None
    if "img_url" in certificate:
        settings = requests.get(certificate["img_url"], timeout=3).json()

    # Generate certificate
    certificate_pdf = (
        CertificateBuilder(settings)
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
