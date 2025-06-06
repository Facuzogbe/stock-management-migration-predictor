import os
import sys
from datetime import datetime

# Añade el directorio raíz del proyecto al path de Python
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

# Ahora las importaciones funcionarán
from src.models import db
from src.app import create_app  # Ajusta según dónde esté tu create_app()

app = create_app()

with app.app_context():
    print("⚠️ Eliminando todas las tablas...")
    db.drop_all()
    print("🔄 Creando tablas actualizadas...")
    db.create_all()
    print("✅ Base de datos reseteada correctamente.")


# python -m src.scripts.reset_db