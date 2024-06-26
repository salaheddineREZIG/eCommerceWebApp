from email_validator import validate_email, EmailNotValidError
from flask import flash, redirect, url_for, session
from functools import wraps

def validate(email):
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        flash("Invalid email format", "error")
        return False

def login_required(f):
    """
    Decorator function to ensure that a user is logged in
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("loggedIn"):
            flash("Please log in to access this page", "error")
            return redirect(url_for("Login"))
        return f(*args, **kwargs)
    return decorated_function


