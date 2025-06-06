import os
import sys
import uuid
from datetime import datetime, timedelta
import random
from flask import Flask

# Configura el path correctamente
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from src.extensions import db
from src.models.inventory_movement_data import InventoryMovementData
from src.models.product_master_data import ProductMasterData

def create_app():
    app = Flask(__name__, static_folder="static", instance_relative_config=True)

    # Aquí debería cargarse configuración real si tenés config.py o similar
    # app.config.from_object('config.DevConfig')  <-- ejemplo

    from src.app import create_app as real_app
    return real_app()

def load_sample_data():
    print("Cargando movimientos de prueba...")
    
    # 1. Reiniciar la base de datos (solo en desarrollo)
    with app.app_context():
        db.drop_all()
        db.create_all()
    
    # 2. Crear producto demo
    if not db.session.get(ProductMasterData, "PROD-001"):
        producto = ProductMasterData(
            product_id="PROD-001",
            product_name="Producto Demo",
            sku="DEMO-001",
            category="TEST",
            cost=0.0,
            sale_price=0.0,
            unit_of_measure="Unit",
            active=True
        )
        db.session.add(producto)
        db.session.commit()

    # 3. Crear movimientos (sin especificar movement_id)
    fecha_inicio = datetime.now() - timedelta(weeks=104)
    movimientos = [{
        'date': datetime.utcnow(),
        'product_id': "PROD-001",
        'movement_type': 'INBOUND',
        'quantity': random.randint(10, 100),
        'order_id': f"PO-{1000+i}",
        'notes': "Datos de prueba",
        'movement_date': fecha_inicio + timedelta(weeks=i)
    } for i in range(104)]

    try:
        db.session.bulk_insert_mappings(InventoryMovementData, movimientos)
        db.session.commit()
        print(f"✅ Se cargaron {len(movimientos)} movimientos.")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error: {str(e)}")
        
if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        # ⚠️ Solo descomentá estas líneas si querés borrar y recrear TODAS las tablas
        # db.drop_all()
        # db.create_all()

        load_sample_data()
