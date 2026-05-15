# Email Notification Setup Guide

This document explains how to configure the website to send form submissions directly to your email.

## 1. Choose an Email Provider
You have two main options for sending emails from the website:

### Option A: Use a Transactional Service (Recommended)
Services like **Brevo (formerly Sendinblue)** or **SMTP2GO** are designed for websites. They are more reliable and less likely to be blocked as spam.
1. Create a free account at [Brevo.com](https://www.brevo.com/).
2. Get your **SMTP Server**, **Port**, **Login**, and **Master Password**.

### Option B: Use an existing Gmail/Outlook account
1. Create a dedicated email (e.g., `website-notifications@yourdomain.com`).
2. **For Gmail**: You MUST enable 2-Factor Authentication and generate an **"App Password"**. A regular password will not work.

---

## 2. Configure the Website
All sensitive credentials are stored in a file named `.env`. This file is private and should never be shared publicly.

Update the `.env` file with your details:

```env
# The "From" address shown in the email
MAIL_DEFAULT_SENDER=notifications@yourdomain.co.za

# The email address that will RECEIVE the notifications
CONTACT_EMAIL=your-real-email@domain.com

# SMTP Credentials
MAIL_SERVER=smtp-relay.brevo.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-service-login
MAIL_PASSWORD=your-service-password

# Ensure real emails are sent (not just logged to console)
MAIL_BACKEND=flask_mailman.backends.smtp.EmailBackend
```

---

## 3. Testing
1. Save the `.env` file.
2. Restart the application.
3. Fill out the contact form on the homepage.
4. Check your inbox (and spam folder) for the notification!
