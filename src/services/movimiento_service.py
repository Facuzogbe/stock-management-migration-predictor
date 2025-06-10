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
    try:
        # Validación del tipo de movimiento
        if movement_type not in VALID_MOVEMENT_TYPES:
            valid_types = ", ".join(VALID_MOVEMENT_TYPES.keys())
            raise ValueError(f"Tipo de movimiento inválido. Use uno de: {valid_types}")

        # Validación de cantidad positiva
        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError("La cantidad debe ser un número entero positivo")
        except (ValueError, TypeError):
            raise ValueError("La cantidad debe ser un número válido")

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

        # Crear el movimiento con conversión explícita de tipos
        now = datetime.utcnow()
        movimiento = Movimiento(
            movement_id=str(new_id),
            product_id=str(product_id),
            movement_type=str(movement_type),
            quantity=int(quantity),
            order_id=str(order_id) if order_id else None,
            notes=str(notes) if notes else None,
            date=now,
            movement_date=now
        )

        # Iniciar transacción
        db.session.begin_nested()
        
        try:
            # Actualizar el stock
            stock = CurrentStockData.query.get(product_id)
            
            if not stock:
                stock = CurrentStockData(
                    product_id=str(product_id),
                    quantity=0,
                    total_inventory_cost=0.0
                )
                db.session.add(stock)
            
            # Calcular nuevo stock con validación
            if movement_type in ['INBOUND', 'ADJUSTMENT_IN']:
                stock.quantity += quantity
            else:
                new_quantity = stock.quantity - quantity
                if new_quantity < 0:
                    raise ValueError("No hay suficiente stock disponible")
                stock.quantity = new_quantity
            
            # Actualizar costos
            stock.total_inventory_cost = float(stock.quantity) * float(producto.cost)
            stock.last_updated = now
            
            # Registrar movimiento y confirmar transacción
            db.session.add(movimiento)
            db.session.commit()
            
            return movimiento

        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Error en transacción: {str(e)}")

    except ValueError as e:
        db.session.rollback()
        raise ValueError(str(e))
    except Exception as e:
        db.session.rollback()
        raise ValueError(f"Error inesperado: {str(e)}")

def actualizar_stock_directo(product_id, movement_type, quantity, unit_cost):
    """
    Función mejorada para actualizar el stock directamente
    """
    try:
        # Convertir tipos de entrada
        product_id = str(product_id)
        quantity = int(quantity)
        unit_cost = float(unit_cost)

        # Iniciar transacción
        db.session.begin_nested()
        
        stock = CurrentStockData.query.get(product_id)
        
        if not stock:
            stock = CurrentStockData(
                product_id=product_id,
                quantity=0,
                total_inventory_cost=0.0
            )
            db.session.add(stock)
        
        # Calcular nuevo stock con validación
        if movement_type in ['INBOUND', 'ADJUSTMENT_IN']:
            stock.quantity += quantity
        else:
            new_quantity = stock.quantity - quantity
            if new_quantity < 0:
                raise ValueError("No hay suficiente stock disponible")
            stock.quantity = new_quantity
        
        # Actualizar valores con conversión explícita
        stock.total_inventory_cost = float(stock.quantity) * unit_cost
        stock.last_updated = datetime.utcnow()
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        raise ValueError(f"Error en actualización de stock: {str(e)}")

def obtener_tipos_movimiento():
    """Devuelve los tipos de movimiento válidos con sus descripciones"""
    return VALID_MOVEMENT_TYPES

def obtener_movimientos():
    """Obtiene todos los movimientos ordenados por fecha descendente"""
    return (db.session.query(Movimiento)
            .order_by(Movimiento.date.desc())
            .all())