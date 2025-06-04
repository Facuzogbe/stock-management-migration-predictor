# src/app/routes/prediccion_routes.py
from flask import Blueprint, render_template
from app.utils.auth_decorators import role_required

prediccion_bp = Blueprint('prediccion', __name__, template_folder='../templates')

@prediccion_bp.route('/')
@role_required(["admin", "gerente",])
def index():
    return render_template('prediccion/index.html')