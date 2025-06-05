from flask import Blueprint, request, jsonify
from src.models import db, ProductMasterData as Product

product_api_bp = Blueprint("product_api", __name__, url_prefix="/api/products")

@product_api_bp.route("/", methods=["GET"])
def get_products():
    products = Product.query.all()
    return jsonify([p.to_dict() for p in products])

@product_api_bp.route("/", methods=["POST"])
def create_product():
    data = request.json
    try:
        new_product = Product(
            product_id=data["product_id"],
            product_name=data["product_name"],
            sku=data["sku"],
            unit_of_measure=data["unit_of_measure"],
            cost=float(data["cost"]),
            sale_price=float(data["sale_price"]),
            category=data["category"],
            location=data["location"],
            active=data.get("active", True),
        )
        db.session.add(new_product)
        db.session.commit()
        return jsonify({"message": "Producto creado correctamente."}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
