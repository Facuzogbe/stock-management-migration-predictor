# src/app/routes/movimientos_routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.movimiento_service import obtener_movimientos, registrar_movimiento
from models import db, Product

movimientos_bp = Blueprint('movimientos', __name__, template_folder='../templates/movimientos')

@movimientos_bp.route('/', methods=['GET'])
def index():
    movimientos = obtener_movimientos()
    return render_template('movimientos/index.html', movimientos=movimientos)

@movimientos_bp.route('/nuevo', methods=['GET', 'POST'])
def nuevo_movimiento():
    if request.method == 'POST':
        producto_id = request.form.get('producto_id')
        tipo = request.form.get('tipo')
        cantidad = request.form.get('cantidad')

        try:
            cantidad = int(cantidad)
            registrar_movimiento(producto_id, tipo, cantidad)
            flash('Movimiento registrado con éxito', 'success')
            return redirect(url_for('movimientos.index'))
        except ValueError as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash(f'Error al registrar movimiento: {str(e)}', 'danger')

    productos = Product.query.all()
    return render_template('movimientos/nuevo.html', productos=productos)