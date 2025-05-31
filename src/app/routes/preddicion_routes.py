# src/app/routes/prediccion_routes.py
from flask import Blueprint, render_template

prediccion_bp = Blueprint('prediccion', __name__, template_folder='../templates')

@prediccion_bp.route('/')
def index():
    return render_template('prediccion/index.html')
