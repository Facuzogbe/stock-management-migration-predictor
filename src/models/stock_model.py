from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Product(db.Model):
    __tablename__ = 'products'

    product_id = db.Column(db.String(10), primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    sku = db.Column(db.String(50), nullable=False)
    unit_of_measure = db.Column(db.String(20), nullable=False)
    cost = db.Column(db.Float, nullable=False)
    sale_price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(20), nullable=False)
    active = db.Column(db.Boolean, default=True)
