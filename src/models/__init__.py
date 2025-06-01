from src.extensions import db

# Importa todos los modelos aquí
from .product_master_data import ProductMasterData
from .inventory_movement_data import InventoryMovementData
from .current_stock_data import CurrentStockData
from .predictor_stock_data import PredictorStockData

__all__ = ['db', 'ProductMasterData', 'InventoryMovementData', 'CurrentStockData', 'PredictorStockData']