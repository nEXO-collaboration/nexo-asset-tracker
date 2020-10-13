import functools
from jira_requests import jira_requests
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for

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
    jira_username = session.get("jira_username")

    if jira_username is None:
        g.jira_username = None
    return


@bp.route("/login", methods=("GET", "POST"))
def login():
    error = None
    "Have user enter their Jira username and password, verify it, and store it in the session."
    if request.method == "POST":
        jira_username = request.form["jira_username"]
        jira_password = request.form["jira_password"]

        if jira_username is None:
            error = "Must specify your JIRA username."
        elif jira_password is None:
            error = "Must also specify your JIRA password."

        my_jira = jira_requests(username=jira_username, password=jira_password)
        if my_jira.verify_auth() == 0:
            error = None
        else:
            error = "Auth Denied by Jira."

        if error is None:
            print("Got here")
            # store the user id in a new session and return to the index
            session.clear()
            session["jira_username"] = jira_username
            session["jira_password"] = jira_password
            return redirect(url_for("main.index"))

        flash(error)

    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    """Clear the current session, including the stored user id."""
    session.clear()
    return redirect(url_for("index"))
