from src.models.product_master_data import ProductMasterData

def test_product_creation(db_session):
    product = ProductMasterData(
        product_id="TEST123",
        product_name="Test Product",
        sku="SKU123",
        cost=10.0,
        sale_price=20.0
    )
    db_session.add(product)
    db_session.commit()
    
    assert product.product_id == "TEST123"
    assert product.calculate_profit() == 10.0  # Ejemplo de método añadido