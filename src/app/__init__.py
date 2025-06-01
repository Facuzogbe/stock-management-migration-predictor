import os
from flask import Flask
from models import db
from app.routes.main_routes import main_bp
from app.routes.product_routes import product_bp
from app.routes.movimientos_routes import movimientos_bp
from app.routes.preddicion_routes import prediccion_bp

# Armamos la ruta absoluta a la carpeta "instance" que está al nivel de "src"
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")

def create_app():
    app = Flask(__name__, static_folder="static", instance_path=INSTANCE_DIR, instance_relative_config=True)

    app.secret_key = "supersecretkey"

    # Ruta absoluta al archivo stock.db dentro de la carpeta "instance"
    DB_PATH = os.path.join(app.instance_path, "stock.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
    print("USANDO BASE:", app.config["SQLALCHEMY_DATABASE_URI"])

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(main_bp)
    app.register_blueprint(product_bp, url_prefix="/products")
    app.register_blueprint(movimientos_bp, url_prefix="/movimientos")
    app.register_blueprint(prediccion_bp, url_prefix="/prediccion")
    # recordar borrar este print
    print("Usando base de datos:", app.config["SQLALCHEMY_DATABASE_URI"])

    return app
