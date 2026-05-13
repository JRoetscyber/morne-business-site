"""
Wipes and re-creates the admin user with credentials you type at the prompt.
Run once:
    python reset_admin.py
"""
import getpass
from app import create_app, db
from app.models import AdminUser
from werkzeug.security import generate_password_hash

print("\n=== Delcon Admin Reset ===\n")
username = input("Enter admin username: ").strip()
password = getpass.getpass("Enter admin password: ")
confirm  = getpass.getpass("Confirm password:    ")

if not username or not password:
    print("Username and password cannot be empty. Aborted.")
    exit(1)

if password != confirm:
    print("Passwords do not match. Aborted.")
    exit(1)

app = create_app()
with app.app_context():
    # Remove every existing admin and start clean
    AdminUser.query.delete()
    db.session.add(AdminUser(
        username=username,
        password_hash=generate_password_hash(password),
    ))
    db.session.commit()
    print(f"\nDone. Log in with username '{username}' and the password you just set.")
