# 🏗️ Project Context: Delcon (Pipe Jacking & Infrastructure)
**Status:** Lead Generation, SEO, & Admin Dashboard Phase
**Developer:** Jonathan Roets
**Client/Business:** Delcon

---

## 🎯 Project Goals & Business Context
- **Objective:** High-value B2B lead capture, SEO dominance for niche construction terms, and a Private Admin Management dashboard.
- **The Business:** Delcon is a Level-2 BBBEE multi-disciplinary contracting service focusing on rural development, infrastructure, and trenchless technology.
- **Core Services to Highlight (From Corporate Profile):** - Pipe Jacking (900mm-2800mm) & Culvert Jacking
    - HDD - Horizontal Directional Drilling (100mm-900mm)
    - HDPE Butt-welding (90mm - 355mm)
    - General Infrastructure (Water, sewer, storm water, pipeline pressure testing)
    - Grouting (sinkhole / voids) & Guniting/shotcrete/Lateral Support
- **Contact Details (Global Variables):** - Phones: 076 941 5725 / 086 582 6796
    - Email: INFO@VANDMPROJECTS.CO.ZA (Note: May need updating to a Delcon domain)

---

## 🛠️ Tech Stack & Strict Design Rules
- **Backend:** Flask (Python), SQLite/SQLAlchemy.
    - *DB Rule:* Enforce strict constraint states and data integrity at the model level.
- **Frontend:** HTML5, Vanilla JavaScript, Bootstrap 5. 
    - *Styling Constraint:* Strictly NO Tailwind CSS. 
    - *Aesthetic/Theme:* The design MUST heavily reflect the company's Corporate Profile document. Use a bold **Black and Orange** modern construction color scheme with industrial styling. 
- **Admin Setup:** Custom internal dashboard. 
    - *Security:* Admin routes must be strictly protected.
- **Architecture:** NO CMS (e.g., WordPress). Built completely from scratch for maximum speed, SEO performance, and easy maintenance.

---

## 📂 Directory Map

pj-leads-site-flask/
├── app/                          # Main Application Package
│   ├── __init__.py               # Initializes App, DB, and Blueprints
│   ├── routes.py                 # Public SEO URL routing (Client-facing)
│   ├── admin.py                  # Admin Logic: Managing leads & content
│   ├── models.py                 # DB Schemas: Leads, Projects, Services, Settings
│   ├── static/                   # Frontend Assets (CSS/JS/Images)
│   │   └── css/                  # Custom CSS (Black & Orange CP theme)
│   └── templates/                # HTML Templates (Jinja2)
│       ├── base.html             # Master skeleton for Public site
│       ├── index.html            # Public landing page (High-conversion focus)
│       ├── projects.html             # SEO Service pages (Pipe Jacking, HDD, etc.)
|       ├── services.html
│       └── admin/                # PRIVATE ADMIN DASHBOARD
│           ├── admin_base.html   # Master skeleton for Admin area
│           ├── dashboard.html    # Admin Overview
│           ├── login.html          # login html
│           └── settings.html            # Global site settings
├── .env                          # Vault: Secret Keys & Admin Credentials
├── AI_CONTEXT.md                 # This file (AI Mapping)
├── config.py                     # Mail & DB Configuration
├── requirements.txt              # Python dependencies
└── run.py                        # Entry point