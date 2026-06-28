import os
import sys
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    # ── Flask core ─────────────────────────────────────────────────────────
    SECRET_KEY = os.getenv('SECRET_KEY', 'civiclens-dev-key-change-in-production')

    # ── Database ───────────────────────────────────────────────────────────
    # On Render: set DATABASE_URL to your PostgreSQL Internal Database URL.
    # Locally: leave DATABASE_URL unset — SQLite is used automatically.
    #
    # Render supplies the URL as  postgres://...  but SQLAlchemy requires
    # postgresql://...  — the replacement below fixes that silently.
    _db_url = os.getenv('DATABASE_URL', 'sqlite:///civiclens.db')
    if _db_url.startswith('postgres://'):
        _db_url = _db_url.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = _db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── File uploads ───────────────────────────────────────────────────────
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024   # 16 MB hard cap
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'heic', 'webp'}

    # ── Gemini ─────────────────────────────────────────────────────────────
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

    # ── Flask-Login ────────────────────────────────────────────────────────
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    REMEMBER_COOKIE_SECURE = os.getenv('FLASK_ENV') == 'production'
    REMEMBER_COOKIE_HTTPONLY = True