import unittest
from unittest.mock import patch, MagicMock
from src.services.stock_service import obtener_stock_actual, update_stock
from src.models import CurrentStockData, ProductMasterData
from datetime import datetime

class TestStockService(unittest.TestCase):

    @patch('src.services.stock_service.db')
    def test_obtener_stock_actual(self, mock_db):
        # Mocking the query and join behavior
        mock_query = mock_db.session.query.return_value
        mock_join = mock_query.join.return_value
        mock_order_by = mock_join.order_by.return_value
        mock_order_by.all.return_value = ['mocked_stock_data']

        result = obtener_stock_actual()

        mock_db.session.query.assert_called_once_with(CurrentStockData)
        mock_query.join.assert_called_once_with(ProductMasterData)
        mock_join.order_by.assert_called_once_with(ProductMasterData.product_name)
        self.assertEqual(result, ['mocked_stock_data'])

    @patch('src.services.stock_service.db')
    @patch('src.services.stock_service.CurrentStockData')
    @patch('src.services.stock_service.ProductMasterData')
    @patch('src.services.stock_service.datetime')
    def test_update_stock(self, mock_datetime, mock_product_master_data, mock_current_stock_data, mock_db):
        # Mocking datetime.datetime.utcnow()
        mock_datetime.datetime.utcnow.return_value = datetime(2023, 1, 1)

        # Mocking product and stock data
        mock_stock = MagicMock(quantity=10, total_inventory_cost=100)
        mock_product = MagicMock(cost=20)
        mock_current_stock_data.query.get.return_value = mock_stock
        mock_product_master_data.query.get.return_value = mock_product

        # Test INBOUND movement
        update_stock(1, 'INBOUND', 5)
        self.assertEqual(mock_stock.quantity, 15)
        self.assertEqual(mock_stock.total_inventory_cost, 300)
        self.assertEqual(mock_stock.last_updated, datetime(2023, 1, 1))
        mock_db.session.commit.assert_called()

        # Test OUTBOUND movement
        update_stock(1, 'OUTBOUND', 3)
        self.assertEqual(mock_stock.quantity, 12)
        self.assertEqual(mock_stock.total_inventory_cost, 240)
        self.assertEqual(mock_stock.last_updated, datetime(2023, 1, 1))
        mock_db.session.commit.assert_called()

        # Test creating a new stock entry
        mock_current_stock_data.query.get.return_value = None
        update_stock(2, 'INBOUND', 10)
        mock_db.session.add.assert_called()
        mock_db.session.commit.assert_called()

if __name__ == '__main__':
    unittest.main()
