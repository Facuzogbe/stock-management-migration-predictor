import sqlite3

# Conexión a la base de datos existente
from src.config import DB_PATH
conn = sqlite3.connect(DB_PATH)

cursor = conn.cursor()

# Activar claves foráneas (necesario en SQLite)
cursor.execute("PRAGMA foreign_keys = ON")

# Crear tabla de movimientos de inventario
cursor.execute('''
CREATE TABLE IF NOT EXISTS inventory_movements (
    movement_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    product_id TEXT NOT NULL,
    movement_type TEXT NOT NULL CHECK(movement_type IN ('INBOUND', 'OUTBOUND', 'ADJUSTMENT_IN', 'ADJUSTMENT_OUT')),
    quantity INTEGER NOT NULL,
    order_id TEXT,
    notes TEXT,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
)
''')

# Confirmar cambios y cerrar conexión
conn.commit()
conn.close()

print("✅ Tabla 'inventory_movements' creada (si no existía).")
