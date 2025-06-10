from datetime import datetime
from src.models import db
from sqlalchemy.orm import relationship

class CurrentStockData(db.Model):
    __tablename__ = 'current_stock_data'

    product_id = db.Column(db.String(10), db.ForeignKey('product_master_data.product_id', ondelete="CASCADE"), primary_key=True)
    quantity = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    total_inventory_cost = db.Column(db.Float, default=0.0)

    product = relationship("ProductMasterData", back_populates="current_stock")

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
        if movement.movement_type in ['INBOUND', 'ADJUSTMENT_IN']:
            self.quantity += movement.quantity
        else:
            self.quantity -= movement.quantity

        if self.product:
            self.total_inventory_cost = self.quantity * self.product.cost

        self.last_updated = datetime.utcnow()
