# services/movimiento_service.py

from datetime import datetime
from models import db
from models.stock_model import Product  # Modelo correcto
from models.movimiento_model import Movimiento

# Registrar movimiento: entrada o salida
def registrar_movimiento(producto_id, tipo, cantidad):
    producto = Product.query.get(producto_id)

    if not producto:
        raise ValueError("Producto no encontrado.")

    if tipo == "salida":
        if producto.stock < cantidad:
            raise ValueError("Stock insuficiente para realizar la salida.")
        producto.stock -= cantidad

    elif tipo == "entrada":
        producto.stock += cantidad

    else:
        raise ValueError("Tipo de movimiento no válido. Use 'entrada' o 'salida'.")

    movimiento = Movimiento(
        producto_id=producto_id,
        tipo=tipo,
        cantidad=cantidad,
        fecha=datetime.now()
    )

    db.session.add(movimiento)
    db.session.commit()
    return movimiento

# Obtener todos los movimientos (historial)
def obtener_movimientos():
    return Movimiento.query.order_by(Movimiento.fecha.desc()).all()
