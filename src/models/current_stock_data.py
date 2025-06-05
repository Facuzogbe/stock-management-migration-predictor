from datetime import datetime
from src.models import db

class CurrentStockData(db.Model):
    """
    Representa el stock actual de cada producto (vista materializada)
    """
    __tablename__ = 'current_stock_data'

    # Clave primaria y foránea
    product_id = db.Column(db.String(10), db.ForeignKey('product_master_data.product_id'), primary_key=True)

    # Campos de stock
    quantity = db.Column(db.Integer, default=0)  # Cantidad actual en stock
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    total_inventory_cost = db.Column(db.Float, default=0.0)  # Costo total = cantidad * costo unitario

    # Relación con Producto
    product = db.relationship('ProductMasterData', backref='current_stock')

    def __repr__(self):
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