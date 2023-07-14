"""
FILE
    index.py
DESCRIPTION
    Entrypoint for Certificate Automation. It creates the Flask app and ties
    the views to the routes of the application.
"""
from flask import Flask
from flask_login import LoginManager
from app.views.certificates import certificates_blueprint
from app.views.accounts import accounts_blueprint
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
    app.secret_key = "somethinguniqueandsecret"
    app.register_blueprint(certificates_blueprint)
    app.register_blueprint(accounts_blueprint)

    login_manager = LoginManager()
    login_manager.login_view = "accounts.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User(user_id)

    return app