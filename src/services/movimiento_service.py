# src/services/movimiento_service.py

from datetime import datetime
from sqlalchemy import func
from src.extensions import db
from src.models.product_master_data import ProductMasterData as Product
from src.models.inventory_movement_data import InventoryMovementData as Movimiento
from src.models.current_stock_data import CurrentStockData

# Definimos los tipos de movimiento válidos según la consigna
VALID_MOVEMENT_TYPES = {
    'INBOUND': 'Entrada de inventario',
    'OUTBOUND': 'Salida de inventario',
    'ADJUSTMENT_IN': 'Ajuste positivo',
    'ADJUSTMENT_OUT': 'Ajuste negativo'
}

def registrar_movimiento(product_id, movement_type, quantity, order_id=None, notes=None):
    """
    Registra un movimiento de inventario con validación completa y actualización de stock
    
    Args:
        product_id (str): ID del producto (ej: P001)
        movement_type (str): Tipo de movimiento (debe estar en VALID_MOVEMENT_TYPES)
        quantity (int): Cantidad de unidades (debe ser positivo)
        order_id (str, optional): ID de orden relacionada
        notes (str, optional): Notas adicionales
        
    Returns:
        Movimiento: El movimiento registrado
        
    Raises:
        ValueError: Con mensajes descriptivos para cada tipo de error
    """
    # Validación del tipo de movimiento
    if movement_type not in VALID_MOVEMENT_TYPES:
        valid_types = ", ".join(VALID_MOVEMENT_TYPES.keys())
        raise ValueError(f"Tipo de movimiento inválido. Use uno de: {valid_types}")

    # Validación de cantidad positiva
    if not isinstance(quantity, int) or quantity <= 0:
        raise ValueError("La cantidad debe ser un número entero positivo")

    # Verificar producto existente
    producto = Product.query.get(product_id)
    if not producto:
        raise ValueError(f"Producto con ID {product_id} no encontrado")

    # Generar ID automático para el movimiento
    last_movement = Movimiento.query.order_by(Movimiento.movement_id.desc()).first()
    new_id = f"M{(int(last_movement.movement_id[1:]) + 1):03d}" if last_movement else "M001"

    # Validación especial para movimientos de salida
    if movement_type in ['OUTBOUND', 'ADJUSTMENT_OUT']:
        stock_actual = CurrentStockData.query.get(product_id)
        if not stock_actual or stock_actual.quantity < quantity:
            raise ValueError(
                f"Stock insuficiente. Disponible: {stock_actual.quantity if stock_actual else 0}, "
                f"Se requieren: {quantity}"
            )

    # Crear el movimiento
    movimiento = Movimiento(
        movement_id=new_id,
        product_id=product_id,
        movement_type=movement_type,
        quantity=quantity,
        order_id=order_id,
        notes=notes,
        date=datetime.utcnow()
    )

    # Actualizar el stock (versión mejorada)
    actualizar_stock_directo(product_id, movement_type, quantity, producto.cost)

    db.session.add(movimiento)
    db.session.commit()
    
    return movimiento

def actualizar_stock_directo(product_id, movement_type, quantity, unit_cost):
    """
    Función interna para actualizar el stock directamente
    """
    stock = CurrentStockData.query.get(product_id)
    
    if not stock:
        stock = CurrentStockData(
            product_id=product_id,
            quantity=0,
            total_inventory_cost=0
        )
        db.session.add(stock)
    
    if movement_type in ['INBOUND', 'ADJUSTMENT_IN']:
        stock.quantity += quantity
    else:
        stock.quantity -= quantity
    
    stock.total_inventory_cost = stock.quantity * unit_cost
    stock.last_updated = datetime.utcnow()

def obtener_tipos_movimiento():
    """Devuelve los tipos de movimiento válidos con sus descripciones"""
    return VALID_MOVEMENT_TYPES

def obtener_movimientos():
    """Obtiene todos los movimientos ordenados por fecha descendente"""
    return (db.session.query(Movimiento)
            .order_by(Movimiento.date.desc())
            .all()) 