# NOUSVA website (Django)

A responsive editorial website for NOUSVA, an AI agents and automation company, with a Django backend.

## Website assistant

The floating service assistant works without an external provider key using built-in service-guide replies. To enable generative AI responses, add `OPENAI_API_KEY` to the Render web service environment. Optionally set `OPENAI_MODEL` (defaults to `gpt-4o-mini`) and `OPENAI_API_URL` (defaults to the OpenAI-compatible chat-completions endpoint). Keep credentials in the hosting provider's environment settings; never put them in browser JavaScript or commit them to Git.

## Accounts and editorial content

Visitors can create an account, sign in, and access a session-protected account page. Django's built-in password validators are enabled. Email verification and password-reset email delivery are not configured. Proof cards are explicitly labeled illustrative placeholders until real customer reviews are approved; the insight articles are original editorial guidance. Service photographs are loaded from Unsplash.

## What is in it

- **Backend:** Django 5, SQLite by default.
  - Contact form saves enquiries (`/api/contact/`).
  - "Free AI visibility check" form saves requests (`/api/audit/`).
  - Both have validation, a hidden honeypot field, CSRF protection, a per-IP rate limit, and optional email notification.
  - Admin at `/admin/` to read enquiries, mark them handled, and edit the **Services** and **FAQs** shown on the page.
- **Frontend:** warm paper and terracotta palette, editorial serif headings, responsive navigation and layouts, service detail pages, customer assistant, live form validation, savings estimator, and FAQ accordion.

Default contact details are `eshanmahey17@gmail.com` and WhatsApp `9258679510`. They can be changed with `CONTACT_EMAIL`, `CONTACT_PHONE`, and `WHATSAPP_PHONE` environment variables.

## Run it locally

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations core   # first run only: creates the database tables' blueprint
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/ and the admin at http://127.0.0.1:8000/admin/.

Run the tests with `python manage.py test`. They cover the page, form validation, the honeypot, the rate limit and saving to the database.

## Set your details

Set these environment variables (or edit `config/settings.py`):

| Variable | Purpose |
| --- | --- |
| `SITE_NAME` | Your company name (default "NOUSVA") |
| `CONTACT_EMAIL`, `CONTACT_PHONE` | Shown in the contact section |
| `NOTIFY_EMAIL` | Where new enquiries are emailed (empty = database only) |
| `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | SMTP settings. Without these, emails print in the terminal |

## Deploy

The project uses SQLite locally. On a host, set `DATABASE_URL` to use PostgreSQL instead; do not rely on a local SQLite file for production data.

For a beginner-friendly Render deployment:

1. Push this project to a GitHub repository. The `.gitignore` excludes your local virtual environment, SQLite database, and collected static files.
2. Create a PostgreSQL database on Render and copy its internal connection URL. Treat this URL as a password.
3. Create a Render Web Service connected to the repository, using these commands:

  - Build: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
  - Start: `python -m gunicorn config.wsgi:application`

4. Add these environment variables to the web service. Generate `DJANGO_SECRET_KEY` in Render; do not put it in the repository.

  | Variable | Value |
  | --- | --- |
  | `DATABASE_URL` | The PostgreSQL internal connection URL |
  | `DJANGO_DEBUG` | `0` |
  | `DJANGO_SECRET_KEY` | A generated secret value |
  | `DJANGO_ALLOWED_HOSTS` | Your Render hostname, such as `your-site.onrender.com` |
  | `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://your-site.onrender.com` |

5. Deploy and check the build log. Open the public HTTPS URL and verify that the page and its CSS load.
6. In the Render Shell, run `python manage.py createsuperuser`, then sign in at `/admin/` and test the forms.

For a custom domain, add its hostname to `DJANGO_ALLOWED_HOSTS` and its `https://` origin to `DJANGO_CSRF_TRUSTED_ORIGINS`. Consider setting `DJANGO_HSTS_SECONDS=31536000` only after HTTPS is confirmed working for every hostname.

## Customising

- Colours: the CSS variables at the top of `static/css/site.css`.
- Copy and layout: `templates/core/index.html`.
- Behaviour and effects: `static/js/site.js`.
- Services and FAQs: add them in the admin. Until you add any, defaults from `core/views.py` are shown.
