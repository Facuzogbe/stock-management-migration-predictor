# app/__init__.py

from flask import Flask
from datetime import timedelta

def create_app():
    app = Flask(__name__)

    # Clave secreta para sesiones
    app.secret_key = "supersecreto"

    # ⏳ Establecer duración de la sesión a 30 minutos
    app.permanent_session_lifetime = timedelta(minutes=2)

    # Registrar el blueprint
    from .routes.main_routes import main_bp
    app.register_blueprint(main_bp)

    return app
