import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pandas as pd
from src.models import db, InventoryMovementData
from flask import current_app

def generar_grafico_predictivo():
    try:
        # 1. Obtener datos históricos
# En movimientos_routes.py y predictor.py
        movimientos = InventoryMovementData.query.order_by(InventoryMovementData.movement_date.desc()).all()
        
        if not movimientos:
            return None
            
        # 2. Preparar datos para DataFrame
        datos = [{
            'fecha': m.movement_date,
            'cantidad': m.quantity
        } for m in movimientos]
        
        df = pd.DataFrame(datos)
        df.set_index('fecha', inplace=True)
        
        # 3. Generar gráfico
        plt.figure(figsize=(12, 6))
        plt.plot(df.index, df['cantidad'], label='Histórico')
        
        # 4. Lógica de predicción aquí...
        
        plt.title('Análisis Predictivo de Stock')
        plt.xlabel('Fecha')
        plt.ylabel('Cantidad')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        
        # 5. Guardar imagen
        os.makedirs(os.path.join(current_app.static_folder, 'graficos'), exist_ok=True)
        ruta_grafico = os.path.join(current_app.static_folder, 'graficos', 'predictivo.png')
        plt.savefig(ruta_grafico)
        plt.close()
        
        return 'graficos/predictivo.png'
        
    except Exception as e:
        current_app.logger.error(f"Error generando gráfico predictivo: {e}")
        return None