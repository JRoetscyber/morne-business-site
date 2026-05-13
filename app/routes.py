"""
Public-facing routes for the Delcon site.
Blueprint: main
"""
import json
from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, abort,
)
from app import db
from app.models import Lead, Service, Project

main = Blueprint('main', __name__)


# ── Helpers ────────────────────────────────────────────────

def _validate_lead_form(form):
    """
    Returns (errors: list[str], data: dict).
    Keeps validation logic out of the view.
    """
    full_name    = form.get('full_name', '').strip()
    company      = form.get('company', '').strip()
    phone        = form.get('phone', '').strip()
    email        = form.get('email', '').strip().lower()
    service_type = form.get('service_type', '').strip()
    message      = form.get('message', '').strip()

    errors = []
    if not full_name:
        errors.append('Full name is required.')
    if not email or '@' not in email:
        errors.append('A valid email address is required.')
    if not phone:
        errors.append('Phone number is required.')
    if not service_type:
        errors.append('Please select a service type.')
    if not message:
        errors.append('Project description is required.')

    data = dict(
        full_name=full_name,
        company=company or None,
        phone=phone,
        email=email,
        service_type=service_type,
        message=message,
    )
    return errors, data


def _save_lead(data, ip_address):
    lead = Lead(
        full_name=data['full_name'],
        company=data['company'],
        phone=data['phone'],
        email=data['email'],
        service_type=data['service_type'],
        message=data['message'],
        status='new',
        ip_address=ip_address,
    )
    db.session.add(lead)
    db.session.commit()
    return lead


# ── Public routes ──────────────────────────────────────────

@main.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        errors, data = _validate_lead_form(request.form)

        if errors:
            for err in errors:
                flash(err, 'danger')
            return redirect(url_for('main.index') + '#contact')

        _save_lead(data, request.remote_addr)
        flash(
            'Thank you, {}! Your enquiry has been received. '
            'We will be in touch within 48 business hours.'.format(data['full_name']),
            'success',
        )
        return redirect(url_for('main.index') + '#contact')

    return render_template('index.html')


@main.route('/contact', methods=['GET', 'POST'])
def contact():
    """
    Named `contact` so navbar url_for('main.contact') resolves.
    POST form data is processed here too (services page submits here).
    """
    if request.method == 'POST':
        errors, data = _validate_lead_form(request.form)

        if errors:
            for err in errors:
                flash(err, 'danger')
            return redirect(url_for('main.services') + '#contact-cta')

        _save_lead(data, request.remote_addr)
        flash(
            'Thank you, {}! We will be in touch within 48 business hours.'.format(data['full_name']),
            'success',
        )
        return redirect(url_for('main.services') + '#contact-cta')

    # GET — redirect back to the homepage contact anchor
    return redirect(url_for('main.index') + '#contact')


@main.route('/services')
def services():
    return render_template('services.html')


@main.route('/services/<slug>')
def service_detail(slug):
    service = Service.query.filter_by(slug=slug, is_active=True).first_or_404()

    # Deserialise JSON columns into Python lists for the template
    for field in ('scope_items', 'applications', 'specs'):
        raw = getattr(service, field, None)
        if raw:
            try:
                setattr(service, field, json.loads(raw))
            except (ValueError, TypeError):
                setattr(service, field, [])
        else:
            setattr(service, field, [])

    return render_template('services/service_detail.html', service=service)


@main.route('/projects')
def projects():
    all_projects = (
        Project.query
        .filter_by(is_active=True)
        .order_by(Project.sort_order.asc(), Project.completed_date.desc())
        .all()
    )
    return render_template('projects.html', projects=all_projects)


@main.route('/about')
def about():
    return render_template('about_us.html')
