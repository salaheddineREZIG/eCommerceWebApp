from flask import Flask, render_template, request, redirect, flash, session,jsonify

from flask_session import Session

from Functions import validate, login_required_user, login_required_admin

from werkzeug.security import check_password_hash, generate_password_hash

from flask_restful import Api, Resource

from flask_sqlalchemy import SQLAlchemy

from datetime import datetime


# Initialize the Flask application

app = Flask(__name__)



# Configure SQLite database

# Configure session to use filesystem (instead of signed cookies)

app.config["SESSION_PERMANENT"] = False

app.config["SESSION_TYPE"] = "filesystem"

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///DataBase.db"

app.config["SECRET_KEY"] = "salahisthegoat"

Session(app)


db = SQLAlchemy(app)

class Users(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    userName = db.Column(db.String(20),nullable=False)

    password = db.Column(db.String(80),nullable=False)

    email = db.Column(db.String(20),nullable=False)

    phoneNumber = db.Column(db.String(20),nullable=False)
    
    

class Admins(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    userName = db.Column(db.String(20),nullable=False)

    password = db.Column(db.String(80),nullable=False)
    

admin = Admins(

    userName="admin",

    password=generate_password_hash("admin", method='pbkdf2:sha256')
    
)    

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'rating': self.rating,
            'comment': self.comment,
            'product_id': self.product_id,
            'user_id': self.user_id,
            'created_at': self.created_at
        }


class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    stock_quantity = db.Column(db.Integer, nullable=False, default=0)
    sku = db.Column(db.String(30), unique=True, nullable=False)
    brand = db.Column(db.String(50), nullable=True)
    weight = db.Column(db.Float, nullable=True)
    dimensions = db.Column(db.String(50), nullable=True)
    color = db.Column(db.String(30), nullable=True)
    size = db.Column(db.String(30), nullable=True)
    material = db.Column(db.String(50), nullable=True)
    features = db.Column(db.Text, nullable=True)
    tags = db.Column(db.String(100), nullable=True)
    discount_price = db.Column(db.Float, nullable=True)
    availability_status = db.Column(db.String(20), nullable=False, default='In Stock')
    rating = db.Column(db.Float, nullable=True)
    reviews = db.relationship('Review', backref='product', lazy=True)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_modified = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'category_id': self.category_id,
            'image_file': self.image_file,
            'stock_quantity': self.stock_quantity,
            'sku': self.sku,
            'brand': self.brand,
            'weight': self.weight,
            'dimensions': self.dimensions,
            'color': self.color,
            'size': self.size,
            'material': self.material,
            'features': self.features,
            'tags': self.tags,
            'discount_price': self.discount_price,
            'availability_status': self.availability_status,
            'rating': self.rating,
            'reviews': [review.to_dict() for review in self.reviews],
            'date_added': self.date_added,
            'date_modified': self.date_modified
        }


class Categories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    image_file = db.Column(db.String(20), nullable=True, default='default.jpg')
    slug = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    parent = db.relationship('Categories', remote_side=[id], backref='subcategories')

    products = db.relationship('Products', backref='category', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'parent_id': self.parent_id,
            'image_file': self.image_file,
            'slug': self.slug,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'subcategories': [sub.to_dict() for sub in self.subcategories]
        }
        
        
class AdminProducts(Resource):

    def get(self):
        products = Products.query.all()

        return jsonify([product.serialize() for product in products])
    

    def post(self):
        data = request.get_json()

        name = data.get('name')
        description = data.get('description')
        price = data.get('price')
        category_id = data.get('category_id')
        image_file = data.get('image_file', 'default.jpg')
        stock_quantity = data.get('stock_quantity', 0)
        sku = data.get('sku')
        brand = data.get('brand')
        weight = data.get('weight')
        dimensions = data.get('dimensions')
        color = data.get('color')
        size = data.get('size')
        material = data.get('material')
        features = data.get('features')
        tags = data.get('tags')
        discount_price = data.get('discount_price')
        availability_status = data.get('availability_status', 'In Stock')
        rating = data.get('rating')
        date_added = datetime.utcnow()
        date_modified = datetime.utcnow()

        new_product = Products(
            name=name,
            description=description,
            price=price,
            category_id=category_id,
            image_file=image_file,
            stock_quantity=stock_quantity,
            sku=sku,
            brand=brand,
            weight=weight,
            dimensions=dimensions,
            color=color,
            size=size,
            material=material,
            features=features,
            tags=tags,
            discount_price=discount_price,
            availability_status=availability_status,
            rating=rating,
            date_added=date_added,
            date_modified=date_modified
        )

        db.session.add(new_product)
        db.session.commit()

        return jsonify(new_product.to_dict()), 201  
    
    
class AdminProductsById(Resource):
    
    def get(self,id):
        
        product = Products.query.filter_by(id=id).first()
        
        return jsonify(product.serialize()), 200
    
    def put(self,id):
        
        data = request.get_json()
        
        product = Products.query.filter_by(id=id).first()
        
        product.name = data.get('name')
        product.description = data.get('description')
        product.price = data.get('price')
        product.category_id = data.get('category_id')
        product.image_file = data.get('image_file', 'default.jpg')
        product.stock_quantity = data.get('stock_quantity', 0)
        product.sku = data.get('sku')
        product.brand = data.get('brand')
        product.weight = data.get('weight')
        product.dimensions = data.get('dimensions')
        product.color = data.get('color')
        product.size = data.get('size')
        product.material = data.get('material')
        product.features = data.get('features')
        product.tags = data.get('tags')
        product.discount_price = data.get('discount_price')
        product.availability_status = data.get('availability_status', 'In Stock')
        product.rating = data.get('rating')
        product.date_modified = datetime.utcnow()
        
        db.session.commit()
        
        flash("Product updated successfully", "success")
        
        return jsonify(product.serialize()), 200
    
    def delete(self,id):
        
        product = Products.query.filter_by(id=id).first()
        
        if product:
            db.session.delete(product)
            db.session.commit()
            
            return jsonify({"message": "Product deleted successfully"}), 200
        else:
            return jsonify({"message": "Product not found"}), 404

# Route for the landing page

@app.route("/", methods=["GET"])

def Index():

    if session.get("loggedIn"):

        return redirect("/HomePage")

    return render_template("Landing.html")


# Route for the homepage/shop

@app.route("/HomePage", methods=["GET", "POST"])

@login_required_user

def Shop():

    return render_template("HomePage.html")



@app.route("/HomePage/Search")

@login_required_user

def Search():

    search = request.args.get("search")

    results = []

    if search:

        queries = Users.query.filter(Users.userName.like(search + '%')).all()

        for query in queries:

            element = {

                "username": query.userName

            }
            results.append(element)
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

        if Users.query.filter_by(userName = username).first():

            flash("Username already exists", "error")

            return redirect("/SignUp")


        # Validate email format

        if not validate(email):

            flash("Invalid email format", "error")

            return redirect("/SignUp")


        # Check if email already exists

        if Users.query.filter_by(email = email).first():

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

        if Users.query.filter_by(phoneNumber = phoneNumber).first():

            flash("Phone number already exists", "error")

            return redirect("/SignUp")


        # Hash the password

        hashedPassword = generate_password_hash(password, method='pbkdf2:sha256')


        # Insert new user into the database

        newUser = Users(

            userName=username,

            email=email,

            phoneNumber=phoneNumber,

            password=hashedPassword
        )

        db.session.add(newUser)

        db.session.commit()
        

        # Get the user id from the newly created user

        user = Users.query.filter_by(userName = username).first()

        session["userId"] = user.id
        
        session["admin"] = False


        session["loggedIn"] = True


        # Flash success message and redirect to homepage

        flash("Signed up successfully", "success")

        return redirect("/HomePage")

    else:

        # Render the sign-up page

        return render_template("SignUp.html")


# Route for user login

@app.route("/LogIn", methods=["GET", "POST"])

def LogIn():

    if request.method == "POST":

        # Retrieve form data

        username = request.form.get("username")

        password = request.form.get("password")


        # Fetch user data from the database

        user = Users.query.filter_by(userName=username).first()

        if not user:

            flash("No username found", "error")

            return redirect("/LogIn")


        # Check if password matches

        if check_password_hash(user.password, password):

            session["userId"] = user.id
            
            session["admin"] = False

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



def LogOut():

    # Clear the session
    session.clear()

    # Flash success message and redirect to the landing page

    flash("Logged out successfully", "success")

    return redirect("/")


@app.route("/AdminPanel/LogIn", methods=["GET", "POST"])

def AdminLogIn():

    if request.method == "POST":

        # Retrieve form data

        username = request.form.get("username")

        password = request.form.get("password")


        # Fetch user data from the database
        admin = Admins.query.filter_by(userName=username).first()
        if not admin:

            flash("No username found", "error")

            return redirect("/AdminPanel/LogIn")


        # Check if password matches

        if check_password_hash(admin.password, password):

            session["userId"] = admin.id
            
            session["admin"] = True

            session["loggedIn"] = True


            # Flash success message and redirect to homepage

            flash("Logged in successfully", "success")

            return redirect("/AdminPanel/Dashboard")

        else:

            flash("Invalid username and/or password", "error")

            return redirect("/AdminPanel/LogIn")

    else:

        # Render the login page

        return render_template("AdminLogIn.html")
    

@app.route("/AdminPanel/Dashboard", methods=["GET"])
@login_required_admin

def Dashboard():

    return render_template("AdminDashboard.html")
    

# Run the application

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  
        if not Admins.query.filter_by(userName="admin").first():
            db.session.add(admin)
            db.session.commit()
    app.run(debug=True)


