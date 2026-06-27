import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Flask core
    SECRET_KEY = os.getenv('SECRET_KEY', 'civiclens-dev-key-change-in-production')

    # Database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///civiclens.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # File uploads
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB cap
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'heic', 'webp'}

    # Gemini
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

    @staticmethod
    def validate():
        if not Config.GEMINI_API_KEY:
            raise EnvironmentError(
                "GEMINI_API_KEY is not set. "
                "Add it to .env locally or to Render environment variables."
            )