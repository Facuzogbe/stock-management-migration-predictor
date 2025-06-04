from flask import Blueprint, render_template, request, redirect, url_for
from src.models import db, ProductMasterData as Product
from app.utils.auth_decorators import role_required


product_bp = Blueprint("product", _name_, template_folder="../templates")

@product_bp.route("/")
@role_required(["admin", "empleado"])

def list_products():
    products = Product.query.all()
    return render_template("products/list.html", products=products)

@product_bp.route("/new", methods=["GET", "POST"])
@role_required(["admin", "empleado"])

def new_product():
    if request.method == "POST":
        data = request.form
        new_product = Product(
            product_id=data["product_id"],
            product_name=data["product_name"],
            sku=data["sku"],
            unit_of_measure=data["unit_of_measure"],
            cost=float(data["cost"]),
            sale_price=float(data["sale_price"]),
            category=data["category"],
            location=data["location"],
            active=bool(data.get("active", True)),
            # active='active' in data,
        )
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for("product.list_products"))

    return render_template("products/new.html")

@product_bp.route("/edit/<product_id>", methods=["GET", "POST"])
@role_required(["admin", "empleado"])

def edit_product(product_id):
    product = Product.query.get_or_404(product_id)

    if request.method == "POST":
        data = request.form
        product.product_name = data["product_name"]
        product.sku = data["sku"]
        product.unit_of_measure = data["unit_of_measure"]
        product.cost = float(data["cost"])
        product.sale_price = float(data["sale_price"])
        product.category = data["category"]
        product.location = data["location"]
        product.active = bool(data.get("active", True))
        # product.active = 'active' in data

        db.session.commit()
        return redirect(url_for("product.list_products"))

    return render_template("products/edit.html", product=product)

@product_bp.route("/delete/<product_id>", methods=["POST"])
@role_required(["admin", "empleado"])

def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for("product.list_products"))