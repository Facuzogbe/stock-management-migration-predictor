from src.models.product_master_data import ProductMasterData

def test_product_creation():
    from src.models.product_master_data import ProductMasterData
    product = ProductMasterData(
        product_id="TEST123",
        product_name="Test Product",
        # ... otros campos requeridos
    )
    assert product.product_id == "TEST123"
    assert product.product_name == "Test Product"