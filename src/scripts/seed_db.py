import os
import sys
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
    from src.app import create_app as real_app
    return real_app()

def load_sample_data():
    print("Cargando datos de productos reales...")
    
    # 1. Reiniciar la base de datos (solo en desarrollo)
    with app.app_context():
        db.drop_all()
        db.create_all()
    
    # 2. Crear productos reales (modificado con tus datos JSON)
    real_products = [
        {
            'product_id': "P001",
            'product_name': "Dell XPS 13 Laptop",
            'sku': "DELL-XPS13",
            'category': "Electronics",
            'unit_of_measure': "Unit",
            'cost': 1200.0,
            'sale_price': 1600.0,
            'location': "A1-01",
            'active': True
        },
        {
            'product_id': "P002",
            'product_name': "LG UltraWide Monitor",
            'sku': "LG-UW34",
            'category': "Electronics",
            'unit_of_measure': "Unit",
            'cost': 350.0,
            'sale_price': 450.0,
            'location': "A1-02",
            'active': True
        },
        {
            'product_id': "P003",
            'product_name': "RGB Mechanical Keyboard",
            'sku': "KM-RGB01",
            'category': "Peripherals",
            'unit_of_measure': "Unit",
            'cost': 80.0,
            'sale_price': 120.0,
            'location': "B2-05",
            'active': True
        },
        {
            'product_id': "P004",
            'product_name': "Logitech Gaming Mouse",
            'sku': "LOGI-G502",
            'category': "Peripherals",
            'unit_of_measure': "Unit",
            'cost': 50.0,
            'sale_price': 75.0,
            'location': "B2-06",
            'active': True
        },
        {
            'product_id': "P005",
            'product_name': "HDMI Cable 2m",
            'sku': "HDMI-2M",
            'category': "Accessories",
            'unit_of_measure': "Unit",
            'cost': 5.0,
            'sale_price': 10.0,
            'location': "C3-10",
            'active': True
        }
    ]
    
    try:
        # Insertar productos
        for product_data in real_products:
            if not db.session.get(ProductMasterData, product_data['product_id']):
                producto = ProductMasterData(**product_data)
                db.session.add(producto)
        db.session.commit()
        print(f"✅ Se cargaron {len(real_products)} productos reales.")
        
        # 3. Crear movimientos de inventario para estos productos
        fecha_inicio = datetime.now() - timedelta(weeks=104)
        movimientos = []
        
        for i in range(104):
            # Seleccionar producto aleatorio de los reales
            product = random.choice(real_products)
            product_id = product['product_id']
            
            # Generar fecha progresiva
            movement_date = fecha_inicio + timedelta(weeks=i)
            
            # Determinar tipo de movimiento
            movement_type = random.choice(['INBOUND', 'OUTBOUND', 'ADJUSTMENT_IN', 'ADJUSTMENT_OUT'])
            
            # Cantidad basada en el tipo de producto
            base_qty = 1 if product['category'] == "Electronics" else (5 if product['category'] == "Peripherals" else 10)
            quantity = random.randint(base_qty, base_qty * 3)
            
            movimientos.append({
                'date': movement_date,
                'product_id': product_id,
                'movement_type': movement_type,
                'quantity': quantity,
                'order_id': f"{'PO' if movement_type == 'INBOUND' else 'SO'}-{1000+i}",
                'notes': f"Movimiento para {product['product_name']}",
                'movement_date': movement_date
            })

        db.session.bulk_insert_mappings(InventoryMovementData, movimientos)
        db.session.commit()
        print(f"✅ Se cargaron {len(movimientos)} movimientos con movement_date.")
        
        # Verificación
        print("\nEjemplo de productos cargados:")
        for prod in ProductMasterData.query.limit(3).all():
            print(f"ID: {prod.product_id} | Nombre: {prod.product_name} | Precio: {prod.sale_price}")
            
        print("\nEjemplo de movimientos cargados:")
        for mov in InventoryMovementData.query.limit(3).all():
            print(f"ID: {mov.movement_id} | Producto: {mov.product_id} | Tipo: {mov.movement_type} | Cantidad: {mov.quantity}")
            
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error: {str(e)}")
        raise e

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        load_sample_data()