"""
Create the CivicLens admin user.

Usage:
    python create_admin.py

Run this once after deploying, via Render Shell or locally.
If an admin user already exists, prompts before overwriting.
"""
import os
import sys
import getpass

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('GEMINI_API_KEY', 'create-admin-placeholder')
os.environ.setdefault('SECRET_KEY', 'create-admin-placeholder')

from main import app
from models import db, User


def create_admin():
    with app.app_context():
        db.create_all()

        existing = User.query.filter_by(is_admin=True).first()
        if existing:
            print(f"Admin user '{existing.username}' already exists.")
            overwrite = input("Overwrite? (yes/no): ").strip().lower()
            if overwrite != 'yes':
                print("Aborted.")
                return

        username = input("Admin username: ").strip().lower()
        if not username:
            print("Username cannot be empty.")
            return

        password = getpass.getpass("Admin password (hidden): ")
        if len(password) < 8:
            print("Password must be at least 8 characters.")
            return

        confirm = getpass.getpass("Confirm password: ")
        if password != confirm:
            print("Passwords do not match.")
            return

        if existing:
            db.session.delete(existing)
            db.session.commit()

        user = User(username=username, is_admin=True)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        print(f"Admin user '{username}' created successfully.")
        print("You can now log in at /login")


if __name__ == '__main__':
    create_admin()