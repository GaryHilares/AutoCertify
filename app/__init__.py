"""
FILE
    index.py
DESCRIPTION
    Entrypoint for Certificate Automation. It creates the Flask app and ties
    the views to the routes of the application.
"""
from bson import ObjectId
from flask import Flask, g
from flask_login import LoginManager
from app.views.certificate import certificate_blueprint
from app.views.account import account_blueprint
from app.models.user import User


def create_app() -> Flask:
    """
    Creates the main lask application.

    Returns:
        app (Flask)
            A Flask application object which can be used to run the main
            website.
    """
    # Initialize app and config
    app = Flask(__name__)
    app.config.from_object("config")
    app.secret_key = "somethinguniqueandsecret"
    app.register_blueprint(certificate_blueprint)
    app.register_blueprint(account_blueprint)

    @app.teardown_request
    def clean(error):
        client = getattr(g, "db_client", None)
        if client:
            client.close()

    login_manager = LoginManager()
    login_manager.login_view = "accounts.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(ObjectId(user_id))

    return app
