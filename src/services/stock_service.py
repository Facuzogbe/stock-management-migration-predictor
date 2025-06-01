# src/services/stock_service.py
from datetime import datetime
from src.extensions import db
from src.models.current_stock_data import CurrentStockData
from src.models.product_master_data import ProductMasterData

def actualizar_stock(product_id, movement_type, quantity):
    """
    Actualiza el stock después de un movimiento
    Args:
        product_id (str): ID del producto
        movement_type (str): Tipo de movimiento
        quantity (int): Cantidad a ajustar
    """
    stock = CurrentStockData.query.get(product_id)
    producto = ProductMasterData.query.get(product_id)
    
    if not stock:
        stock = CurrentStockData(product_id=product_id, quantity=0)
        db.session.add(stock)
    
    if movement_type in ['INBOUND', 'ADJUSTMENT_IN']:
        stock.quantity += quantity
    else:
        stock.quantity -= quantity
    
    if producto:
        stock.total_inventory_cost = stock.quantity * producto.cost
    
    stock.last_updated = datetime.utcnow()
    db.session.commit()