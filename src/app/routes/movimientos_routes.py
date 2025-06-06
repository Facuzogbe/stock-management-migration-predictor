from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..utils.auth_decorators import role_required

from src.services.movimiento_service import (
    obtener_movimientos, 
    registrar_movimiento,
    obtener_tipos_movimiento,
    VALID_MOVEMENT_TYPES
)
from src.models import db, ProductMasterData as Product
from sqlalchemy.exc import SQLAlchemyError

movimientos_bp = Blueprint('movimientos', __name__, template_folder='../templates/movimientos')

@movimientos_bp.route('/', methods=['GET'])
@role_required(["admin", "empleado"])

def index():
    """Muestra todos los movimientos de inventario"""
    movimientos = obtener_movimientos()
    return render_template('movimientos/index.html', movimientos=movimientos)

@movimientos_bp.route('/nuevo', methods=['GET', 'POST'])
@role_required(["admin", "empleado"])

def nuevo_movimiento():
    """Registra un nuevo movimiento de inventario"""
    # Obtener datos para el formulario
    productos_activos = Product.query.filter_by(active=True).order_by(Product.product_name).all()
    tipos_movimiento = obtener_tipos_movimiento()
    
    if request.method == 'POST':
        # Obtener datos del formulario
        producto_id = request.form.get('producto_id')
        movement_type = request.form.get('movement_type')
        cantidad = request.form.get('cantidad')
        order_id = request.form.get('order_id')
        notes = request.form.get('notes')

        # Validación básica de campos requeridos
        if not all([producto_id, movement_type, cantidad]):
            flash('Producto, tipo de movimiento y cantidad son campos requeridos', 'danger')
            return render_template('movimientos/nuevo.html', 
                                productos=productos_activos,
                                tipos_movimiento=tipos_movimiento)

        try:
            # Convertir y validar cantidad
            cantidad = int(cantidad)
            if cantidad <= 0:
                flash('La cantidad debe ser mayor a cero', 'danger')
                return render_template('movimientos/nuevo.html',
                                    productos=productos_activos,
                                    tipos_movimiento=tipos_movimiento)

            # Validar tipo de movimiento
            if movement_type not in VALID_MOVEMENT_TYPES:
                flash('Tipo de movimiento no válido', 'danger')
                return render_template('movimientos/nuevo.html',
                                    productos=productos_activos,
                                    tipos_movimiento=tipos_movimiento)

            # Registrar el movimiento (la validación de stock se hace en el servicio)
            registrar_movimiento(
                product_id=producto_id,
                movement_type=movement_type,
                quantity=cantidad,
                order_id=order_id,
                notes=notes
            )

            flash('Movimiento registrado con éxito', 'success')
            return redirect(url_for('movimientos.index'))

        except ValueError as e:
            flash(f'Error en los datos: {str(e)}', 'danger')
        except SQLAlchemyError:
            db.session.rollback()
            flash('Error al guardar en la base de datos', 'danger')
        except Exception as e:
            flash(f'Error inesperado: {str(e)}', 'danger')

    return render_template('movimientos/nuevo.html',
                         productos=productos_activos,
                         tipos_movimiento=tipos_movimiento)