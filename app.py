from flask import Flask, render_template, request, redirect, flash, session, jsonify, url_for, make_response
from flask_session import Session
from Functions import validate, login_required_user, login_required_admin
from werkzeug.security import check_password_hash, generate_password_hash
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import func, desc

# Initialize the Flask application
app = Flask(__name__, static_folder='static')
api = Api(app)

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
    userName = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    phoneNumber = db.Column(db.String(20), nullable=False)
    profilePicture = db.Column(db.String(100), nullable=False, default='default.png')

    def to_dict(self):
        return {
            'id': self.id,
            'userName': self.userName,
            'email': self.email,
            'phoneNumber': self.phoneNumber
        }


class Admins(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userName = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    profilePicture = db.Column(db.String(100), nullable=False, default='default.png')

    def to_dict(self):
        return {
            'id': self.id,
            'userName': self.userName
        }


admin = Admins(
    userName="admin",
    password=generate_password_hash("admin", method='pbkdf2:sha256')
)


class Reviews(db.Model):
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
    reviews = db.relationship('Reviews', backref='product', lazy=True)
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
    image_file = db.Column(db.String(20), nullable=True, default='default.jpg')
    slug = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    products = db.relationship('Products', backref='category', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'image_file': self.image_file,
            'slug': self.slug,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }


class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default='Pending')
    total_amount = db.Column(db.Float, nullable=False)
    shipping_address = db.Column(db.String(200), nullable=False)
    order_items = db.relationship('Sales', backref='order', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'order_date': self.order_date,
            'status': self.status,
            'total_amount': self.total_amount,
            'shipping_address': self.shipping_address,
            'order_items': [item.to_dict() for item in self.order_items]
        }


class Sales(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, nullable=True)
    total_price = db.Column(db.Float, nullable=False)
    product = db.relationship('Products', backref='sales', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'discount': self.discount,
            'total_price': self.total_price
        }




class AdminProducts(Resource):

    def get(self):
        products = Products.query.all()
        productList = []
        for product in products:
            category = Categories.query.filter_by(id=product.category_id).first()
            product.category_name = category.name
            productList.append(product.to_dict())
        return make_response(jsonify(productList), 200)

    def post(self):
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        category_id = request.form.get('category_id')
        stock_quantity = request.form.get('stock_quantity')
        sku = request.form.get('sku')
        brand = request.form.get('brand')
        weight = request.form.get('weight')
        dimensions = request.form.get('dimensions')
        color = request.form.get('color')
        size = request.form.get('size')
        material = request.form.get('material')
        features = request.form.get('features')
        tags = request.form.get('tags')
        discount_price = request.form.get('discount_price')
        availability_status = request.form.get('availability_status')
        image_file = request.files['image_file']

        # Save the image file if necessary
        if image_file:
            image_filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
        else:
            image_filename = 'default.jpg'

        product = Products(
            name=name,
            description=description,
            price=price,
            category_id=category_id,
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
            image_file=image_filename
        )

        db.session.add(product)
        db.session.commit()
        return make_response(jsonify({"message": "Product created successfully"}), 201)
    
    def delete(self, id):
        product = Products.query.filter_by(id=id).first()
        if product:
            db.session.delete(product)
            db.session.commit()
            return make_response(jsonify({"message": "Product deleted successfully"}), 200)
        else:
            return make_response(jsonify({"message": "Product not found"}), 404)

        
class AdminCategories(Resource):

    def get(self):
        categories = Categories.query.all()
        categories_list = [category.to_dict() for category in categories]
        return make_response(jsonify(categories_list), 200)
    
    def post(self):
        data = request.form
        new_category = Categories(
            name=data.get('name'),
            description=data.get('description'),
            image_file=data.get('image_file', 'default.jpg'),
            slug=data.get('slug')
        )
        
        db.session.add(new_category)
        db.session.commit()
        
        return make_response(jsonify({"message": "Category created successfully"}), 201)

    def put(self, id):  
        data = request.form
        category = Categories.query.filter_by(id=id).first()
        if category:
            category.name = data.get('name')
            category.description = data.get('description')
            category.image_file = data.get('image_file', 'default.jpg')
            category.slug = data.get('slug')
            category.updated_at = datetime.utcnow()
            db.session.commit()
            return make_response(jsonify({"message": "Category updated successfully"}), 200)
        else:
            return make_response(jsonify({"message": "Category not found"}), 404)

    def delete(self, id):
        category = Categories.query.filter_by(id=id).first()
        if category:
            db.session.delete(category)
            db.session.commit()
            return make_response(jsonify({"message": "Category deleted successfully"}), 200)
        else:
            return make_response(jsonify({"message": "Category not found"}), 404)
        
        
class AdminUsers(Resource):

    def get(self):
        users = Users.query.all()
        for user in users:
            print (user)
        users_list = [user.to_dict() for user in users]
        return make_response(jsonify(users_list), 200)
    

    def delete(self, id):
        user = Users.query.filter_by(id=id).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            return make_response(jsonify({"message": "User deleted successfully"}), 200)
        else:
            return make_response(jsonify({"message": "User not found"}), 404)


class AdminDashboard(Resource):

    def get(self):
        
        
        TopSalesQuery = db.session.query(
            Sales.product_id,
            func.sum(Sales.total_price).label('total_sales')
        ).group_by(Sales.product_id).order_by(desc('total_sales')).limit(5)

        topSales = TopSalesQuery.all()

        topSalesList = [{'product_id': Products.query.filter_by(id=product_id).first().name, 'total_sales': total_sales} for product_id, total_sales in topSales]
        stats = {
            "totalProducts": Products.query.count(),
            "totalCategories": Categories.query.count(),
            "totalUsers": Users.query.count(),
            "totalOrders": Orders.query.count(),
            "totalSales": Sales.query.count(),
            "newOrders": [order.to_dict() for order in Orders.query.order_by(Orders.id.desc()).limit(5).all()],
            "newReviews": [review.to_dict() for review in Reviews.query.order_by(Reviews.id.desc()).limit(5).all()],
            "topSales": topSalesList,
        }
        
        return make_response(jsonify(stats),200)

api.add_resource(AdminCategories, '/AdminPanel/Categories/OPS', '/AdminPanel/Categories/OPS/<int:id>')
api.add_resource(AdminUsers, '/AdminPanel/Users/OPS', '/AdminPanel/Users/OPS/<int:id>')
api.add_resource(AdminDashboard, '/AdminPanel/Dashboard/Stats')
api.add_resource(AdminProducts, '/AdminPanel/Products/OPS', '/AdminPanel/Products/OPS/<int:id>')
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

def UsersSearch():

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

@app.route("/AdminPanel/Dashboard/Search")

def AdminsSearch():

    search = request.args.get("search")
    searchType = request.args.get("type")
    print(searchType + " " + search)

    results = []

    if search and searchType:
        if searchType == "users":
            queries = Users.query.filter(Users.userName.like(search + "%")).all()
            for query in queries:
                results.append({"userName": query.userName})
        
        elif searchType == "products":
            queries = Products.query.filter(Products.name.like(search + "%")).all()
            for query in queries:
                results.append({"product": query.name})

        elif searchType == "categories":
            queries = Categories.query.filter(Categories.name.like(search + "%")).all()
            for query in queries:
                results.append({"category": query.name})

        elif searchType == "reviews":
            queries = Reviews.query.filter(Reviews.comment.like(search + "%")).all()
            for query in queries:
                results.append({"reviewText": query.comment})

    for result in results:
        print (result)
        
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

@app.route("/LogOut", methods=["GET","POST"])



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

def Dashboard():

    return render_template("AdminDashboard.html")
    
    
@app.route("/AdminPanel/Products", methods=["GET", "POST"])

def ProductsRoute():

    return render_template("AdminProducts.html")

@app.route("/AdminPanel/Categories", methods=["GET", "POST"])
def CategoriesRoute():

    return render_template("AdminCategories.html")

@app.route("/AdminPanel/Users", methods=["GET", "POST"])
def UsersRoute():
    
    return render_template("AdminUsers.html")

# Run the application


if __name__ == "__main__":
    with app.app_context():

        db.create_all()
        admin = Admins.query.filter_by(userName="admin").first()
        if not admin:
            admin = Admins(
                userName="admin",
                password=generate_password_hash("admin", method='pbkdf2:sha256')
            )
            db.session.add(admin)
            db.session.commit()
    app.run(debug=True)

