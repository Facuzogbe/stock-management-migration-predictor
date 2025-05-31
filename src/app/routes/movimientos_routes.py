# src/app/routes/movimientos_routes.py
from flask import Blueprint, render_template

movimientos_bp = Blueprint('movimientos', __name__, template_folder='../templates')

@movimientos_bp.route('/')
def index():
    return render_template('movimientos/index.html')
