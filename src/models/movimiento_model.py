from models import db
from datetime import datetime

class Movimiento(db.Model):
    __tablename__ = 'movimientos'

    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.String(10), db.ForeignKey('products.product_id'), nullable=False)
    tipo = db.Column(db.String(10), nullable=False)  # 'entrada' o 'salida'
    cantidad = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    producto = db.relationship('Product', backref=db.backref('movimientos', lazy=True))

    def __repr__(self):
        return f"<Movimiento {self.tipo} {self.cantidad} producto {self.producto_id}>"