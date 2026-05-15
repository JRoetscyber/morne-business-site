"""
Application configuration.
All sensitive values are read from environment variables first;
safe fallbacks are provided for local development only.
Copy .env.example to .env and set real values before deploying.
"""
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    # ── Security ────────────────────────────────────────────
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-CHANGE-before-deploy-xyz987')

    # ── Database ─────────────────────────────────────────────
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(basedir, 'delcon_leads.db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── Session ──────────────────────────────────────────────
    SESSION_COOKIE_HTTPONLY  = True
    SESSION_COOKIE_SAMESITE  = 'Lax'
    # Set SESSION_COOKIE_SECURE = True in production (requires HTTPS)
    SESSION_COOKIE_SECURE    = os.environ.get('SESSION_COOKIE_SECURE', 'false').lower() == 'true'
    PERMANENT_SESSION_LIFETIME = 28800  # 8 hours in seconds

    # ── Admin bootstrap (first-run seed only) ────────────────
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'changeme123')

    # ── Upload paths ─────────────────────────────────────────
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif', 'mp4', 'webm'}
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB hard cap on uploads
    # Cache static files for 1 year in production (Nginx handles this in prod,
    # but this covers Flask's dev server and any Flask-served static responses)
    SEND_FILE_MAX_AGE_DEFAULT = 31536000

    # ── Email Settings (Flask-Mailman) ───────────────────────
    MAIL_SERVER   = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT     = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS  = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'notifications@delcon.co.za')
    MAIL_BACKEND  = os.environ.get('MAIL_BACKEND', 'flask_mailman.backends.smtp.EmailBackend')
    
    # Recipient for lead notifications
    CONTACT_EMAIL = os.environ.get('CONTACT_EMAIL', 'jroets@cyber.co.za')


class DevelopmentConfig(Config):
    DEBUG = True
    SEND_FILE_MAX_AGE_DEFAULT = 0  # no caching in dev — CSS/JS changes show instantly
    MAIL_BACKEND = os.environ.get('MAIL_BACKEND', 'flask_mailman.backends.console.EmailBackend')


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True


config = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'default':     DevelopmentConfig,
}
