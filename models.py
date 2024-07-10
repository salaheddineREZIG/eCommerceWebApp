from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userName = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    phoneNumber = db.Column(db.String(20), nullable=False)
    profilePicture = db.Column(db.String(100), nullable=False, default='default.jpg')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    carts = db.relationship('Carts', backref='user', lazy=True)
    orders = db.relationship('Orders', backref='user', lazy=True)
    reviews = db.relationship('Reviews', backref='user', lazy=True)
    wishlists = db.relationship('Wishlists', backref='user', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'userName': self.userName,
            'email': self.email,
            'phoneNumber': self.phoneNumber,
            'profilePicture': self.profilePicture,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'orders': [order.to_dict() for order in self.orders],
            'reviews': [review.to_dict() for review in self.reviews],
            'wishlists': [wishlist.to_dict() for wishlist in self.wishlists],
            'carts': [cart.to_dict() for cart in self.carts]
        }


class Admins(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userName = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    profilePicture = db.Column(db.String(100), nullable=False, default='default.png')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'userName': self.userName,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }



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
    slug= db.Column(db.String(100), nullable=False, unique=True)
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
    discount_price = db.Column(db.Float, nullable=True, default=0)
    availability_status = db.Column(db.String(20), nullable=False, default='In Stock')
    rating = db.Column(db.Float, nullable=True)
    reviews = db.relationship('Reviews', backref='product', lazy=True)
    attributes = db.relationship('ProductAttributes', backref='product', lazy=True)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_modified = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    carts = db.relationship('Carts', backref='product', lazy=True)


    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'slug': self.slug,
            'price': self.price,
            'category_id': self.category_id,
            'category_name': self.category.name,
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
            'attributes': [attribute.to_dict() for attribute in self.attributes],
            'carts': [cart.to_dict() for cart in self.carts],
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
            'updated_at': self.updated_at
        }


class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default='Pending')
    total_amount = db.Column(db.Float, nullable=False)
    shipping_address = db.Column(db.String(200), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    tracking_number = db.Column(db.String(50), nullable=True)
    order_items = db.relationship('Sales', backref='order', lazy=True)
    shipping_details = db.relationship('ShippingDetails', backref='order', lazy=True, uselist=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'order_date': self.order_date,
            'status': self.status,
            'total_amount': self.total_amount,
            'shipping_address': self.shipping_address,
            'payment_method': self.payment_method,
            'tracking_number': self.tracking_number,
            'order_items': [item.to_dict() for item in self.order_items],
            'shipping_details': self.shipping_details.to_dict() if self.shipping_details else None
        }


class Sales(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, nullable=True)
    total_price = db.Column(db.Float, nullable=False)
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


class ProductAttributes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    attribute_name = db.Column(db.String(50), nullable=False)
    attribute_value = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'attribute_name': self.attribute_name,
            'attribute_value': self.attribute_value
        }



class Wishlists(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    added_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'added_at': self.added_at
        }



class ShippingDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    carrier = db.Column(db.String(50), nullable=False)
    tracking_number = db.Column(db.String(50), nullable=True)
    shipped_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expected_delivery_date = db.Column(db.DateTime, nullable=False)
    delivery_status = db.Column(db.String(20), nullable=False, default='Shipped')

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'carrier': self.carrier,
            'tracking_number': self.tracking_number,
            'shipped_date': self.shipped_date,
            'expected_delivery_date': self.expected_delivery_date,
            'delivery_status': self.delivery_status
        }


class Carts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    added_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'added_at': self.added_at
        }
