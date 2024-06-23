from email_validator import validate_email, EmailNotValidError
from flask import Flask,flash, redirect, url_for, session
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
from models import db
from flask_migrate import Migrate
from flask_session import Session



ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



def create_app():
    
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///DataBase.db")
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "salahisthegoat")
    app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024
    app.config['UPLOAD_FOLDER'] = os.path.join('static', 'images', 'uploads')

    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    
    db.init_app(app)
    migrate = Migrate(app, db)
    Session(app)
    
    with app.app_context():
        db.create_all()
    
    return app


def validate(email):
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        flash("Invalid email format", "error")
        return False

def login_required_user(f):
    """
    Decorator function to ensure that a user is logged in
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("loggedIn") or session.get("admin"):
            flash("Please log in to access this page", "error")
            return redirect(url_for("LogIn"))
        return f(*args, **kwargs)
    return decorated_function


def login_required_admin(f):
    """
    Decorator function to ensure that a user is logged in
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("loggedIn") or not session.get("admin"):
            flash("Please log in to access this page", "error")
            return redirect(url_for("AdminLogIn"))
        return f(*args, **kwargs)
    return decorated_function

