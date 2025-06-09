import unittest
from flask import Flask
from unittest.mock import patch
from src.app.routes.stock_routes import stock_bp

class TestStockRoutes(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.testing = True
        self.client = self.app.test_client()

    @patch('src.app.routes.stock_routes.render_template')
    @patch('src.app.routes.stock_routes.obtener_stock_actual')
    @patch('src.app.routes.stock_routes.role_required')
    def test_index_route(self, mock_role_required, mock_obtener_stock_actual, mock_render_template):
        mock_role_required.side_effect = lambda roles: lambda f: f
        mock_obtener_stock_actual.return_value = [{"item": "Product A", "quantity": 10}]
        mock_render_template.return_value = "Rendered Template"

        # Ahora registrás el blueprint DESPUÉS de aplicar los mocks
        self.app.register_blueprint(stock_bp)

        response = self.client.get('/')

        mock_obtener_stock_actual.assert_called_once()
        mock_render_template.assert_called_once_with('stock/index.html', stock_data=[{"item": "Product A", "quantity": 10}])
        self.assertEqual(response.data.decode(), "Rendered Template")
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
