# setup.py
import sys
import os

# Aseguramos que src esté en el path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from app import create_app
from models.product_master_data import db

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()
    print("✅ Base de datos recreada correctamente.")
