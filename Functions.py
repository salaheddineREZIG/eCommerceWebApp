from email_validator import validate_email, EmailNotValidError
from flask import Flask,flash, redirect, url_for,request,make_response
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
from models import db, Users, Admins
from flask_migrate import Migrate
import jwt


secretKey = None

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
    global secretKey
    secretKey = os.getenv("SECRET_KEY", "salahisthegoat")
    app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024
    app.config['UPLOAD_FOLDER'] = os.path.join('static', 'images', 'uploads')
    app.config['SESSION_COOKIE_SECURE'] = True


    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    
    db.init_app(app)
    migrate = Migrate(app, db)
    
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
        token = request.cookies.get("token")
        token = token.encode('utf-8')
        
        if not token:
            flash("token is missing!","error")
            return make_response(redirect("/HomePage"))
        
        try:
            data = jwt.decode(token, secretKey, algorithms=["HS256"])
            currentUser = Users.query.filter_by(userName=data["userName"]).first()
        except jwt.ExpiredSignatureError:
            flash("Token Expired","error")
            return make_response(redirect("/UserPanel/LogIn"))
        except jwt.InvalidTokenError:
            flash("Invalid Token","error")
            return make_response(redirect("/UserPanel/LogIn"))
        
        if not currentUser:
            flash("Must Log in","error")
            
            return make_response(redirect("/UserPanel/LogIn"))
        if not data["isAdmin"]:
            currentUser = currentUser.to_dict()
            return f(currentUser,*args, **kwargs)
        else:
            flash("You are not authorized to access this page","error")
            return make_response(redirect("/LogIn"))
        
    return decorated_function


def login_required_admin(f):
    """
    Decorator function to ensure that a user is logged in
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get("token")
        token = token.encode('utf-8')
        
        if not token :
            flash("Token Missing","error")
            return make_response(redirect("/AdminPanel/LogIn"))
            
        try:
            
            data = jwt.decode(token, secretKey, algorithms=["HS256"])
            currentUser = Admins.query.filter_by(userName=data["userName"]).first()
        except jwt.ExpiredSignatureError:
            flash("Token Expired","error")
            return make_response(redirect("/AdminPanel/LogIn"))
        except jwt.InvalidTokenError:
            flash("Invalid Token","error")
            return make_response(redirect("/AdminPanel/LogIn"))
        
        if not currentUser:
            flash("Must Log in","error")
            return make_response(redirect("/AdminPanel/LogIn"))        
        
        if data["isAdmin"]:
            currentUser = currentUser.to_dict()
            return f(currentUser,*args, **kwargs)
        else:
            flash("You are not authorized to access this page","error")
            return make_response(redirect("/AdminPanel/LogIn"))
    return decorated_function


def get_info(mod):
    token = request.cookies.get("token")
    
    if not token :
        return None

    try:
        data = jwt.decode(token, secretKey, algorithms=["HS256"])
        currentUser = mod.query.filter_by(userName=data["userName"]).first()
        return currentUser
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    

def get_float(value, default=0.0):
    try:
        return float(value) if value else default
    except ValueError:
        return default