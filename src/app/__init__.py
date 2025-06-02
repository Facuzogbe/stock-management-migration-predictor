import os
from flask import Flask
from src.extensions import db  # Importa db desde extensions
from .routes.stock_routes import stock_bp

def create_app():
    app = Flask(__name__, static_folder="static", instance_relative_config=True)
    
    # Configuración básica
    app.secret_key = "supersecretkey"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(app.instance_path, 'stock.db')}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Inicialización de extensiones
    db.init_app(app)
    
    # Importar y registrar blueprints dentro del contexto de la aplicación
    with app.app_context():
        from app.routes.main_routes import main_bp
        from app.routes.product_routes import product_bp
        from app.routes.movimientos_routes import movimientos_bp
        from app.routes.preddicion_routes import prediccion_bp
        
        app.register_blueprint(main_bp)
        app.register_blueprint(product_bp, url_prefix="/products")
        app.register_blueprint(movimientos_bp, url_prefix="/movimientos")
        app.register_blueprint(stock_bp, url_prefix='/stock')
        app.register_blueprint(prediccion_bp, url_prefix="/prediccion")
        
        # Crear tablas si no existen
        db.create_all()
    
    return app 