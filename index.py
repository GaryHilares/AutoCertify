"""
FILE
    index.py
DESCRIPTION
    Entrypoint for Certificate Automation. It creates the Flask app and ties
    the views to the routes of the application.
"""
from dotenv import load_dotenv
from flask import Flask
from views.certificates import certificates_blueprint
from views.accounts import accounts_blueprint

# Initialize app and config
load_dotenv()
app = Flask(__name__)
app.register_blueprint(certificates_blueprint)
app.register_blueprint(accounts_blueprint)

if __name__ == "__main__":
    app.run(debug=True)
