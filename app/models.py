"""
SQLAlchemy models for the Delcon lead-gen site.
All tables created via db.create_all() in the app factory.
"""
from datetime import datetime
from app import db


class Lead(db.Model):
    """Inbound enquiry / contact-form submission."""
    __tablename__ = 'leads'

    id           = db.Column(db.Integer, primary_key=True)
    full_name    = db.Column(db.String(120), nullable=False)
    company      = db.Column(db.String(120), nullable=True)
    email        = db.Column(db.String(255), nullable=False)
    phone        = db.Column(db.String(30),  nullable=False)
    service_type = db.Column(db.String(60),  nullable=False)
    message      = db.Column(db.Text,        nullable=False)
    status       = db.Column(db.String(20),  nullable=False, default='new')
    ip_address   = db.Column(db.String(45),  nullable=True)
    created_at   = db.Column(db.DateTime,    nullable=False, default=datetime.utcnow)

    VALID_STATUSES = ('new', 'open', 'replied', 'closed')

    def __repr__(self):
        return f'<Lead #{self.id} {self.full_name} [{self.status}]>'


class Service(db.Model):
    """
    A service offering (Pipe Jacking, HDD, etc.).
    scope_items and applications are stored as JSON strings.
    """
    __tablename__ = 'services'

    id                = db.Column(db.Integer, primary_key=True)
    name              = db.Column(db.String(120), nullable=False)
    slug              = db.Column(db.String(120), nullable=False, unique=True)
    category          = db.Column(db.String(80),  nullable=True)
    short_description = db.Column(db.Text,        nullable=True)
    full_description  = db.Column(db.Text,        nullable=True)
    spec_range        = db.Column(db.String(100), nullable=True)
    scope_items       = db.Column(db.Text,        nullable=True)   # JSON list
    specs             = db.Column(db.Text,        nullable=True)   # JSON list
    methodology       = db.Column(db.Text,        nullable=True)
    applications      = db.Column(db.Text,        nullable=True)   # JSON list
    meta_description  = db.Column(db.String(320), nullable=True)
    is_active         = db.Column(db.Boolean,     nullable=False, default=True)
    sort_order        = db.Column(db.Integer,     nullable=False, default=0)
    created_at        = db.Column(db.DateTime,    nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<Service {self.slug}>'


class Project(db.Model):
    """A completed project portfolio entry."""
    __tablename__ = 'projects'

    id             = db.Column(db.Integer,  primary_key=True)
    title          = db.Column(db.String(200), nullable=False)
    service_type   = db.Column(db.String(60),  nullable=True)
    location       = db.Column(db.String(150), nullable=True)
    client         = db.Column(db.String(150), nullable=True)
    description    = db.Column(db.Text,        nullable=True)
    image_path     = db.Column(db.String(300), nullable=True)
    pipe_size      = db.Column(db.String(50),  nullable=True)
    drive_length   = db.Column(db.String(50),  nullable=True)
    value          = db.Column(db.String(50),  nullable=True)
    completed_date = db.Column(db.Date,        nullable=True)
    is_active      = db.Column(db.Boolean,     nullable=False, default=True)
    sort_order     = db.Column(db.Integer,     nullable=False, default=0)
    created_at     = db.Column(db.DateTime,    nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<Project #{self.id} {self.title}>'


class AdminUser(db.Model):
    """Admin portal credentials. Passwords stored as Werkzeug hashes."""
    __tablename__ = 'admin_users'

    id            = db.Column(db.Integer,  primary_key=True)
    username      = db.Column(db.String(80),  nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at    = db.Column(db.DateTime,    nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<AdminUser {self.username}>'


class SiteSetting(db.Model):
    """
    Simple key-value store for global site settings
    (contact info, BBBEE level, etc.)
    """
    __tablename__ = 'site_settings'

    id         = db.Column(db.Integer,  primary_key=True)
    key        = db.Column(db.String(80), nullable=False, unique=True)
    value      = db.Column(db.Text,       nullable=True)
    updated_at = db.Column(db.DateTime,   nullable=False,
                           default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<SiteSetting {self.key}>'
