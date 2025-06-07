import os
import sys
from datetime import datetime, timedelta
import random
from flask import Flask

# Configuración
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from src.extensions import db
from src.models import InventoryMovementData, ProductMasterData, CurrentStockData, PredictorStockData

def create_app():
    app = Flask(__name__, static_folder="static", instance_relative_config=True)
    from src.app import create_app as real_app
    return real_app()

def generar_historico_controlado():
    print("Generando histórico controlado (04/04/2025 - 04/06/2025)...")
    
    with app.app_context():
        # 1. Limpiar y preparar BD (opcional)
        # db.drop_all()
        # db.create_all()
        
        # 2. Crear producto de prueba si no existe (usando SQLAlchemy 2.0 style)
        producto = db.session.get(ProductMasterData, "P001")
        if not producto:
            producto = ProductMasterData(
                product_id="P001",
                product_name="Laptop Business Pro",
                sku="LT-BP-2023",
                category="Electronics",
                cost=1350.0,
                sale_price=1899.0,
                unit_of_measure="Unit",
                active=True
            )
            db.session.add(producto)
            db.session.commit()
        
        # 3. Verificar/crear registro de stock actual
        stock = db.session.get(CurrentStockData, "P001")
        if not stock:
            stock = CurrentStockData(
                product_id="P001",
                quantity=40,
                total_inventory_cost=40 * producto.cost
            )
            db.session.add(stock)
            db.session.commit()
        
        # 4. Configuración de período exacto
        fecha_inicio = datetime(2025, 4, 4)
        fecha_fin = datetime(2025, 6, 4)
        dias_totales = (fecha_fin - fecha_inicio).days
        stock_actual = stock.quantity
        
        # 5. Generación de 1 movimiento por día
        for dia in range(dias_totales + 1):
            fecha_movimiento = fecha_inicio + timedelta(days=dia)
            
            # Hora comercial aleatoria
            fecha_movimiento = fecha_movimiento.replace(
                hour=random.randint(8, 18),
                minute=random.randint(0, 59),
                second=random.randint(0, 59)
            )
            
            # Determinar tipo de movimiento (50% entrada, 50% salida)
            if random.random() < 0.5 or stock_actual < 10:
                movimiento_tipo = 'INBOUND'
                cantidad = random.randint(5, 20)
                stock_actual += cantidad
                notas = f"Compra a proveedor - {cantidad} unidades"
            else:
                movimiento_tipo = 'OUTBOUND'
                max_posible = min(8, stock_actual)  # Limitar ventas a 8 unidades máximo
                cantidad = random.randint(1, max_posible)
                stock_actual -= cantidad
                notas = f"Venta a cliente - {cantidad} unidades"
            
            # Registrar movimiento
            try:
                # Crear movimiento de inventario
                movimiento = InventoryMovementData(
                    movement_id=f"MOV-{fecha_movimiento.strftime('%Y%m%d%H%M%S')}",
                    product_id="P001",
                    movement_type=movimiento_tipo,
                    quantity=cantidad,
                    order_id=f"{movimiento_tipo[:2]}-{fecha_movimiento.strftime('%Y%m%d%H%M')}",
                    notes=notas,
                    date=fecha_movimiento,
                    movement_date=fecha_movimiento
                )
                db.session.add(movimiento)
                
                # Actualizar stock
                stock.quantity = stock_actual
                stock.total_inventory_cost = stock.quantity * producto.cost
                stock.last_updated = datetime.utcnow()
                
                # Crear registro para predictor solo si es OUTBOUND
                if movimiento_tipo == 'OUTBOUND':
                    predictor_data = PredictorStockData(
                        date=fecha_movimiento.date(),
                        product_id="P001",
                        units_sold=cantidad,
                        avg_sale_price=producto.sale_price * (0.95 if random.random() < 0.3 else 1.0),
                        promotion_active=random.random() < 0.2,
                        special_event="None"
                    )
                    db.session.add(predictor_data)
                
                db.session.commit()
                print(f"✅ Día {dia+1}/{dias_totales+1}: {fecha_movimiento.date()} - {movimiento_tipo} {cantidad} unidades")
                
            except Exception as e:
                db.session.rollback()
                print(f"❌ Error en día {dia+1}: {str(e)}")
                continue
        
        # 6. Resultados finales
        print("\nResumen final:")
        print(f"Período: {fecha_inicio.date()} al {fecha_fin.date()}")
        print(f"Total de días: {dias_totales + 1}")
        print(f"Stock final: {stock_actual} unidades")
        
        # Estadísticas
        total_inbound = db.session.query(db.func.sum(InventoryMovementData.quantity))\
            .filter_by(movement_type='INBOUND')\
            .filter(InventoryMovementData.date >= fecha_inicio)\
            .filter(InventoryMovementData.date <= fecha_fin)\
            .scalar() or 0
        
        total_outbound = db.session.query(db.func.sum(InventoryMovementData.quantity))\
            .filter_by(movement_type='OUTBOUND')\
            .filter(InventoryMovementData.date >= fecha_inicio)\
            .filter(InventoryMovementData.date <= fecha_fin)\
            .scalar() or 0
        
        print(f"\nTotal entradas (INBOUND): {total_inbound} unidades")
        print(f"Total salidas (OUTBOUND): {total_outbound} unidades")
        
        # Mostrar últimos 5 movimientos
        print("\nÚltimos movimientos generados:")
        for mov in InventoryMovementData.query\
            .filter(InventoryMovementData.date >= fecha_inicio)\
            .filter(InventoryMovementData.date <= fecha_fin)\
            .order_by(InventoryMovementData.date.desc())\
            .limit(5).all():
            print(f"{mov.date} | {mov.movement_type} | {mov.quantity} unidades | {mov.notes}")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        generar_historico_controlado()