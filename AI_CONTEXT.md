# 🏗️ Project Context: [Morne] Pipe Jacking
**Status:** Lead Generation, SEO, & Admin Dashboard Phase
**Developer:** Jonathan Roets

---

## 🎯 Project Goals & Rules
- **Objective:** High-value B2B lead capture + Private Admin Management.
- **Tech Stack:** Flask (Backend), Vanilla JS, Bootstrap 5.
- **Admin Setup:** Custom internal dashboard for content & lead management.
- **Constraints:** 
    - **NO CMS:** Built from scratch for maximum SEO performance.
    - **Modular CSS:** Cinema-dark or Industrial-steel variables.
    - **Security:** Admin routes must be protected (access restricted to Jonathan).

---

## 📂 Directory Map

pj-leads-site-flask/
├── app/                          # Main Application Package
│   ├── __init__.py               # Initializes App, DB, and Blueprints
│   ├── routes.py                 # Public SEO URL routing (Client-facing)
│   ├── admin.py                  # Admin Logic: Managing leads & content
│   ├── models.py                 # DB Schemas: Leads, Projects, Services, Settings
│   ├── static/                   # Frontend Assets (CSS/JS/Images)
│   └── templates/                # HTML Templates (Jinja2)
│       ├── base.html             # Master skeleton for Public site
│       ├── index.html            # Public landing page
│       ├── services/             # SEO Service pages
│       └── admin/                # PRIVATE ADMIN DASHBOARD
│           ├── admin_base.html   # Master skeleton for Admin area
│           ├── dashboard.html    # Admin Overview
│           ├── inquiries_manage.html    # Lead/Contact message management
│           ├── login.html          # login html
│           ├── products_manage.html # Equipment/Product editor
│           ├── projects_manage.html # Case study/Gallery editor
│           ├── service_form.html        # Form to add/edit services
│           └── settings.html            # Global site settings (Phone, Email, etc.)
├── .env                          # Vault: Secret Keys & Admin Credentials
├── AI_CONTEXT.md                 # This file (AI Mapping)
├── config.py                     # Mail & DB Configuration
├── requirements.txt              # Python dependencies
└── run.py                        # Entry point