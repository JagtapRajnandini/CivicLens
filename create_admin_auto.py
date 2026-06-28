import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('GEMINI_API_KEY', 'setup-placeholder')
os.environ.setdefault('SECRET_KEY', 'setup-placeholder')

from main import app
from models import db, User

ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')

if not ADMIN_PASSWORD:
    print("ADMIN_PASSWORD environment variable not set — skipping admin creation.")
    sys.exit(0)

with app.app_context():
    db.create_all()
    existing = User.query.filter_by(username=ADMIN_USERNAME).first()
    if existing:
        print(f"Admin '{ADMIN_USERNAME}' already exists — skipping.")
        sys.exit(0)
    user = User(username=ADMIN_USERNAME, is_admin=True)
    user.set_password(ADMIN_PASSWORD)
    db.session.add(user)
    db.session.commit()
    print(f"Admin '{ADMIN_USERNAME}' created successfully.")