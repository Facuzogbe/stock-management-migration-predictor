from sqlalchemy.orm import relationship
from src.models import db

class ProductMasterData(db.Model):
    _tablename_ = 'product_master_data'
    _table_args_ = {'extend_existing': True}

    product_id = db.Column(db.String(10), primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    unit_of_measure = db.Column(db.String(20), default='Unit')
    cost = db.Column(db.Float, nullable=False)
    sale_price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50))
    location = db.Column(db.String(20))
    active = db.Column(db.Boolean, default=True)

    current_stock = relationship("CurrentStockData", back_populates="product", cascade="all, delete", passive_deletes=True)
    movements = relationship("InventoryMovementData", back_populates="product", cascade="all, delete", passive_deletes=True)
    predictions = relationship("PredictorStockData", back_populates="product", cascade="all, delete", passive_deletes=True)

    def _repr_(self):
        return f'<Product {self.product_id}: {self.product_name}>'

    def to_dict(self):
        return {
            'product_id': self.product_id,
            'product_name': self.product_name,
            'sku': self.sku,
            'unit_of_measure': self.unit_of_measure,
            'cost': self.cost,
            'sale_price': self.sale_price,
            'category': self.category,
            'location': self.location,
            'active': self.active
        }