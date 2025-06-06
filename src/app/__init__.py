import os
from flask import Flask, render_template
from src.extensions import db

def create_app():
    app = Flask(__name__, static_folder="static", instance_relative_config=True)
    
    # Configuración mejorada
    app.config.from_mapping(
        SECRET_KEY="supersecretkey",
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{os.path.join(app.instance_path, 'stock.db')}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        STATIC_FOLDER=os.path.join(os.path.dirname(__file__), 'static')
    )
    
    # Asegurar que existan los directorios necesarios
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(os.path.join(app.static_folder, 'graficos'), exist_ok=True)
    
    # Inicialización de extensiones
    db.init_app(app)
    
    # Registrar blueprints
    register_blueprints(app)
    
    # Registrar manejadores de error
    register_error_handlers(app)
    
    return app

def register_blueprints(app):
    """Registra todos los blueprints de la aplicación"""
    from .routes.main_routes import main_bp
    from .routes.product_routes import product_bp
    from .routes.movimientos_routes import movimientos_bp
    from .routes.predictor_routes import predictor_bp
    from .routes.stock_routes import stock_bp
    from .routes.api.product_api import product_api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(product_bp, url_prefix="/products")
    app.register_blueprint(movimientos_bp, url_prefix="/movimientos")
    app.register_blueprint(stock_bp, url_prefix='/stock')
    app.register_blueprint(predictor_bp, url_prefix="/predictor")
    app.register_blueprint(product_api_bp)

def register_error_handlers(app):
    """Registra los manejadores de errores"""
    @app.errorhandler(403)
    def forbidden_error(e):
        return render_template("errors/403.html"), 403
    
    # Puedes agregar más manejadores aquí
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("errors/404.html"), 404