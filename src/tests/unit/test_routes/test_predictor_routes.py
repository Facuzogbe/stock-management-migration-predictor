from unittest.mock import patch
import unittest

class TestPredictorRoutes(unittest.TestCase):
    def setUp(self):
        from src.app import create_app
        app = create_app()
        app.config['TESTING'] = True
        self.app = app
        self.client = app.test_client()

    @patch('src.app.routes.predictor_routes.role_required', lambda f: f)
    @patch('src.app.routes.predictor_routes.generar_grafico_predictivo')
    @patch('src.app.routes.predictor_routes.render_template')
    def test_index_route(self, mock_render_template, mock_generar_grafico_predictivo):
        mock_generar_grafico_predictivo.return_value = "mocked_grafico_url"
        mock_render_template.return_value = "mocked_template"

        response = self.client.get('/predictor/')
        self.assertEqual(response.status_code, 200)
