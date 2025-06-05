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
from datetime import datetime
from sqlalchemy.orm import relationship
from src.models import db

class InventoryMovementData(db.Model):
    """
    Registra todos los movimientos de entrada/salida/ajuste de inventario
    """
    _tablename_ = 'inventory_movement_data'

    # Campos principales
    movement_id = db.Column(db.String(10), primary_key=True)  # Ej: M001, M002
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    product_id = db.Column(
        db.String(10),
        db.ForeignKey('product_master_data.product_id', ondelete="CASCADE"),
        nullable=False
    )

    movement_type = db.Column(db.String(20), nullable=False)  # INBOUND, OUTBOUND, ADJUSTMENT
    quantity = db.Column(db.Integer, nullable=False)
    order_id = db.Column(db.String(20))  # PO-1001 (compra), SO-2001 (venta), ADJ-001 (ajuste)
    notes = db.Column(db.Text)  # Notas adicionales

    # Relación explícita con producto
    product = relationship("ProductMasterData", back_populates="movements")

    # Tipos de movimiento permitidos
    MOVEMENT_TYPES = {
        'INBOUND': 'Entrada de inventario',
        'OUTBOUND': 'Salida de inventario',
        'ADJUSTMENT_IN': 'Ajuste positivo',
        'ADJUSTMENT_OUT': 'Ajuste negativo'
    }

    def _repr_(self):
        return f'<Movement {self.movement_id}: {self.product_id} {self.movement_type} {self.quantity}>'

    def to_dict(self):
        return {
            'movement_id': self.movement_id,
            'date': self.date.isoformat(),
            'product_id': self.product_id,
            'movement_type': self.movement_type,
            'quantity': self.quantity,
            'order_id': self.order_id,
            'notes': self.notes,
            'product_name': self.product.product_name if self.product else None
        }