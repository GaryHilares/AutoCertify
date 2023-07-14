"""
FILE
    index.py
DESCRIPTION
    Entrypoint for Certificate Automation. It creates the Flask app and ties
    the views to the routes of the application.
"""
from flask import Flask
from app.views.certificates import certificates_blueprint
from app.views.accounts import accounts_blueprint


def create_app():
    # Initialize app and config
    app = Flask(__name__)
    app.register_blueprint(certificates_blueprint)
    app.register_blueprint(accounts_blueprint)
    return app
