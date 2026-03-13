# FullStack Deployment Guide

This workspace originally contained several standalone Flask exercises. It now includes one deployment target at the repository root:

- `wsgi.py` is the production entrypoint.
- `fullstack_app/` contains the deployable Flask application.
- The older exercise folders remain in place for reference.

## What is deployable now

The root app exposes these routes:

- `/` home page for the workspace
- `/students` Jinja list example
- `/form-demo` validated form example
- `/auth/register` SQLAlchemy-backed registration
- `/auth/login` SQLAlchemy-backed login check

## Local setup

1. Create and activate a virtual environment.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and update values.
4. Start the app:

   ```bash
   python wsgi.py
   ```

## Production configuration

Set these environment variables in your hosting platform:

- `SECRET_KEY`: required, use a long random value
- `DATABASE_URL`: optional, defaults to local SQLite. For managed Postgres use a SQLAlchemy URL.
- Python runtime: pinned in `.python-version` so hosts such as Render do not default to Python 3.14.

Example PostgreSQL URL:

```text
postgresql://username:password@host:5432/database_name
```

## Deployment command

Use the Procfile command or configure the platform start command as:

```bash
gunicorn wsgi:app
```

## Render note

If Render was previously trying to build with Python 3.14, redeploy after pulling the latest commit. This repository now pins Python `3.12.6` and uses a `psycopg` version that has compatible binary wheels.

## Notes

- SQLite is fine for quick demos. Use Postgres or another managed database for real deployment.
- `db.create_all()` runs automatically on startup for this small project. For larger apps, switch to migrations.
