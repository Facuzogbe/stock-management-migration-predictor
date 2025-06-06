import os
from flask import Flask, render_template
from src.extensions import db  # Importa db desde extensions
from .routes.api.product_api import product_api_bp 
from .routes.stock_routes import stock_bp

def create_app():
    app = Flask(__name__, static_folder="static", instance_relative_config=True)
    
    os.makedirs(app.instance_path, exist_ok=True)  # <--- Línea clave recien agregada

    
    # Configuración básica
    app.secret_key = "supersecretkey"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(app.instance_path, 'stock.db')}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Inicialización de extensiones
    db.init_app(app)
    
    # Importar y registrar blueprints dentro del contexto de la aplicación
    with app.app_context():
        from .routes.main_routes import main_bp                       
        from .routes.product_routes import product_bp                 
        from .routes.movimientos_routes import movimientos_bp         
        from .routes.predictor_routes import predictor_bp
        
        app.register_blueprint(main_bp)
        app.register_blueprint(product_bp, url_prefix="/products")
        app.register_blueprint(movimientos_bp, url_prefix="/movimientos")
        app.register_blueprint(stock_bp, url_prefix='/stock')
        app.register_blueprint(predictor_bp, url_prefix="/predictor")
        app.register_blueprint(product_api_bp)

        # Crear tablas si no existen
        db.create_all()

    # ⛔ Manejador para error 403
    @app.errorhandler(403)
    def forbidden_error(e):
        return render_template("errors/403.html"), 403

    return app


