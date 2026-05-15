"""
Private admin routes for the Delcon site.
Blueprint: admin_bp  (url_prefix='/admin')

All routes except /admin/login are protected by the
@login_required decorator which checks Flask's server-side session.
"""
import os
import uuid
import functools
from datetime import datetime
from sqlalchemy import func

from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, session,
    abort, current_app,
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from app import db, invalidate_cp_cache
from app.models import AdminUser, Lead, Project, Service, SiteSetting

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# ── Image slot definitions ──────────────────────────────────
# Add new slots here; the upload/delete routes handle any key in this list.
IMAGE_SLOTS = [
    # ── Homepage ────────────────────────────────────────────
    {
        'key':     'hero_image_path',
        'display': 'Homepage — Hero Background',
        'type':    'image',
        'desc':    'Full-width banner behind the homepage hero text. '
                   'Recommended: 1920 × 1080px, JPG/WebP.',
    },
    {
        'key':     'hero_video_path',
        'display': 'Homepage — Hero Video',
        'type':    'video',
        'desc':    'Optional video to play in the background. '
                   'Recommended: optimized .mp4 or .webm, max 5-10MB.',
    },

    # ── About Us ────────────────────────────────────────────
    {
        'key':     'about_image_path',
        'display': 'About Us — Primary Photo',
        'type':    'image',
        'desc':    'Main photo in the Our Story section (right column). '
                   'Recommended: 900 × 600px.',
    },
    {
        'key':     'about_image_2_path',
        'display': 'About Us — Secondary Photo',
        'type':    'image',
        'desc':    'Second photo shown in the Objectives section. '
                   'Recommended: 900 × 600px.',
    },

    # ── Services ────────────────────────────────────────────
    {
        'key':     'service_img_pipe_jacking',
        'display': 'Services — Pipe Jacking Photo',
        'type':    'image',
        'desc':    'Photo in the Pipe Jacking section sidebar. '
                   'Recommended: 800 × 600px.',
    },
    {
        'key':     'service_img_hdd',
        'display': 'Services — HDD Photo',
        'type':    'image',
        'desc':    'Photo in the Horizontal Directional Drilling section sidebar. '
                   'Recommended: 800 × 600px.',
    },
    {
        'key':     'service_img_hdpe',
        'display': 'Services — HDPE Welding Photo',
        'type':    'image',
        'desc':    'Photo in the HDPE Butt-Welding section sidebar. '
                   'Recommended: 800 × 600px.',
    },
    {
        'key':     'service_img_infrastructure',
        'display': 'Services — Infrastructure Photo',
        'type':    'image',
        'desc':    'Photo in the General Infrastructure section sidebar. '
                   'Recommended: 800 × 600px.',
    },
]

_SLOT_KEYS = {s['key'] for s in IMAGE_SLOTS}


# ── Helpers ─────────────────────────────────────────────────

def _allowed_file(filename):
    allowed = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'webp', 'gif'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed


def _json_to_lines(raw):
    """Convert a JSON-encoded list string to newline-separated text for textarea display."""
    import json as _j
    if not raw:
        return ''
    try:
        items = _j.loads(raw)
        return '\n'.join(items) if isinstance(items, list) else raw
    except (ValueError, TypeError):
        return raw


def login_required(f):
    """Redirect unauthenticated requests to the admin login page."""
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Please sign in to access the admin portal.', 'warning')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated


def _ctx():
    """Base template context for every admin view."""
    return {
        'admin_username': session.get('admin_username', 'Admin'),
        'new_inquiries':  Lead.query.filter_by(status='new').count(),
    }


# ── Login / Logout ──────────────────────────────────────────

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin.dashboard'))

    error = None

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            error = 'Username and password are required.'
        else:
            user = AdminUser.query.filter_by(username=username).first()
            if user and check_password_hash(user.password_hash, password):
                session.clear()
                session.permanent = True
                session['admin_logged_in'] = True
                session['admin_username']  = user.username
                session['admin_user_id']   = user.id
                flash(f'Welcome back, {user.username}.', 'success')
                return redirect(url_for('admin.dashboard'))
            else:
                error = 'Invalid username or password.'

    return render_template('admin/login.html', error=error)


@admin_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been signed out.', 'info')
    return redirect(url_for('admin.login'))


# ── Dashboard ───────────────────────────────────────────────

@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    ctx = _ctx()
    ctx.update({
        'total_inquiries':  Lead.query.count(),
        'total_services':   Service.query.filter_by(is_active=True).count(),
        'total_projects':   Project.query.filter_by(is_active=True).count(),
        'recent_inquiries': (
            Lead.query.order_by(Lead.created_at.desc()).limit(10).all()
        ),
    })
    return render_template('admin/dashboard.html', **ctx)


# ── Inquiries ───────────────────────────────────────────────

@admin_bp.route('/inquiries')
@login_required
def inquiries():
    ctx = _ctx()
    status_filter = request.args.get('status', '').strip()

    query = Lead.query
    if status_filter in Lead.VALID_STATUSES:
        query = query.filter_by(status=status_filter)

    # One GROUP BY query replaces five separate COUNT(*) round-trips
    rows   = db.session.query(Lead.status, func.count(Lead.id)).group_by(Lead.status).all()
    totals = {status: count for status, count in rows}
    ctx.update({
        'inquiries':     query.order_by(Lead.created_at.desc()).all(),
        'status_filter': status_filter,
        'status_counts': {
            'all':     sum(totals.values()),
            'new':     totals.get('new', 0),
            'open':    totals.get('open', 0),
            'replied': totals.get('replied', 0),
            'closed':  totals.get('closed', 0),
        },
    })
    return render_template('admin/inquiries_manage.html', **ctx)


@admin_bp.route('/inquiries/<int:id>')
@login_required
def view_inquiry(id):
    ctx  = _ctx()
    lead = Lead.query.get_or_404(id)

    if lead.status == 'new':
        lead.status = 'open'
        db.session.commit()
        ctx['new_inquiries'] = max(0, ctx['new_inquiries'] - 1)

    ctx['lead'] = lead
    return render_template('admin/inquiries_manage.html', **ctx)


@admin_bp.route('/inquiries/<int:id>/status', methods=['POST'])
@login_required
def update_inquiry_status(id):
    lead       = Lead.query.get_or_404(id)
    new_status = request.form.get('status', '').strip()

    if new_status not in Lead.VALID_STATUSES:
        flash('Invalid status value.', 'danger')
        return redirect(url_for('admin.inquiries'))

    lead.status = new_status
    db.session.commit()
    flash(f'Inquiry #{id} status updated to "{new_status}".', 'success')
    return redirect(url_for('admin.inquiries'))


@admin_bp.route('/inquiries/<int:id>/delete', methods=['POST'])
@login_required
def delete_inquiry(id):
    lead = Lead.query.get_or_404(id)
    db.session.delete(lead)
    db.session.commit()
    flash(f'Inquiry #{id} deleted.', 'success')
    return redirect(url_for('admin.inquiries'))


# ── Projects ────────────────────────────────────────────────

@admin_bp.route('/projects')
@login_required
def projects():
    ctx = _ctx()
    ctx['projects'] = (
        Project.query
        .order_by(Project.sort_order.asc(), Project.created_at.desc())
        .all()
    )
    return render_template('admin/projects_manage.html', **ctx)


@admin_bp.route('/projects/new', methods=['GET', 'POST'])
@admin_bp.route('/projects/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def project_form(id=None):
    ctx     = _ctx()
    project = Project.query.get_or_404(id) if id else Project()

    if request.method == 'POST':
        project.title        = request.form.get('title', '').strip()
        project.service_type = request.form.get('service_type', '').strip()
        project.location     = request.form.get('location', '').strip() or None
        project.client       = request.form.get('client', '').strip() or None
        project.description  = request.form.get('description', '').strip() or None
        project.pipe_size    = request.form.get('pipe_size', '').strip() or None
        project.drive_length = request.form.get('drive_length', '').strip() or None
        project.value        = request.form.get('value', '').strip() or None
        project.is_active    = 'is_active' in request.form

        date_str = request.form.get('completed_date', '').strip()
        if date_str:
            try:
                project.completed_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                project.completed_date = None
        else:
            project.completed_date = None

        if not project.title:
            flash('Project title is required.', 'danger')
            ctx['project'] = project
            return render_template('admin/projects_manage.html', **ctx)

        if not project.id:
            db.session.add(project)

        db.session.commit()
        flash(f'Project "{project.title}" saved.', 'success')
        return redirect(url_for('admin.projects'))

    ctx['project'] = project
    return render_template('admin/projects_manage.html', **ctx)


@admin_bp.route('/projects/<int:id>/delete', methods=['POST'])
@login_required
def delete_project(id):
    project = Project.query.get_or_404(id)
    db.session.delete(project)
    db.session.commit()
    flash(f'Project "{project.title}" deleted.', 'success')
    return redirect(url_for('admin.projects'))


# ── Services ────────────────────────────────────────────────

@admin_bp.route('/services')
@login_required
def services():
    ctx = _ctx()
    ctx['services'] = Service.query.order_by(Service.sort_order, Service.name).all()
    return render_template('admin/service_form.html', **ctx)


@admin_bp.route('/services/new', methods=['GET', 'POST'])
@admin_bp.route('/services/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def service_form(id=None):
    import json as _json

    ctx     = _ctx()
    service = Service.query.get_or_404(id) if id else Service()

    if request.method == 'POST':
        service.name              = request.form.get('name', '').strip()
        service.slug              = request.form.get('slug', '').strip().lower()
        service.category          = request.form.get('category', '').strip() or None
        service.short_description = request.form.get('short_description', '').strip() or None
        service.full_description  = request.form.get('full_description', '').strip() or None
        service.spec_range        = request.form.get('spec_range', '').strip() or None
        service.methodology       = request.form.get('methodology', '').strip() or None
        service.meta_description  = request.form.get('meta_description', '').strip() or None
        service.is_active         = 'is_active' in request.form

        def lines_to_json(field_name):
            raw   = request.form.get(field_name, '').strip()
            items = [l.strip() for l in raw.splitlines() if l.strip()]
            return _json.dumps(items) if items else None

        service.scope_items  = lines_to_json('scope_items')
        service.specs        = lines_to_json('specs')
        service.applications = lines_to_json('applications')

        if not service.name or not service.slug:
            flash('Service name and slug are required.', 'danger')
            ctx['service'] = service
            return render_template('admin/service_form.html', **ctx)

        if not service.id:
            db.session.add(service)

        db.session.commit()
        invalidate_cp_cache()
        flash(f'Service "{service.name}" saved.', 'success')
        return redirect(url_for('admin.services'))

    ctx['service']           = service
    ctx['services']          = Service.query.order_by(Service.sort_order, Service.name).all()
    ctx['scope_items_text']  = _json_to_lines(service.scope_items)
    ctx['specs_text']        = _json_to_lines(service.specs)
    ctx['applications_text'] = _json_to_lines(service.applications)
    return render_template('admin/service_form.html', **ctx)


@admin_bp.route('/services/<int:id>/delete', methods=['POST'])
@login_required
def delete_service(id):
    service = Service.query.get_or_404(id)
    db.session.delete(service)
    db.session.commit()
    invalidate_cp_cache()
    flash(f'Service "{service.name}" deleted.', 'success')
    return redirect(url_for('admin.services'))


# ── Products (stub) ─────────────────────────────────────────

@admin_bp.route('/products')
@login_required
def products():
    ctx = _ctx()
    return render_template('admin/products_manage.html', **ctx)


# ── Settings ────────────────────────────────────────────────

@admin_bp.route('/settings')
@login_required
def settings():
    ctx  = _ctx()
    rows = SiteSetting.query.all()
    site = {row.key: row.value for row in rows}

    ctx.update({
        'site_settings':  site,
        'admin_users':    AdminUser.query.order_by(AdminUser.created_at).all(),
        'image_slots':    IMAGE_SLOTS,
        # current_images maps slot key → value (relative path or None)
        'current_images': {s['key']: site.get(s['key']) for s in IMAGE_SLOTS},
    })
    return render_template('admin/settings.html', **ctx)


@admin_bp.route('/settings/save', methods=['POST'])
@login_required
def save_settings():
    text_fields = [
        'business_name', 'tagline',
        'phone_primary', 'phone_secondary',
        'email_contact', 'bbbee_level', 'address',
    ]
    for key in text_fields:
        value   = request.form.get(key, '').strip()
        setting = SiteSetting.query.filter_by(key=key).first()
        if setting:
            setting.value      = value
            setting.updated_at = datetime.utcnow()
        else:
            db.session.add(SiteSetting(key=key, value=value))

    db.session.commit()
    invalidate_cp_cache()
    flash('Site settings saved.', 'success')
    return redirect(url_for('admin.settings'))


@admin_bp.route('/settings/upload-image', methods=['POST'])
@login_required
def upload_image():
    slot_key = request.form.get('key', '').strip()
    if slot_key not in _SLOT_KEYS:
        flash('Invalid image slot.', 'danger')
        return redirect(url_for('admin.settings'))

    file = request.files.get('image')
    if not file or file.filename == '':
        flash('No file was selected.', 'warning')
        return redirect(url_for('admin.settings'))

    if not _allowed_file(file.filename):
        flash('File type not allowed. Use PNG, JPG, WebP, MP4, or WebM.', 'danger')
        return redirect(url_for('admin.settings'))

    # Build a collision-safe filename: <slot_key>_<8-char uuid>.<ext>
    ext      = secure_filename(file.filename).rsplit('.', 1)[-1].lower()
    filename = f"{slot_key}_{uuid.uuid4().hex[:8]}.{ext}"

    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'images')
    os.makedirs(upload_dir, exist_ok=True)

    # Remove the old file from disk before replacing
    old = SiteSetting.query.filter_by(key=slot_key).first()
    if old and old.value:
        old_abs = os.path.join(current_app.root_path, 'static', old.value)
        if os.path.isfile(old_abs):
            os.remove(old_abs)

    try:
        file.save(os.path.join(upload_dir, filename))
    except OSError as exc:
        flash(f'File could not be saved: {exc}', 'danger')
        return redirect(url_for('admin.settings'))

    # Store the path relative to app/static/ so url_for('static', filename=…) works
    relative = f'uploads/images/{filename}'

    setting = SiteSetting.query.filter_by(key=slot_key).first()
    if setting:
        setting.value      = relative
        setting.updated_at = datetime.utcnow()
    else:
        db.session.add(SiteSetting(key=slot_key, value=relative))

    db.session.commit()

    slot_label = next((s['display'] for s in IMAGE_SLOTS if s['key'] == slot_key), slot_key)
    flash(f'"{slot_label}" uploaded successfully.', 'success')
    return redirect(url_for('admin.settings'))


@admin_bp.route('/settings/delete-image', methods=['POST'])
@login_required
def delete_image():
    slot_key = request.form.get('key', '').strip()
    if slot_key not in _SLOT_KEYS:
        flash('Invalid image slot.', 'danger')
        return redirect(url_for('admin.settings'))

    setting = SiteSetting.query.filter_by(key=slot_key).first()
    if setting and setting.value:
        abs_path = os.path.join(current_app.root_path, 'static', setting.value)
        if os.path.isfile(abs_path):
            os.remove(abs_path)
        setting.value      = None
        setting.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Image removed.', 'success')
    else:
        flash('No image to remove.', 'warning')

    return redirect(url_for('admin.settings'))


@admin_bp.route('/settings/password', methods=['POST'])
@login_required
def change_password():
    current_pw = request.form.get('current_password', '')
    new_pw     = request.form.get('new_password', '')
    confirm_pw = request.form.get('confirm_password', '')

    user = AdminUser.query.get(session.get('admin_user_id'))
    if not user:
        abort(403)

    if not check_password_hash(user.password_hash, current_pw):
        flash('Current password is incorrect.', 'danger')
        return redirect(url_for('admin.settings'))

    if len(new_pw) < 8:
        flash('New password must be at least 8 characters.', 'danger')
        return redirect(url_for('admin.settings'))

    if new_pw != confirm_pw:
        flash('New passwords do not match.', 'danger')
        return redirect(url_for('admin.settings'))

    user.password_hash = generate_password_hash(new_pw)
    db.session.commit()
    flash('Password updated successfully.', 'success')
    return redirect(url_for('admin.settings'))
