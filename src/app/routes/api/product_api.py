from flask import Blueprint, request, jsonify
from src.models import db, ProductMasterData as Product

product_api_bp = Blueprint("product_api", __name__, url_prefix="/api/products")


# GET - Obtener todos los productos
@product_api_bp.route("/", methods=["GET"])
def get_products():
    products = Product.query.all()
    return jsonify([p.to_dict() for p in products]), 200


# POST - Crear un nuevo producto
@product_api_bp.route("/", methods=["POST"])
def create_product():
    data = request.get_json()
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
        return jsonify({"message": "Producto creado correctamente.", "product": new_product.to_dict()}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# PUT - Actualizar un producto existente
@product_api_bp.route("/<product_id>", methods=["PUT"])
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json()

    try:
        product.product_name = data.get("product_name", product.product_name)
        product.sku = data.get("sku", product.sku)
        product.unit_of_measure = data.get("unit_of_measure", product.unit_of_measure)
        product.cost = float(data.get("cost", product.cost))
        product.sale_price = float(data.get("sale_price", product.sale_price))
        product.category = data.get("category", product.category)
        product.location = data.get("location", product.location)
        product.active = bool(data.get("active", product.active))

        db.session.commit()
        return jsonify({"message": "Producto actualizado correctamente.", "product": product.to_dict()}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# DELETE - Eliminar un producto
@product_api_bp.route("/<product_id>", methods=["DELETE"])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)

    try:
        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": f"Producto {product_id} eliminado correctamente."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400