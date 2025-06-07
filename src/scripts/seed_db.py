import os
import sys
from datetime import datetime, timedelta
import random
from flask import Flask

# Configuración
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from src.extensions import db
from src.models import InventoryMovementData, ProductMasterData, CurrentStockData
from src.services.movimiento_service import registrar_movimiento

def create_app():
    app = Flask(__name__, static_folder="static", instance_relative_config=True)
    from src.app import create_app as real_app
    return real_app()

def generar_historico_realista():
    print("Generando histórico realista 2023-2025...")
    
    with app.app_context():
        # 1. Limpiar y preparar BD
        db.drop_all()
        db.create_all()
        
        # 2. Crear producto de prueba
        producto = {
            'product_id': "P001",
            'product_name': "Laptop Business Pro",
            'sku': "LT-BP-2023",
            'category': "Electronics",
            'cost': 1350.0,
            'sale_price': 1899.0,
            'unit_of_measure': "Unit",
            'active': True
        }
        
        db.session.add(ProductMasterData(**producto))
        db.session.add(CurrentStockData(
            product_id=producto['product_id'],
            quantity=40,
            total_inventory_cost=40 * producto['cost']
        ))
        db.session.commit()
        
        # 3. Configuración de período histórico
        fecha_inicio = datetime(2023, 1, 1)
        fecha_fin = datetime(2025, 6, 6)  # Fecha actual
        rango_dias = (fecha_fin - fecha_inicio).days
        
        # 4. Generación de movimientos con distribución temporal real
        movimientos_generados = 0
        stock_actual = 40
        
        # Generar aproximadamente 2-3 movimientos por semana
        total_movimientos = int(rango_dias / 3 * 2.5)
        
        for i in range(total_movimientos):
            # Fecha aleatoria dentro del rango
            dias_aleatorios = random.randint(0, rango_dias)
            fecha_movimiento = fecha_inicio + timedelta(days=dias_aleatorios)
            
            # Hora aleatoria del día
            fecha_movimiento = fecha_movimiento.replace(
                hour=random.randint(8, 18),  # Horario comercial
                minute=random.randint(0, 59),
                second=random.randint(0, 59)
            )
            
            # Determinar tipo de movimiento (60% entrada, 40% salida)
            if random.random() < 0.6 or stock_actual < 15:
                movimiento_tipo = 'INBOUND'
                cantidad = random.randint(5, 20)
                stock_actual += cantidad
                notas = f"Compra a proveedor - {cantidad} unidades"
            else:
                movimiento_tipo = 'OUTBOUND'
                max_posible = min(10, stock_actual)
                cantidad = random.randint(1, max_posible)
                stock_actual -= cantidad
                notas = f"Venta a cliente - {cantidad} unidades"
            
            # Registrar movimiento (sin pasar date y movement_date)
            try:
                # Crear movimiento directamente para poder asignar fechas manuales
                movimiento = InventoryMovementData(
                    movement_id=f"MOV-{fecha_movimiento.strftime('%Y%m%d%H%M%S')}",
                    product_id=producto['product_id'],
                    movement_type=movimiento_tipo,
                    quantity=cantidad,
                    order_id=f"{movimiento_tipo[:2]}-{fecha_movimiento.strftime('%Y%m%d%H%M')}",
                    notes=notas,
                    date=fecha_movimiento,
                    movement_date=fecha_movimiento
                )
                db.session.add(movimiento)
                
                # Actualizar stock manualmente
                stock = CurrentStockData.query.get(producto['product_id'])
                if movimiento_tipo == 'INBOUND':
                    stock.quantity += cantidad
                else:
                    stock.quantity -= cantidad
                stock.total_inventory_cost = stock.quantity * producto['cost']
                stock.last_updated = datetime.utcnow()
                
                db.session.commit()
                movimientos_generados += 1
                
                # 25% de probabilidad de movimiento adicional cercano
                if random.random() < 0.25:
                    fecha_extra = fecha_movimiento + timedelta(hours=random.randint(1, 6))
                    tipo_extra = 'INBOUND' if random.random() < 0.7 else 'OUTBOUND'
                    cantidad_extra = random.randint(1, 5)
                    
                    movimiento_extra = InventoryMovementData(
                        movement_id=f"MOV-{fecha_extra.strftime('%Y%m%d%H%M%S')}",
                        product_id=producto['product_id'],
                        movement_type=tipo_extra,
                        quantity=cantidad_extra,
                        order_id=f"{tipo_extra[:2]}-EXTRA-{fecha_extra.strftime('%Y%m%d%H%M')}",
                        notes="Movimiento adicional por ajuste de inventario",
                        date=fecha_extra,
                        movement_date=fecha_extra
                    )
                    db.session.add(movimiento_extra)
                    
                    # Actualizar stock
                    if tipo_extra == 'INBOUND':
                        stock.quantity += cantidad_extra
                    else:
                        stock.quantity -= cantidad_extra
                    stock.total_inventory_cost = stock.quantity * producto['cost']
                    stock.last_updated = datetime.utcnow()
                    
                    db.session.commit()
                    movimientos_generados += 1
                    
            except Exception as e:
                db.session.rollback()
                print(f"Error en movimiento {i}: {str(e)}")
                continue
        
        # 5. Resultados y verificación
        print(f"\n✅ Histórico generado: {movimientos_generados} movimientos entre {fecha_inicio.date()} y {fecha_fin.date()}")
        print(f"Stock final: {stock_actual} unidades")
        
        # Verificar que hay movimientos antes de intentar acceder a ellos
        primer_movimiento = InventoryMovementData.query.order_by(InventoryMovementData.date.asc()).first()
        ultimo_movimiento = InventoryMovementData.query.order_by(InventoryMovementData.date.desc()).first()
        
        if primer_movimiento and ultimo_movimiento:
            print(f"\nPrimer movimiento: {primer_movimiento.date} | Último movimiento: {ultimo_movimiento.date}")
            
            # Mostrar algunos movimientos de ejemplo
            print("\nEjemplos de movimientos generados:")
            for mov in InventoryMovementData.query.order_by(db.func.random()).limit(5).all():
                print(f"{mov.date} | {mov.movement_type} | {mov.quantity} unidades | {mov.notes}")
        else:
            print("\n⚠️ No se generaron movimientos. Verifica los errores anteriores.")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        generar_historico_realista()