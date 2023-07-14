import re
from flask import Blueprint, render_template, request
from flask_bcrypt import Bcrypt
from utils import get_database, check_metadata

accounts_blueprint = Blueprint(
    "accounts", __name__, template_folder="templates", url_prefix="/account"
)

# Initialize objects without app configuration
bcrypt = Bcrypt()


@accounts_blueprint.route("/register", methods=["GET", "POST"])
def register():
    """
    View to register a new user.

    Accessing this view's route with GET will render a form to register a new
    user. Accessing this view's route with POST will register a new user with
    the received arguments.
    """
    # If request method is GET, return form
    if request.method == "GET":
        return render_template("register-account.html")

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


@accounts_blueprint.route("/verify", methods=["GET", "POST"])
def verify_account():
    """
    Verify an user's account. To be verified, a certifier must have a website
    where they have a `meta` tag with `name="ca-key"` and
    `content="ca-key-{username}"`. Then, the URL of the website must be
    submitted through this form.

    Accessing this view's route with GET will render a form to verify the
    user's account. Accessing this view's route with POST will try to
    verify the user using the information provided.
    """
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
