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

movimientos_bp = Blueprint('movimientos', __name__, template_folder='../templates/Movimientos')

@movimientos_bp.route('/', methods=['GET'])
@role_required(["admin", "empleado"])
def index():
    """Muestra todos los movimientos de inventario"""
    try:
        movimientos = obtener_movimientos()
        return render_template('Movimientos/index.html', movimientos=movimientos)
    except Exception as e:
        flash(f'Error al cargar movimientos: {str(e)}', 'danger')
        return render_template('Movimientos/index.html', movimientos=[])

@movimientos_bp.route('/nuevo', methods=['GET', 'POST'])
@role_required(["admin", "empleado"])
def nuevo_movimiento():
    """Registra un nuevo movimiento de inventario"""
    productos_activos = Product.query.filter_by(active=True).order_by(Product.product_name).all()
    tipos_movimiento = obtener_tipos_movimiento()
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario (usando 'product_id' directamente)
            product_id = request.form.get('product_id')  # Cambiado de 'producto_id'
            movement_type = request.form.get('movement_type')
            quantity = request.form.get('quantity')
            order_id = request.form.get('order_id')
            notes = request.form.get('notes')

            # Validación mejorada
            if not product_id:
                flash('Debe seleccionar un producto', 'danger')
                return render_template('Movimientos/nuevo.html',
                                    productos=productos_activos,
                                    tipos_movimiento=tipos_movimiento)

            if not movement_type:
                flash('Debe seleccionar un tipo de movimiento', 'danger')
                return render_template('Movimientos/nuevo.html',
                                    productos=productos_activos,
                                    tipos_movimiento=tipos_movimiento)

            if not quantity:
                flash('La cantidad es requerida', 'danger')
                return render_template('Movimientos/nuevo.html',
                                    productos=productos_activos,
                                    tipos_movimiento=tipos_movimiento)

            # Convertir cantidad a entero
            try:
                quantity = int(quantity)
                if quantity <= 0:
                    flash('La cantidad debe ser mayor a cero', 'danger')
                    return render_template('Movimientos/nuevo.html',
                                        productos=productos_activos,
                                        tipos_movimiento=tipos_movimiento)
            except ValueError:
                flash('La cantidad debe ser un número válido', 'danger')
                return render_template('Movimientos/nuevo.html',
                                    productos=productos_activos,
                                    tipos_movimiento=tipos_movimiento)

            # Registrar el movimiento
            movimiento = registrar_movimiento(
                product_id=product_id,
                movement_type=movement_type,
                quantity=quantity,
                order_id=order_id,
                notes=notes
            )

            flash('Movimiento registrado con éxito', 'success')
            return redirect(url_for('movimientos.index'))

        except ValueError as e:
            flash(f'Error en los datos: {str(e)}', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Error inesperado: {str(e)}', 'danger')

    return render_template('Movimientos/nuevo.html',
                         productos=productos_activos,
                         tipos_movimiento=tipos_movimiento)