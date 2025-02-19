import functools

from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from batweb.db import get_db

bp = Blueprint("auth", __name__, url_prefix="/auth")


def login_required(view):
    """View decorator that redirects anonymous users to the login page."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    """If a user id is stored in the session, load the user object from
    the database into ``g.user``."""
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = (
            get_db().execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
        )


@bp.route("/register", methods=("GET", "POST"))
def register():
    """Register a new user.
    Validates that the username is not already taken. Hashes the
    password for security.
    """
    if request.method == "POST":
        mail = request.form["mail"]
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        db = get_db()
        error = None

        if not mail:
            error = "Mail is required."
        elif not firstname:
            error = "Firstname is required."
        elif not lastname:
            error = "Lastname is required."
        elif not password1 or not password2:
            error = "Password is required."
        elif password1 != password2:
            error = "Passwords must be the same."
        elif len(password1) < 8:
            error = "The password's length must be higher than 7"
        elif (
            db.execute("SELECT id FROM user WHERE mail = ?", (mail,)).fetchone()
            is not None
        ):
            error = "Mail {0} is already registered.".format(mail)

        if error is None:
            # the name is available, store it in the database and go to
            # the login page
            db.execute(
                "INSERT INTO user (mail, password, firstname, lastname) VALUES (?, ?, ?, ?)",
                (mail, generate_password_hash(password1), firstname, lastname),
            )
            db.commit()
            return redirect(url_for("auth.login"))

        flash(error)

    return render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    """Log in a registered user by adding the user id to the session."""
    if request.method == "POST":
        mail = request.form["mail"]
        password = request.form["password"]
        db = get_db()
        error = None
        user = db.execute(
            "SELECT * FROM user WHERE mail = ?", (mail,)
        ).fetchone()

        if user is None:
            error = "Incorrect mail."
        elif not check_password_hash(user["password"], password):
            error = "Incorrect password."

        if error is None:
            # store the user id in a new session and return to the index
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("index"))

        flash(error)

    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    """Clear the current session, including the stored user id."""
    session.clear()
    return redirect(url_for("index"))
