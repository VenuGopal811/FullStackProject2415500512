import os
from pathlib import Path
from typing import Any

from flask import Flask, flash, redirect, render_template, request, url_for

from .forms import LoginForm, RegisterForm
from .models import User, db


def _normalize_database_url(database_url: str) -> str:
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql://", 1)
    return database_url


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)

    instance_path = Path(app.instance_path)
    instance_path.mkdir(parents=True, exist_ok=True)

    default_database = f"sqlite:///{(instance_path / 'fullstack.db').as_posix()}"
    database_url = os.getenv("DATABASE_URL", default_database)
    secret_key = os.getenv("SECRET_KEY") or "dev-only-secret-key"

    app.config.update(
        SECRET_KEY=secret_key,
        SQLALCHEMY_DATABASE_URI=_normalize_database_url(database_url),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ENGINE_OPTIONS={"pool_pre_ping": True},
    )

    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.route("/")
    def home():
        projects = [
            {
                "title": "Jinja Student List",
                "description": "Simple templating example rendered from Flask.",
                "endpoint": "students",
                "cta": "Open student list",
            },
            {
                "title": "Validated Form",
                "description": "Server-side validation for name, mobile, and password.",
                "endpoint": "form_demo",
                "cta": "Open validation form",
            },
            {
                "title": "Auth Demo",
                "description": "Registration and login backed by SQLAlchemy.",
                "endpoint": "register",
                "cta": "Open auth flow",
            },
        ]
        return render_template("home.html", projects=projects)

    @app.route("/students")
    def students():
        student_list = ["student1", "student2", "student3"]
        return render_template("students.html", students=student_list)

    @app.route("/form-demo", methods=["GET", "POST"])
    def form_demo():
        errors = []
        submitted_name = None

        if request.method == "POST":
            submitted_name = request.form.get("name", "").strip()
            mobile = request.form.get("mobile", "").strip()
            password = request.form.get("password", "")

            if len(submitted_name) < 5:
                errors.append("Username must be at least 5 characters long.")

            if not mobile.isdigit() or len(mobile) < 10:
                errors.append("Mobile number must be at least 10 digits long.")

            if len(password) < 8:
                errors.append("Password must be at least 8 characters long.")

            if not errors:
                return render_template("form_success.html", name=submitted_name)

        return render_template("form_demo.html", errors=errors, submitted_name=submitted_name)

    @app.route("/auth/register", methods=["GET", "POST"])
    def register():
        form = RegisterForm()

        if form.validate_on_submit():
            existing_user = User.query.filter(
                (User.username == form.username.data) | (User.email == form.email.data)
            ).first()

            if existing_user is not None:
                flash("A user with that username or email already exists.", "error")
            else:
                user = User(username=form.username.data, email=form.email.data)
                user.set_password(form.password.data)
                db.session.add(user)
                db.session.commit()
                flash("Registration successful. You can log in now.", "success")
                return redirect(url_for("login"))

        return render_template("register.html", form=form)

    @app.route("/auth/login", methods=["GET", "POST"])
    def login():
        form = LoginForm()

        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user is None or not user.check_password(form.password.data):
                flash("Invalid username or password.", "error")
            else:
                flash(f"Welcome back, {user.username}.", "success")
                return redirect(url_for("home"))

        return render_template("login.html", form=form)

    return app