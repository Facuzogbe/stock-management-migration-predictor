import unittest
from unittest.mock import patch
from flask import Flask
from src.app.routes.predictor_routes import predictor_bp

class TestPredictorRoutes(unittest.TestCase):
    def setUp(self):
        # Create a Flask app and register the blueprint
        self.app = Flask(__name__)
        self.app.register_blueprint(predictor_bp)
        self.client = self.app.test_client()

    @patch('src.app.routes.predictor_routes.generar_grafico_predictivo')
    @patch('src.app.routes.predictor_routes.render_template')
    @patch('src.app.routes.predictor_routes.role_required')
    def test_index_route(self, mock_role_required, mock_render_template, mock_generar_grafico_predictivo):
        # Mock the role_required decorator to bypass authentication
        mock_role_required.return_value = lambda f: f

        # Mock the generar_grafico_predictivo function
        mock_generar_grafico_predictivo.return_value = "mocked_grafico_url"

        # Mock the render_template function
        mock_render_template.return_value = "mocked_template"

        # Make a GET request to the index route
        response = self.client.get('/predictor/')

        # Assert the response status code
        self.assertEqual(response.status_code, 200)

        # Assert that generar_grafico_predictivo was called
        mock_generar_grafico_predictivo.assert_called_once()

        # Assert that render_template was called with the correct arguments
        mock_render_template.assert_called_once_with(
            'predictor/predictor.html',
            grafico_url="mocked_grafico_url"
        )

if __name__ == '__main__':
    unittest.main()