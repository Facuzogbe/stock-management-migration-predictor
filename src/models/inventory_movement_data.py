from datetime import datetime
from sqlalchemy.orm import relationship
from src.models import db

class InventoryMovementData(db.Model):
    """
    Registra todos los movimientos de entrada/salida/ajuste de inventario
    """
    __tablename__ = 'inventory_movement_data'
    movement_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
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
    movement_date = db.Column(db.DateTime)  # <-- ESTA ES LA QUE TE FALTA USAR


    # Relación explícita con producto
    product = relationship("ProductMasterData", back_populates="movements")

    # Tipos de movimiento permitidos
    MOVEMENT_TYPES = {
        'INBOUND': 'Entrada de inventario',
        'OUTBOUND': 'Salida de inventario',
        'ADJUSTMENT_IN': 'Ajuste positivo',
        'ADJUSTMENT_OUT': 'Ajuste negativo'
    }

    def __repr__(self):
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