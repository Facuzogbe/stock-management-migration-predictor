from flask import Blueprint, render_template
from src.services.predictor_service import generar_grafico_predictivo
from ..utils.auth_decorators import role_required

predictor_bp = Blueprint('predictor', __name__, url_prefix='/predictor')

@predictor_bp.route('/')
@role_required(["admin", "gerente"])

def index():
    grafico_url = generar_grafico_predictivo()
    return render_template('predictor/predictor.html', 
                         grafico_url=grafico_url)
