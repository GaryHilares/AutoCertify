"""
FILE
    index.py
DESCRIPTION
    Entrypoint for Certificate Automation. It creates the Flask app and ties
    the views to the routes of the application.
"""
import re
from bson.objectid import ObjectId
from dotenv import load_dotenv
from flask import Flask, request, render_template, send_file
from flask_bcrypt import Bcrypt
import requests
from utils import get_database, check_metadata, get_certificate_pdf

load_dotenv()
app = Flask(__name__)
bcrypt = Bcrypt(app)


@app.route("/register", methods=["GET", "POST"])
def register():
    # If request method is GET, return form
    if request.method == "GET":
        return render_template("register.html")

    # Retrieve and check POST input
    name = request.form.get("name", None)
    password = request.form.get("password", None)
    if not name or not password:
        return (
            render_template("error.html", message="Name or password are missing."),
            400,
        )

    # Check that password is not too long
    pattern = "^[A-Za-z0-9\\-\\_\\@\\!\\?\\.]{4,50}$"
    if not re.search(pattern, name) or not re.search(pattern, password):
        return render_template(
            "error.html",
            message="""Name and password must consist of 4-50 characters,
            including only letters, numbers, and standard punctuation.""",
        )

    # Check that account does not already exist in database
    database = get_database()
    if database["certifiers"].find_one({"name": name}) is not None:
        return render_template(
            "error.html", message=f"An account with the name {name} already exists."
        )

    # Update database with new account
    database["certifiers"].insert_one(
        {
            "name": name,
            "password": bcrypt.generate_password_hash(password),
            "url": "None",
        }
    )

    # Return success message
    return render_template(
        "success.html", message=f"Account {name} created successfully"
    )


@app.route("/verify-account", methods=["GET", "POST"])
def verify_account():
    # If request method is GET, return form
    if request.method == "GET":
        return render_template("verify-account.html")

    # Retrieve and check POST input
    name = request.form.get("name", None)
    password = request.form.get("password", None)
    url = request.form.get("url", None)
    if not name or not password or not url:
        return render_template("error.html", message="A field is missing."), 400

    # Check that certifier exists and retrieve its information
    database = get_database()
    certifier = database["certifiers"].find_one({"name": name})
    if not certifier or not bcrypt.check_password_hash(certifier["password"], password):
        return render_template("error.html", message="Credentials are incorrect."), 400

    # Check if metadata in URL is valid for this specific certifier
    if not check_metadata(url, "ca-key", f"ca-key-{name}"):
        return (
            render_template(
                "error.html",
                message="Metadata tag was not found. Make sure you followed the steps correctly.",
            ),
            400,
        )

    # Update database with verified URL
    database["certifiers"].update_one({"_id": certifier["id"]}, {"$set": {"url": url}})

    # Return success message
    return render_template(
        "success.html",
        message=f"Account {name} verified correctly with the website {url}",
    )


@app.route("/create-certificate", methods=["GET", "POST"])
def create_certificate():
    # If request method is GET, return form
    if request.method == "GET":
        return render_template("create-certificate.html")

    # Retrieve and check POST input
    certifier_name = request.form.get("certifier-name", None)
    certifier_password = request.form.get("certifier-password", None)
    certificate_name = request.form.get("certificate-name", None)
    certificate_title = request.form.get("certificate-title", None)
    if (
        not certifier_name
        or not certifier_password
        or not certificate_name
        or not certificate_title
    ):
        return (
            render_template(
                "error.html", message="A field is missing in your request."
            ),
            400,
        )

    # Retrieve certifier and check that its credentials are correct
    database = get_database()
    certifier = database["certifiers"].find_one(
        {
            "name": certifier_name,
        }
    )
    if not certifier or not bcrypt.check_password_hash(
        certifier["password"], certifier_password
    ):
        return (
            render_template(
                "error.html", message="Certifier credentials are incorrect."
            ),
            403,
        )

    # Update database with new certificate
    insert_data = database["certificate-list"].insert_one(
        {
            "name": certificate_name,
            "title": certificate_title,
            "certifier_id": certifier["_id"],
        }
    )

    # Return success message
    return render_template(
        "success.html",
        message=f"Certificate with the id {insert_data.inserted_id} created successfully",
    )


@app.route("/view-certificate", methods=["GET"])
def view_certificate():
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
    except:
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
        download_url=f'{request.host_url}/download-certificate?id={certificate["_id"]}',
    )


@app.route("/download-certificate", methods=["GET"])
def download_certificate():
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
    except:
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
    certificate_pdf = get_certificate_pdf(
        certificate,
        certifier,
        settings,
        f"{request.host_url}view-certificate?id={str(id)}",
    )

    # Return PDF
    return send_file(
        certificate_pdf,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="Certificate.pdf",
    )


if __name__ == "__main__":
    app.run(debug=True)
