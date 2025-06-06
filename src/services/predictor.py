# src/app/services/predictor.py

import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose
import matplotlib
matplotlib.use('Agg')  # Usa un backend que no lanza ventanas
import matplotlib.pyplot as plt
from src.models.inventory_movement_data import InventoryMovementData
from src.extensions import db

def obtener_serie_temporal_stock():
    query = db.session.query(
        InventoryMovementData.movement_date.label("fecha"),
        InventoryMovementData.quantity.label("cantidad")
    ).all()

    df = pd.DataFrame(query, columns=['fecha', 'cantidad'])

    # 👉 Convertimos fechas y eliminamos las inválidas
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    df = df.dropna(subset=['fecha'])

    if df.empty:
        return df  # Evita continuar con un DataFrame vacío

    # 👉 Agrupamos por semana
    df = df.groupby(pd.Grouper(key='fecha', freq='W')).sum().reset_index()

    if df.empty:
        return df

    # 👉 Establecemos el índice para el modelo
    df = df.set_index('fecha')
    df.index.freq = 'W'

    return df

def generar_grafico_predictor(df):
    if df.empty:
        raise ValueError("La serie temporal está vacía. No hay datos para procesar.")
    if len(df) < 104:
        raise ValueError(f"Se requieren al menos 104 observaciones, pero solo hay {len(df)}.")

    # 👉 Descomposición estacional
    decomp = seasonal_decompose(df['cantidad'], period=52)
    fig = decomp.plot()
    fig.suptitle('Descomposición de la Serie Temporal', fontsize=16)

    # 👉 Guardamos imagen en el directorio estático
    path = 'src/app/static/img/predictor_plot.png'
    fig.savefig(path)
    plt.close(fig)  # libera memoria

    return path
