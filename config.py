"""
Application configuration.
All sensitive values are read from environment variables first;
safe fallbacks are provided for local development only.
Copy .env.example to .env and set real values before deploying.
"""
import os

basedir = os.path.abspath(os.path.dirname(__file__))


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
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True


config = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'default':     DevelopmentConfig,
}
