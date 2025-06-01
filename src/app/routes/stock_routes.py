from flask import Blueprint, render_template
from src.models.current_stock_data import CurrentStock
from src.models.product_master_data import ProductMasterData

bp = Blueprint('stock', __name__, url_prefix='/stock')

@bp.route('/')
def stock_dashboard():
    stock_data = CurrentStock.query.join(ProductMasterData).all()
    return render_template('stock/dashboard.html', stock_data=stock_data)