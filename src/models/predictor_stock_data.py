from datetime import date
from sqlalchemy.orm import relationship
from src.models import db

class PredictorStockData(db.Model):
    """
    Datos históricos para entrenar el modelo predictivo de stock
    """
    __tablename__ = 'predictor_stock_data'

    # Campos principales
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)  # Fecha del registro histórico

    product_id = db.Column(
        db.String(10),
        db.ForeignKey('product_master_data.product_id', ondelete="CASCADE"),
        nullable=False
    )

    units_sold = db.Column(db.Integer, nullable=False)  # Unidades vendidas ese día
    avg_sale_price = db.Column(db.Float)  # Precio promedio de venta
    promotion_active = db.Column(db.Boolean, default=False)  # ¿Hubo promoción?
    special_event = db.Column(db.String(100))  # Evento especial (ej: "New Year's Day")

    # Relación explícita con Producto
    product = relationship("ProductMasterData", back_populates="predictions")

    def __repr__(self):
        return f'<Prediction Data {self.date}: {self.product_id} - Sold {self.units_sold}>'

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'product_id': self.product_id,
            'product_name': self.product.product_name if self.product else None,
            'units_sold': self.units_sold,
            'avg_sale_price': self.avg_sale_price,
            'promotion_active': self.promotion_active,
            'special_event': self.special_event
        }