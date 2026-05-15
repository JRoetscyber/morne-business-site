"""
Application factory for the Delcon lead-gen site.
"""
import os
import time
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mailman import Mail
from config import Config

# ── Simple in-process TTL cache for context-processor queries ──
# These values (site settings + nav services) change only when an admin
# saves them, so fetching from DB on every request is wasteful.
_CP_CACHE: dict = {}
_CP_TTL = 60  # seconds


def _cp_get(key: str, loader, ttl: int = _CP_TTL):
    """Return cached value for *key*, refreshing via *loader* when stale."""
    entry = _CP_CACHE.get(key)
    if entry is None or time.monotonic() - entry['ts'] > ttl:
        _CP_CACHE[key] = {'data': loader(), 'ts': time.monotonic()}
    return _CP_CACHE[key]['data']


def invalidate_cp_cache():
    """Call after any admin write that changes settings or services."""
    _CP_CACHE.clear()

db = SQLAlchemy()
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # ── Extensions ─────────────────────────────────────────
    db.init_app(app)
    mail.init_app(app)

    # ── Blueprints ──────────────────────────────────────────
    from app.routes import main
    from app.admin import admin_bp

    app.register_blueprint(main)
    app.register_blueprint(admin_bp)

    # ── Context processors ──────────────────────────────────
    @app.context_processor
    def inject_globals():
        """
        Makes shared variables available in every template.
        Both DB calls are cached for _CP_TTL seconds so we don't hit
        the database on every single HTTP request.
        """
        from app.models import SiteSetting, Service
        try:
            site_settings = _cp_get(
                'site_settings',
                lambda: {row.key: row.value for row in SiteSetting.query.all()},
            )
            # Cache nav_services as plain dicts — avoids DetachedInstanceError
            # when the SQLAlchemy session used during caching is no longer active.
            nav_services = _cp_get(
                'nav_services',
                lambda: [
                    {'name': s.name, 'slug': s.slug, 'spec_range': s.spec_range}
                    for s in Service.query
                        .filter_by(is_active=True)
                        .order_by(Service.sort_order, Service.name)
                        .all()
                ],
            )
        except Exception:
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
