import unittest
from unittest.mock import patch, MagicMock, call
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

from src.models.product_master_data import ProductMasterData as Product
from src.models.inventory_movement_data import InventoryMovementData as Movimiento
from src.models.current_stock_data import CurrentStockData
from src.services.movimiento_service import (
    registrar_movimiento,
    actualizar_stock_directo,
    obtener_tipos_movimiento,
    obtener_movimientos,
    VALID_MOVEMENT_TYPES
)

class TestMovimientoService(unittest.TestCase):

    ## Tests para registrar_movimiento
    
    @patch('src.services.movimiento_service.Product.query.get')
    @patch('src.services.movimiento_service.CurrentStockData.query.get')
    @patch('src.services.movimiento_service.Movimiento.query.order_by')
    @patch('src.services.movimiento_service.db.session')
    def test_registrar_movimiento_inbound(self, mock_session, mock_order_by, mock_stock_get, mock_product_get):
        # Configurar mocks
        mock_product = MagicMock()
        mock_product.cost = 10.0
        mock_product_get.return_value = mock_product

        mock_stock = MagicMock()
        mock_stock.quantity = 50
        mock_stock_get.return_value = mock_stock

        mock_last_movement = MagicMock()
        mock_last_movement.movement_id = "M001"
        mock_order_by.return_value.first.return_value = mock_last_movement

        # Ejecutar
        movimiento = registrar_movimiento("P001", "INBOUND", 10)

        # Verificar
        self.assertEqual(movimiento.movement_type, "INBOUND")
        self.assertEqual(movimiento.quantity, 10)
        mock_session.add.assert_called()
        mock_session.commit.assert_called()


    @patch('src.services.movimiento_service.db.session')
    def test_registrar_movimiento_invalid_type(self, mock_session):
        # Ejecutar y verificar excepción
        with self.assertRaises(ValueError) as context:
            registrar_movimiento("P001", "INVALID_TYPE", 10)

        self.assertIn("Tipo de movimiento inválido", str(context.exception))
        mock_session.rollback.assert_called()

    @patch('src.services.movimiento_service.Product.query.get')
    @patch('src.services.movimiento_service.CurrentStockData.query.get')
    @patch('src.services.movimiento_service.Movimiento.query.order_by')
    @patch('src.services.movimiento_service.db.session')
    def test_registrar_movimiento_db_error(self, mock_session, mock_order_by, mock_stock_get, mock_product_get):
        # Configurar mocks
        mock_product = MagicMock()
        mock_product_get.return_value = mock_product

        mock_stock = MagicMock()
        mock_stock_get.return_value = mock_stock

        mock_last_movement = MagicMock()
        mock_order_by.return_value.first.return_value = mock_last_movement

        # Simular error en commit
        mock_session.commit.side_effect = SQLAlchemyError("DB Error")

        # Ejecutar y verificar excepción
        with self.assertRaises(ValueError) as context:
            registrar_movimiento("P001", "INBOUND", 10)

        self.assertIn("Error en transacción", str(context.exception))
        mock_session.rollback.assert_called()

    ## Tests para actualizar_stock_directo

    @patch('src.services.movimiento_service.CurrentStockData.query.get')
    @patch('src.services.movimiento_service.db.session')
    def test_actualizar_stock_directo_db_error(self, mock_session, mock_stock_get):
        # Configurar mock
        mock_stock = MagicMock()
        mock_stock_get.return_value = mock_stock

        # Simular error en commit
        mock_session.commit.side_effect = SQLAlchemyError("DB Error")

        # Ejecutar y verificar excepción
        with self.assertRaises(ValueError) as context:
            actualizar_stock_directo("P001", "INBOUND", 10, 15.0)

        self.assertIn("Error en actualización de stock", str(context.exception))
        mock_session.rollback.assert_called_once()

    ## Tests para obtener_tipos_movimiento

    def test_obtener_tipos_movimiento(self):
        tipos = obtener_tipos_movimiento()
        self.assertEqual(tipos, VALID_MOVEMENT_TYPES)

if __name__ == '__main__':
    unittest.main()
