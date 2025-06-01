from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from services.movimiento_service import obtener_movimientos, registrar_movimiento
from models import db, Product
from sqlalchemy.exc import SQLAlchemyError

movimientos_bp = Blueprint('movimientos', __name__, template_folder='../templates/movimientos')

@movimientos_bp.route('/', methods=['GET'])
def index():
    movimientos = obtener_movimientos()
    return render_template('movimientos/index.html', movimientos=movimientos)

@movimientos_bp.route('/nuevo', methods=['GET', 'POST'])
def nuevo_movimiento():
    productos_activos = Product.query.filter_by(active=True).order_by(Product.product_name).all()
    
    if request.method == 'POST':
        producto_id = request.form.get('producto_id')
        tipo = request.form.get('tipo').upper()  # Convertir a mayúsculas para consistencia
        cantidad = request.form.get('cantidad')

        # Validación básica
        if not all([producto_id, tipo, cantidad]):
            flash('Todos los campos son requeridos', 'danger')
            return render_template('movimientos/nuevo.html', productos=productos_activos)

        try:
            cantidad = int(cantidad)
            if cantidad <= 0:
                flash('La cantidad debe ser mayor a cero', 'danger')
                return render_template('movimientos/nuevo.html', productos=productos_activos)
                
            producto = Product.query.get(producto_id)
            if not producto:
                flash('Producto no encontrado', 'danger')
                return render_template('movimientos/nuevo.html', productos=productos_activos)

            # --- VALIDACIÓN DE STOCK PARA SALIDAS ---
            if tipo == "OUTBOUND" and producto.stock < cantidad:
                flash(f'Stock insuficiente. Disponible: {producto.stock}', 'danger')
                return render_template('movimientos/nuevo.html', productos=productos_activos)
            # ---------------------------------------

            registrar_movimiento(producto_id, tipo, cantidad)
            
            # Actualizar stock del producto
            if tipo == "INBOUND":
                producto.stock += cantidad
            elif tipo == "OUTBOUND":
                producto.stock -= cantidad
            db.session.commit()

            flash('Movimiento registrado con éxito', 'success')
            return redirect(url_for('movimientos.index'))

        except ValueError:
            flash('Cantidad debe ser un número válido', 'danger')
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Error de base de datos: {str(e)}', 'danger')
        except Exception as e:
            flash(f'Error inesperado: {str(e)}', 'danger')

    return render_template('movimientos/nuevo.html', productos=productos_activos)