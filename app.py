from flask import Flask, render_template, request, redirect, flash, session,jsonify
from cs50 import SQL
from flask_session import Session
from Functions import validate, login_required
from werkzeug.security import check_password_hash, generate_password_hash

# Initialize the Flask application
app = Flask(__name__)

# Configure SQLite database
db = SQL("sqlite:///DataBase.db")

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Route for the landing page
@app.route("/", methods=["GET"])
def Index():
    if session.get("loggedIn"):
        return redirect("/HomePage")
    return render_template("Landing.html")

# Route for the homepage/shop
@app.route("/HomePage", methods=["GET", "POST"])
@login_required
def Shop():
    return render_template("HomePage.html")


@app.route("/HomePage/Search")
@login_required
def Search():
    search = request.args.get("search")
    if search:
        results = db.execute("SELECT * FROM users WHERE username LIKE ? ","%" + search + "%")
    else:
        results = []
    print(results)
    return jsonify(results)

# Route for user sign-up
@app.route("/SignUp", methods=["GET", "POST"])
def SignUp():
    if request.method == "POST":
        # Retrieve form data
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        email = request.form.get("email")
        phoneNumber = request.form.get("phoneNumber")

        # Check if username already exists
        if db.execute("SELECT * FROM users WHERE username = ?", (username,)):
            flash("Username already exists", "error")
            return redirect("/SignUp")

        # Validate email format
        if not validate(email):
            flash("Invalid email format", "error")
            return redirect("/SignUp")

        # Check if email already exists
        if db.execute("SELECT * FROM users WHERE email = ?", (email,)):
            flash("Email already exists", "error")
            return redirect("/SignUp")

        # Check if passwords match
        if password != confirmation:
            flash("Passwords don't match", "error")
            return redirect("/SignUp")

        # Check password length
        if len(password) < 8:
            flash("Password must be at least 8 characters long", "error")
            return redirect("/SignUp")

        # Check phone number length
        if len(phoneNumber) > 16:
            flash("Phone number must be no more than 16 characters long", "error")
            return redirect("/SignUp")

        # Check if phone number already exists
        if db.execute("SELECT * FROM users WHERE phoneNumber = ?", (phoneNumber,)):
            flash("Phone number already exists", "error")
            return redirect("/SignUp")

        # Hash the password
        hashedPassword = generate_password_hash(password, method='pbkdf2:sha256')

        # Insert new user into the database
        db.execute("INSERT INTO users (username, email, hash, phoneNumber) VALUES (?, ?, ?, ?)",username, email, hashedPassword, phoneNumber)

        # Get the user id from the newly created user
        user = db.execute("SELECT id FROM users WHERE username = ?", (username,))[0]
        session["userId"] = user["id"]
        session["loggedIn"] = True

        # Flash success message and redirect to homepage
        flash("Signed up successfully", "success")
        return redirect("/HomePage")
    else:
        # Render the sign-up page
        return render_template("SignUp.html")

# Route for user login
@app.route("/LogIn", methods=["GET", "POST"])
def Login():
    if request.method == "POST":
        # Retrieve form data
        username = request.form.get("username")
        password = request.form.get("password")

        # Fetch user data from the database
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,))
        if not user:
            flash("No username found", "error")
            return redirect("/LogIn")

        user = user[0]
        # Check if password matches
        if check_password_hash(user["hash"], password):
            session["userId"] = user["id"]
            session["loggedIn"] = True

            # Flash success message and redirect to homepage
            flash("Logged in successfully", "success")
            return redirect("/HomePage")
        else:
            flash("Invalid username and/or password", "error")
            return redirect("/LogIn")
    else:
        # Render the login page
        return render_template("LogIn.html")

# Route for user logout
@app.route("/LogOut", methods=["POST"])
@login_required
def LogOut():
    # Clear the session
    session.clear()
    # Flash success message and redirect to the landing page
    flash("Logged out successfully", "success")
    return redirect("/")

# Run the application
if __name__ == "__main__":
    app.run(debug=True)
