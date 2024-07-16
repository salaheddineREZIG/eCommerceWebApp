from flask import Flask, render_template, request, redirect, flash, session, jsonify, url_for, make_response
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
import os
from functools import wraps
from Functions import login_required_user, login_required_admin, validate, create_app, allowed_file
from models import db, Users, Admins, Orders, Products, Categories, Reviews, ShippingDetails, Wishlists, Sales, ProductAttributes, Carts
from PIL import Image

app = create_app()
api = Api(app)


class FileManager(Resource):
    @login_required_admin
    def post(self):
        image_file = request.files.get('file')
        if image_file:
            return self.upload_file(image_file)
        return {"message": "No image file provided"}, 400
    
    @login_required_admin
    def delete(self, filename):
        return self.delete_file(filename)

    @staticmethod
    def upload_file(image_file):
        try:
            image_filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image_file.save(image_path)
            return {"message": "Image uploaded successfully", "image_file": image_filename}, 200
        except Exception as e:
            return {"error": str(e)}, 500

    @staticmethod
    def delete_file(filename):
        try:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if not os.path.exists(file_path):
                return {"message": "Image not found"}, 404
            os.remove(file_path)
            return {"message": "Image deleted successfully"}, 200
        except Exception as e:
            return {"error": str(e)}, 500


class AdminProducts(Resource):
    
    @login_required_admin
    def get(self):
        try:
            products = Products.query.all()
            productList = []
            for product in products:
                category = Categories.query.filter_by(id=product.category_id).first()
                product.category_name = category.name
                productList.append(product.to_dict())
            return make_response(jsonify(productList), 200)
        except SQLAlchemyError as e:
            return make_response(jsonify({"error": str(e)}), 500)
        
        
    @login_required_admin
    def post(self):
        try:
            data = request.form
            name = data.get('name')
            description = data.get('description')
            slug = data.get('slug')
            price = data.get('price', type=float)
            category_id = data.get('category_id', type=int)
            stock_quantity = data.get('stock_quantity', type=int)
            sku = data.get('sku')
            brand = data.get('brand')
            weight = data.get('weight', type=float, default=0.0)
            dimensions = data.get('dimensions')
            color = data.get('color')
            size = data.get('size')
            material = data.get('material')
            features = data.get('features')
            tags = data.get('tags')
            discount_price = data.get('discount_price', type=float, default=0.0)
            availability_status = data.get('availability_status')

            if not name or not description or not slug or price is None or category_id is None:
                return make_response(jsonify({"error": "Missing required fields"}), 400)

            image_file = request.files.get('image_file')
            image_filename = 'default.jpg'

            if image_file:
                upload_result, status_code = FileManager.upload_file(image_file)
                if status_code == 200:
                    image_filename = upload_result["image_file"]
                else:
                    return make_response(jsonify({"error": upload_result["message"]}), status_code)

            product = Products(
                name=name,
                description=description,
                slug=slug,
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

        except SQLAlchemyError as e:
            db.session.rollback()
            return make_response(jsonify({"error": str(e)}), 500)
        except Exception as e:
            return make_response(jsonify({"error": str(e)}), 500)
            
    @login_required_admin
    def delete(self, slug):
        try:
            product = Products.query.filter_by(slug=slug).first()
            if product:
                image_file = product.image_file
                
                if image_file and image_file != 'default.jpg':
                    delete_result, status_code = FileManager.delete_file(image_file)
                    if status_code != 200:
                        return make_response(jsonify({"error": delete_result["message"]}), status_code)
                    
                db.session.delete(product)
                db.session.commit()
                return make_response(jsonify({"message": "Product deleted successfully"}), 200)
            else:
                return make_response(jsonify({"message": "Product not found"}), 404)
        except SQLAlchemyError as e:
            return make_response(jsonify({"error": str(e)}), 500)
    
    @login_required_admin
    def put(self, slug):
        try:
            product = Products.query.filter_by(slug=slug).first()
            if product:
                data = request.form
                product.name = data.get('name')
                product.description = data.get('description')
                product.slug = data.get('slug')
                product.price = data.get('price')
                product.category_id = data.get('category_id')
                product.stock_quantity = data.get('stock_quantity')
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
                product.availability_status = data.get('availability_status')
                new_image_file = request.files.get('image_file')

                if new_image_file:
                    if not (product.image_file == 'default.jpg') :
                        FileManager.delete_file(product.image_file)

                    upload_result, status_code = FileManager.upload_file(new_image_file)
                    if status_code == 200:
                        product.image_file = upload_result["image_file"]
                    else:
                        return make_response(jsonify({"error": upload_result["message"]}), status_code)

                db.session.commit()
                return make_response(jsonify({"message": "Product updated successfully"}), 200)
            else:
                return make_response(jsonify({"message": "Product not found"}), 404)
        except SQLAlchemyError as e:
            return make_response(jsonify({"error": str(e)}), 500)
        except Exception as e:
            return make_response(jsonify({"error": str(e)}), 500)


# Admin Categories Resource
class AdminCategories(Resource):
    @login_required_admin
    def get(self):
        try:
            categories = Categories.query.all()
            categories_list = [category.to_dict() for category in categories]
            return make_response(jsonify(categories_list), 200)
        except SQLAlchemyError as e:
            return make_response(jsonify({"error": str(e)}), 500)
    
    @login_required_admin
    def post(self):
        try:
            data = request.form

            image_file = request.files.get('image_file')
            image_filename = 'default.jpg'
            
            if image_file:
                upload_result, status_code = FileManager.upload_file(image_file)
                if status_code == 200:
                    image_filename = upload_result["image_file"]
                else:
                    return make_response(jsonify({"error": upload_result["message"]}), status_code)
            
            if not data.get('name') or not data.get('description') or not data.get('slug'):
                return make_response(jsonify({"error": "All fields are required"}), 400)
            
            new_category = Categories(
                name=data.get('name'),
                description=data.get('description'),
                image_file=image_filename,
                slug=data.get('slug')
            )
            db.session.add(new_category)
            db.session.commit()
            
            return make_response(jsonify({"message": "Category created successfully"}), 201)
        except SQLAlchemyError as e:
            db.session.rollback()
            return make_response(jsonify({"error": str(e)}), 500)
    
    @login_required_admin
    def put(self, slug):
        try:
            data = request.form
            category = Categories.query.filter_by(slug=slug).first()
            if category:
                category.name = data.get('name')
                category.description = data.get('description')
                category.slug = data.get('slug')
                category.updated_at = datetime.utcnow()
                new_image_file = request.files.get('image_file')
                
                if new_image_file:
                    if category.image_file and category.image_file != 'default.jpg':
                        FileManager.delete_file(category.image_file)
                    upload_result, status_code = FileManager.upload_file(new_image_file)
                    if status_code == 200:
                        category.image_file = upload_result["image_file"]
                    else:
                        return make_response(jsonify({"error": upload_result["message"]}), status_code)
                else:
                    category.image_file = 'default.jpg'
                    
                db.session.commit()
                return make_response(jsonify({"message": "Category updated successfully"}), 200)
            else:
                return make_response(jsonify({"message": "Category not found"}), 404)
        except SQLAlchemyError as e:
            return make_response(jsonify({"error": str(e)}), 500)
    
    @login_required_admin
    def delete(self, slug):
        try:
            category = Categories.query.filter_by(slug=slug).first()
            if category:
                image_file = category.image_file
                if image_file and image_file != 'default.jpg':
                    delete_result, status_code = FileManager.delete_file(image_file)
                    if status_code != 200:
                        return make_response(jsonify({"error": delete_result["message"]}), status_code)
                    
                db.session.delete(category)
                db.session.commit()
                return make_response(jsonify({"message": "Category deleted successfully"}), 200)
            else:
                return make_response(jsonify({"message": "Category not found"}), 404)
        except SQLAlchemyError as e:
            return make_response(jsonify({"error": str(e)}), 500)

# Admin Users Resource
class AdminUsers(Resource):
    @login_required_admin
    def get(self):
        try:
            users = Users.query.all()
            users_list = [user.to_dict() for user in users]
            return make_response(jsonify(users_list), 200)
        except SQLAlchemyError as e:
            return make_response(jsonify({"error": str(e)}), 500)
    
    @login_required_admin
    def delete(self, id):
        try:
            user = Users.query.filter_by(id=id).first()
            if user:
                db.session.delete(user)
                db.session.commit()
                return make_response(jsonify({"message": "User deleted successfully"}), 200)
            else:
                return make_response(jsonify({"message": "User not found"}), 404)
        except SQLAlchemyError as e:
            return make_response(jsonify({"error": str(e)}), 500)

# Admin Orders Resource
class AdminOrders(Resource):
    @login_required_admin
    def get(self):
        try:
            orders = Orders.query.all()
            orders_list = [order.to_dict() for order in orders]
            return make_response(jsonify(orders_list), 200)
        except SQLAlchemyError as e:
            return make_response(jsonify({"error": str(e)}), 500)
    
    @login_required_admin
    def put(self, id):
        try:
            data = request.form
            order = Orders.query.filter_by(id=id).first()
            if order:
                order.order_status = data.get('order_status')
                order.payment_status = data.get('payment_status')
                order.shipping_status = data.get('shipping_status')
                db.session.commit()
                return make_response(jsonify({"message": "Order updated successfully"}), 200)
            else:
                return make_response(jsonify({"message": "Order not found"}), 404)
        except SQLAlchemyError as e:
            return make_response(jsonify({"error": str(e)}), 500)

# Admin Reviews Resource
class AdminReviews(Resource):
    @login_required_admin
    def get(self):
        try:
            reviews = Reviews.query.all()
            reviews_list = [review.to_dict() for review in reviews]
            return make_response(jsonify(reviews_list), 200)
        except SQLAlchemyError as e:
            return make_response(jsonify({"error": str(e)}), 500)

# Admin Dashboard Resource
class AdminDashboard(Resource):
    @login_required_admin
    def get(self):
        try:
            totalUsers = Users.query.count()
            totalOrders = Orders.query.count()
            totalProducts = Products.query.count()
            totalCategories = Categories.query.count()
            totalSales = db.session.query(func.sum(Sales.total_price)).scalar()
            totalRevenue = db.session.query(func.sum(Orders.total_amount)).scalar()
            
            dashboard_data = {
                "totalUsers": totalUsers,
                "totalOrders": totalOrders,
                "totalProducts": totalProducts,
                "totalCategories": totalCategories,
                "totalSales": totalSales,
                "totalRevenue": totalRevenue
            }
            return make_response(jsonify(dashboard_data), 200)
        except SQLAlchemyError as e:
            return make_response(jsonify({"error": str(e)}), 500)

class UserCategories(Resource):
    def get(self):
        try:
            categories = Categories.query.all()
            categories_list = [category.to_dict() for category in categories]
            return make_response(jsonify(categories_list), 200)
        except Exception as e:
            return make_response(jsonify({"error": str(e)}), 500)

class UserProducts(Resource):
    def get(self):
        try:
            products = Products.query.all()
            products_list = [product.to_dict() for product in products]
            return make_response(jsonify(products_list), 200)
        except Exception as e:
            return make_response(jsonify({"error": str(e)}), 500)
        
class UsersCart(Resource):
    def post(self,slug):
        userId = session.get("userId")
        product = Products.query.filter_by(slug=slug).first()
        if product:
            cart = Carts(user_id=userId, product_id=product.id, quantity=1,added_at=datetime.now())
            db.session.add(cart)
            db.session.commit()
            return make_response(jsonify({"message": "Product added to cart"}), 200)
        else:
            return make_response(jsonify({"error": "Product not found"}), 404)
        
    def get(self):
        user_id = session.get("userId")
        
        # Aggregate quantities and group by product_id
        cart_aggregates = db.session.query(
            Carts.product_id,
            func.sum(Carts.quantity).label('total_quantity')
        ).filter_by(user_id=user_id).group_by(Carts.product_id).all()
        
        result = []
        for aggregate in cart_aggregates:
            product = Products.query.filter_by(id=aggregate.product_id).first()
            if product:
                cart_dict = {
                    'productName': product.name,
                    'productPrice': product.price,
                    'productSlug': product.slug,
                    'quantity': aggregate.total_quantity,
                    'total_price': product.price * aggregate.total_quantity
                }
                result.append(cart_dict)

        return make_response(jsonify(result), 200)
    
    def delete(self,slug):
        user_id = session.get("userId")
        product = Products.query.filter_by(slug=slug).first()
        if product:
            carts = Carts.query.filter_by(user_id=user_id, product_id=product.id).all()
            if carts:

                for cart in carts:
                    db.session.delete(cart)
                    db.session.commit()
                return make_response(jsonify({"message": "Product removed from cart"}), 200)
            else:
                return make_response(jsonify({"error": "Product not found in cart"}), 404)
        else:
            return make_response(jsonify({"error": "Product not found"}), 404)
    

api.add_resource(AdminCategories, '/AdminPanel/Categories/OPS', '/AdminPanel/Categories/OPS/<string:slug>')
api.add_resource(AdminUsers, '/AdminPanel/Users/OPS', '/AdminPanel/Users/OPS/<int:id>')
api.add_resource(AdminDashboard, '/AdminPanel/Dashboard/Stats')
api.add_resource(AdminProducts, '/AdminPanel/Products/OPS', '/AdminPanel/Products/OPS/<string:slug>')
api.add_resource(UserCategories, '/HomePage/OPS/Categories')
api.add_resource(UserProducts, '/HomePage/OPS/Products') 
api.add_resource(FileManager, '/AdminPanel/Files', '/AdminPanel/Files/<string:filename>')  
api.add_resource(UsersCart, '/HomePage/Cart/OPS', '/HomePage/Cart/OPS/<string:slug>') 
      
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

        queries = Products.query.filter(Products.name.like(search + '%')).all()

        for query in queries:

            element = {

                "productName": query.name

            }
            results.append(element)

    return jsonify(results)

@app.route("/AdminPanel/Dashboard/Search")
@login_required_admin
def AdminsSearch():

    search = request.args.get("search")
    searchType = request.args.get("type")

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

    return jsonify(results)
           
# Route for user sign-up

@app.route("/SignUp", methods=["GET", "POST"])
def SignUp():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        email = request.form.get("email")
        phoneNumber = request.form.get("phoneNumber")

        try:
            # Check if username already exists
            if Users.query.filter_by(userName=username).first():
                flash("Username already exists", "error")
                return redirect("/SignUp")

            # Validate email format
            if not validate(email):
                flash("Invalid email format", "error")
                return redirect("/SignUp")

            # Check if email already exists
            if Users.query.filter_by(email=email).first():
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
            if Users.query.filter_by(phoneNumber=phoneNumber).first():
                flash("Phone number already exists", "error")
                return redirect("/SignUp")

            # Hash the password
            hashedPassword = generate_password_hash(password, method='pbkdf2:sha256')

            # Create a new user
            newUser = Users(
                userName=username,
                email=email,
                phoneNumber=phoneNumber,
                password=hashedPassword
            )
            db.session.add(newUser)
            db.session.commit()

            # Set session variables
            session["userId"] = newUser.id
            session["admin"] = False
            session["loggedIn"] = True

            flash("Signed up successfully", "success")
            return redirect("/HomePage")

        except SQLAlchemyError as e:
            db.session.rollback()
            flash("An error occurred during sign-up. Please try again.", "error")
            print(f"SQLAlchemyError: {str(e)}")
            return redirect("/SignUp")

        except Exception as e:
            flash("An unexpected error occurred. Please try again.", "error")
            print(f"Exception: {str(e)}")
            return redirect("/SignUp")

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

        return render_template("Login.html")


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
@login_required_admin
def Dashboard():

    return render_template("AdminDashboard.html")
    
    
@app.route("/AdminPanel/Products", methods=["GET", "POST"])
@login_required_admin

def ProductsRoute():

    return render_template("AdminProducts.html")

@app.route("/AdminPanel/Categories", methods=["GET", "POST"])
@login_required_admin

def AdminCategoriesRoute():

    return render_template("AdminCategories.html")

@app.route("/AdminPanel/Users", methods=["GET", "POST"])

@login_required_admin
def UsersRoute():
    
    return render_template("AdminUsers.html")


@app.route("/AdminPanel/Orders", methods=["GET", "POST"])
@login_required_admin

def OrdersRoute():
    
    return render_template("AdminOrders.html")



@app.route("/HomePage/Categories", methods=["GET", "POST"])
@login_required_user
def UsersCategoriesRoute():
    
    slug = request.args.get("slug")
    category = Categories.query.filter_by(slug=slug).first()
    
    if category is None :
        flash("Category not found", "error")
        return redirect("/HomePage")
    products = Products.query.filter_by(category_id=category.id).all()
    if not products:
        flash("Category not found", "error")
        return redirect("/HomePage")
    productsSerialized = [product.to_dict() for product in products]        
    return render_template("UsersCategory.html", category=category.to_dict() , products=productsSerialized)
    

@app.route("/HomePage/Products", methods=["GET", "POST"])
@login_required_user
def UsersProductsRoute():
    
    slug = request.args.get("slug")
    product = Products.query.filter_by(slug=slug).first()
    if product is None:
        
        flash("Product not found", "error")
        return redirect("/HomePage")
    
    return render_template("UsersProducts.html", product=product.to_dict())


@app.route("/HomePage/Cart", methods=["GET", "POST"])
@login_required_user
def UsersCartRoute():
    
    return render_template("UsersCart.html")
        




if __name__ == "__main__":
    with app.app_context():
        db.drop_all()
        db.create_all()
        admin = Admins.query.filter_by(userName="admin").first()
        if not admin:
            admin = Admins(
                userName="admin",
                password=generate_password_hash("admin", method='pbkdf2:sha256')
            )
            db.session.add(admin)
            db.session.commit()
    app.run()

