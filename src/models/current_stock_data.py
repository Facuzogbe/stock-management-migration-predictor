from flask import Blueprint, request, jsonify
from src.models import db, ProductMasterData as Product

product_api_bp = Blueprint("product_api", _name_, url_prefix="/api/products")


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
from datetime import datetime
from src.models import db
from sqlalchemy.orm import relationship

class CurrentStockData(db.Model):
    """
    Representa el stock actual de cada producto (vista materializada)
    """
    _tablename_ = 'current_stock_data'

    # Clave primaria y foránea
    product_id = db.Column(db.String(10), db.ForeignKey('product_master_data.product_id', ondelete="CASCADE"), primary_key=True)

    # Campos de stock
    quantity = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    total_inventory_cost = db.Column(db.Float, default=0.0)

    # Relación explícita
    product = relationship("ProductMasterData", back_populates="current_stock")

    def _repr_(self):
        return f'<Stock {self.product_id}: {self.quantity} units>'

    def to_dict(self):
        return {
            'product_id': self.product_id,
            'product_name': self.product.product_name if self.product else None,
            'quantity': self.quantity,
            'last_updated': self.last_updated.isoformat(),
            'total_inventory_cost': self.total_inventory_cost,
            'unit_cost': self.product.cost if self.product else None
        }

    def update_from_movement(self, movement):
        """Actualiza el stock basado en un movimiento"""
        if movement.movement_type in ['INBOUND', 'ADJUSTMENT_IN']:
            self.quantity += movement.quantity
        else:
            self.quantity -= movement.quantity
        
        if self.product:
            self.total_inventory_cost = self.quantity * self.product.cost
        
        self.last_updated = datetime.utcnow()