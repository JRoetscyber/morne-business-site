"""
Application factory for the Delcon lead-gen site.
"""
import os
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # ── Extensions ─────────────────────────────────────────
    db.init_app(app)

    # ── Blueprints ──────────────────────────────────────────
    from app.routes import main
    from app.admin import admin_bp

    app.register_blueprint(main)
    app.register_blueprint(admin_bp)

    # ── Context processors ──────────────────────────────────
    @app.context_processor
    def inject_globals():
        """
        Makes shared variables available in every template:
          now           — current UTC datetime (footer copyright year)
          site_settings — dict of all SiteSetting K/V pairs
          nav_services  — active Service rows for the navbar dropdown
        """
        from app.models import SiteSetting, Service
        try:
            site_settings = {row.key: row.value for row in SiteSetting.query.all()}
            nav_services = (
                Service.query
                .filter_by(is_active=True)
                .order_by(Service.sort_order, Service.name)
                .all()
            )
        except Exception:
            # DB not yet initialised on very first request
            site_settings = {}
            nav_services = []

        return {
            'now':           datetime.utcnow(),
            'site_settings': site_settings,
            'nav_services':  nav_services,
        }

    # ── DB init & seed ──────────────────────────────────────
    with app.app_context():
        db.create_all()
        _ensure_upload_dirs(app)
        _seed_admin(app)

    return app


# ── Helpers ─────────────────────────────────────────────────

def _ensure_upload_dirs(app):
    """Create the upload directory tree on first run."""
    base = app.config.get('UPLOAD_FOLDER', '')
    for subdir in ('', 'images'):
        path = os.path.join(base, subdir) if subdir else base
        os.makedirs(path, exist_ok=True)


def _seed_admin(app):
    """
    Creates the default admin user on a fresh install.
    Credentials come from environment variables; the defaults are
    intentionally weak — override via .env before deployment.
    """
    from app.models import AdminUser
    from werkzeug.security import generate_password_hash

    if AdminUser.query.count() == 0:
        username = app.config.get('ADMIN_USERNAME', 'admin')
        password = app.config.get('ADMIN_PASSWORD', 'changeme123')
        db.session.add(AdminUser(
            username=username,
            password_hash=generate_password_hash(password),
        ))
        db.session.commit()
        app.logger.info(
            f'Admin user "{username}" created. '
            'Change the default password immediately.'
        )
