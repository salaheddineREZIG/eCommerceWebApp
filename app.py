from flask import Flask, render_template, request, redirect, flash, session
from cs50 import SQL
from flask_session import Session
from Functions import validate
from werkzeug.security import check_password_hash, generate_password_hash



app = Flask(__name__)
db = SQL("sqlite:///DataBase.db")

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/",methods=["GET"])
def Index():
    if session.get("loggedIn") == True:
        return redirect("/Shop")
    return render_template("Landing.html")

@app.route("/Shop",methods=["GET","POST"])
def Shop():
    if request.method == "GET":
        return render_template("Shop.html")
    else:
        return render_template("Shop.html")

@app.route("/SignUp", methods=["GET", "POST"])

def SignUp():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        email = request.form.get("email")
        phoneNumber = request.form.get("phoneNumber")

        if db.execute("SELECT * FROM users WHERE username = ?", username):
            flash("Username already exists", "error")
            return redirect("/SignUp")

        if not validate(email):
            flash("Invalid email format", "error")
            return redirect("/SignUp")

        if db.execute("SELECT * FROM users WHERE email =?", email):
            flash("Email already exists", "error")
            return redirect("/SignUp")

        if password != confirmation:
            flash("Passwords don't match", "error")
            return redirect("/SignUp")
        
        if len(password) < 8 or len(phoneNumber) > 16:
            flash("Password must be at least 8 characters long", "error")
            return redirect("/SignUp")      
        
        if db.execute("SELECT * FROM users WHERE phoneNumber =?", phoneNumber):
            flash("Phone Number already exists", "error")
            return redirect("/SignUp")

        hashedPassword = generate_password_hash(password, method='pbkdf2')

        db.execute("INSERT INTO users (username, email, hash, phoneNumber) VALUES (?, ?,?,?)",
                   username, email, hashedPassword, phoneNumber)

        session["userId"] = db.execute("SELECT id FROM users WHERE username = ?", username)[0]["id"]
        session["username"] = username
        session["email"] = email
        session["phoneNumber"] = phoneNumber
        session["loggedIn"] = True

        flash("Signed up successfully", "success")
        return redirect("/Shop")
    else:
        return render_template("SignUp.html")


@app.route("/LogIn", methods=["GET", "POST"])
def Login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        info = db.execute("SELECT * FROM users WHERE username = ?", username)
        if not info:
            flash("No username found", "error")
            return redirect("/LogIn")
        if info[0]["username"] == username and check_password_hash(info[0]["hash"], password):
            session["userId"] = info[0]["id"]
            session["username"] = username
            session["loggedIn"] = True

            flash("Logged in successfully", "success")
            return redirect("/Shop")
        else:
            flash("Invalid username and/or password", "error")
            return redirect("/LogIn")
    else:
        return render_template("LogIn.html")


@app.route("/LogOut", methods=["POST"])
def LogOut():
    session.clear()
    session["loggedIn"] = False
    flash("Logged out succesfully", "success")
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)