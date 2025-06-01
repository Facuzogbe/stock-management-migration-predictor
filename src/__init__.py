from flask_sqlalchemy import SQLAlchemy

# Inicialización de la extensión SQLAlchemy
db = SQLAlchemy()

# Exporta db para que esté disponible como src.db
__all__ = ['db']