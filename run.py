from dotenv import load_dotenv
from app import create_app

load_dotenv()

if __name__ == "__main__":
    flask_app = create_app()
    flask_app.run(debug=True)
