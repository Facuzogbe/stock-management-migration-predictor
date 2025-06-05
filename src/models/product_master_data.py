from datetime import datetime
from src.models import db

class ProductMasterData(db.Model):
    """
    Tabla maestra de productos - Almacena información base de todos los productos
    """
    __tablename__ = 'product_master_data'
    __table_args__ = {'extend_existing': True}  # Previene el error de tabla duplicada


    # Campos principales
    product_id = db.Column(db.String(10), primary_key=True)  # Ej: P001, P002
    product_name = db.Column(db.String(100), nullable=False)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    unit_of_measure = db.Column(db.String(20), default='Unit')  # Unit, Kg, Liter, etc.
    cost = db.Column(db.Float, nullable=False)  # Costo unitario
    sale_price = db.Column(db.Float, nullable=False)  # Precio de venta
    category = db.Column(db.String(50))  # Electronics, Peripherals, etc.
    location = db.Column(db.String(20))  # Ubicación en almacén (A1-01, B2-05)
    active = db.Column(db.Boolean, default=True)  # Producto activo/inactivo

    # Relaciones (se crearán automáticamente con los backref de otros modelos)
    # movements = relación con InventoryMovementData
    # current_stock = relación con CurrentStockData
    # predictions = relación con PredictorStockData

    def __repr__(self):
        return f'<Product {self.product_id}: {self.product_name}>'

    def to_dict(self):
        """Convierte el objeto a diccionario para APIs"""
        return {
            'product_id': self.product_id,
            'product_name': self.product_name,
            'sku': self.sku,
            'unit_of_measure': self.unit_of_measure,
            'cost': self.cost,
            'sale_price': self.sale_price,
            'category': self.category,
            'location': self.location,
            'active': self.active
        }