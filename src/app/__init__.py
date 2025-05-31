from flask import Flask
from models import db
from app.routes.main_routes import main_bp
from app.routes.product_routes import product_bp
from app.routes.movimientos_routes import movimientos_bp
from app.routes.preddicion_routes import prediccion_bp

def create_app():
    app = Flask(__name__, static_folder="static")

    app.secret_key = "supersecretkey"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///stock.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(main_bp)
    app.register_blueprint(product_bp, url_prefix="/products")
    app.register_blueprint(movimientos_bp, url_prefix="/movimientos")
    app.register_blueprint(prediccion_bp, url_prefix="/prediccion")

    return app
