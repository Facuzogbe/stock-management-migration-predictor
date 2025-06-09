import unittest
from datetime import date
from src.models.predictor_stock_data import PredictorStockData
from unittest.mock import MagicMock

class TestPredictorStockData(unittest.TestCase):

    def setUp(self):
        # Mocking the product relationship
        self.mock_product = MagicMock()
        self.mock_product.product_name = "Test Product"

        # Creating a sample PredictorStockData instance
        self.stock_data = PredictorStockData(
            id=1,
            date=date(2023, 10, 1),
            product_id="P12345",
            units_sold=100,
            avg_sale_price=19.99,
            promotion_active=True,
            special_event="Black Friday"
        )
        self.stock_data.product = self.mock_product

    def test_repr(self):
        expected_repr = "<Prediction Data 2023-10-01: P12345 - Sold 100>"
        self.assertEqual(repr(self.stock_data), expected_repr)

    def test_to_dict(self):
        expected_dict = {
            'id': 1,
            'date': "2023-10-01",
            'product_id': "P12345",
            'product_name': "Test Product",
            'units_sold': 100,
            'avg_sale_price': 19.99,
            'promotion_active': True,
            'special_event': "Black Friday"
        }
        self.assertEqual(self.stock_data.to_dict(), expected_dict)

    def test_to_dict_no_product(self):
        # Test when product is None
        self.stock_data.product = None
        expected_dict = {
            'id': 1,
            'date': "2023-10-01",
            'product_id': "P12345",
            'product_name': None,
            'units_sold': 100,
            'avg_sale_price': 19.99,
            'promotion_active': True,
            'special_event': "Black Friday"
        }
        self.assertEqual(self.stock_data.to_dict(), expected_dict)

if __name__ == '__main__':
    unittest.main()