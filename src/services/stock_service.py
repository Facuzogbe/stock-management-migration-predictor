import datetime 
from src.extensions import db
from src.models import CurrentStockData, ProductMasterData

def obtener_stock_actual():
    """Obtiene todo el stock actual con información de productos"""
    return db.session.query(CurrentStockData)\
        .join(ProductMasterData)\
        .order_by(ProductMasterData.product_name)\
        .all()

def update_stock(product_id, movement_type, quantity):
    """Actualiza el stock después de un movimiento"""
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
    
    stock.last_updated = datetime.datetime.utcnow()
    db.session.commit()
