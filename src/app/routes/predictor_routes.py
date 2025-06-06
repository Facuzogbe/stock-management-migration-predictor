import os
from flask import Blueprint, render_template
from ..utils.auth_decorators import role_required
from src.services.predictor import obtener_serie_temporal_stock, generar_grafico_predictor

template_dir = os.path.join(os.path.dirname(__file__), '../templates')
predictor_bp = Blueprint('predictor', __name__, template_folder=template_dir)

@predictor_bp.route('/')
@role_required(["admin", "gerente"])
def index():
    try:
        df = obtener_serie_temporal_stock()
        imagen_path = generar_grafico_predictor(df)
        return render_template('predictor.html', image_path=imagen_path)
    except ValueError as e:
        return render_template('predictor.html', error=str(e))
