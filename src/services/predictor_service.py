import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pandas as pd
from src.models import db, InventoryMovementData
from flask import current_app
from sklearn.linear_model import LinearRegression
import numpy as np

def generar_grafico_predictivo():
    try:
        # 1. Obtener datos históricos
        movimientos = InventoryMovementData.query.order_by(InventoryMovementData.movement_date.asc()).all()
        
        if len(movimientos) < 7:  # Mínimo para predicción
            return None
            
        # 2. Preparar DataFrame con tipo de movimiento
        datos = [{
            'fecha': m.movement_date,
            'cantidad': m.quantity,
            'tipo': m.movement_type
        } for m in movimientos]

        df = pd.DataFrame(datos)
        df = df.resample('D', on='fecha').agg({
            'cantidad': 'sum',
            'tipo': lambda x: x.mode()[0] if not x.empty else None
        }).fillna(0)
        
        # 3. Calcular stock acumulado (asumiendo stock inicial=40)
        df['entradas'] = df.apply(lambda x: x['cantidad'] if x['tipo'] == 'INBOUND' else 0, axis=1)
        df['salidas'] = df.apply(lambda x: x['cantidad'] if x['tipo'] == 'OUTBOUND' else 0, axis=1)
        df['stock'] = 40 + df['entradas'].cumsum() - df['salidas'].cumsum()
        
        # 4. Modelo para predecir stock
        df['dias'] = np.arange(len(df))
        X = df['dias'].values.reshape(-1, 1)
        y = df['stock'].values
        
        modelo = LinearRegression()
        modelo.fit(X, y)
        
        # 5. Predicción 7 días
        dias_futuros = np.arange(len(df), len(df)+7).reshape(-1, 1)
        predicciones = modelo.predict(dias_futuros)
        fechas_futuras = [df.index[-1] + timedelta(days=i+1) for i in range(7)]

        # 6. Gráfico mejorado (combinando ambos estilos)
        plt.figure(figsize=(14, 7))
        
        # Configuración de estilo
        plt.style.use('seaborn-v0_8')
        plt.rcParams['axes.grid'] = True
        plt.rcParams['grid.alpha'] = 0.3
        
        # Histórico - línea azul gruesa
        plt.plot(df.index, df['stock'], 
                color='#1f77b4', 
                linewidth=2.5, 
                label='Stock histórico')
        
        # Línea divisoria "Hoy" - gris punteada
        hoy = df.index[-1]
        plt.axvline(x=hoy, 
                   color='gray', 
                   linestyle='--', 
                   linewidth=1.5,
                   alpha=0.7,
                   label='Fecha actual')
        
        # Predicción - línea roja punteada gruesa
        plt.plot(fechas_futuras, predicciones, 
                color='#d62728', 
                linestyle='--', 
                linewidth=2.5, 
                alpha=0.9,
                label='Predicción lineal')
        
        # Rango probable - área semitransparente roja
        plt.fill_between(fechas_futuras, 
                        predicciones * 0.9, 
                        predicciones * 1.1,
                        color='#d62728', 
                        alpha=0.15, 
                        label='Rango probable (±10%)')
        
        # Detalles del gráfico
        plt.title('Predicción de Nivel de Stock\nRegresión Lineal', 
                 fontsize=14, pad=20)
        plt.xlabel('Fecha', fontsize=12)
        plt.ylabel('Unidades en Stock', fontsize=12)
        
        # Leyenda con sombra
        legend = plt.legend(framealpha=1, shadow=True)
        legend.get_frame().set_facecolor('white')
        
        # Ajustar márgenes
        plt.tight_layout()
        plt.margins(x=0.02)

        # 7. Guardar imagen en alta calidad
        os.makedirs(os.path.join(current_app.static_folder, 'graficos'), exist_ok=True)
        ruta_grafico = os.path.join(current_app.static_folder, 'graficos', 'predictivo_premium.png')
        plt.savefig(ruta_grafico, dpi=120, bbox_inches='tight')
        plt.close()
        
        return 'graficos/predictivo_premium.png'
        
    except Exception as e:
        current_app.logger.error(f"Error en gráfico predictivo: {e}", exc_info=True)
        return None