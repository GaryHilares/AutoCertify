"""
FILE
    run.py
DESCRIPTION
    Entrypoint for Certificate Automation. Runs the Flask application located in the
    app package.
"""
from dotenv import load_dotenv
from app import create_app

# Load environment variables from .env
load_dotenv()

# Create app and run it
if __name__ == "__main__":
    flask_app = create_app()
    flask_app.run(debug=True)
