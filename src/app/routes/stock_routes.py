from flask import Blueprint, render_template
from src.services.stock_service import obtener_stock_actual
from ..utils.auth_decorators import role_required 
stock_bp = Blueprint('stock', __name__, template_folder='../templates/stock')

@stock_bp.route('/')
@role_required(["admin", "gerente", "empleado"])

def index():
    stock_data = obtener_stock_actual()
    return render_template('stock/index.html', stock_data=stock_data)