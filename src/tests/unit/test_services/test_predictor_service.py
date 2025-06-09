import pytest
from unittest.mock import patch, MagicMock, call
from flask import Flask
from src.services.predictor_service import generar_grafico_predictivo
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

@pytest.fixture
def test_app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.static_folder = '/tmp/static'  # Ruta temporal para testing
    return app

class TestGenerarGraficoPredictivo:

    def test_success_with_sufficient_data(self, test_app):
        with test_app.app_context():
            # Mock de los datos y dependencias
            mock_movements = [
                MagicMock(
                    movement_date=datetime.now() - timedelta(days=i),
                    quantity=i+1,
                    movement_type="INBOUND" if i % 2 == 0 else "OUTBOUND"
                ) for i in range(7, 0, -1)
            ]
            
            with patch('src.services.predictor_service.InventoryMovementData.query') as mock_query, \
                 patch('src.services.predictor_service.plt') as mock_plt, \
                 patch('src.services.predictor_service.os.makedirs'), \
                 patch('src.services.predictor_service.current_app', test_app):

                # Configurar mocks
                mock_query.order_by.return_value.all.return_value = mock_movements
                
                # Ejecutar función
                result = generar_grafico_predictivo()
                
                # Verificaciones
                assert result == 'graficos/predictivo_premium.png'
                mock_plt.figure.assert_called_once()
                mock_plt.savefig.assert_called_once()
                assert mock_plt.plot.call_count >= 2  # Debería llamar a plot al menos 2 veces

    def test_insufficient_data(self, test_app):
        with test_app.app_context():
            with patch('src.services.predictor_service.InventoryMovementData.query') as mock_query:
                mock_query.order_by.return_value.all.return_value = []  # Datos insuficientes
                
                result = generar_grafico_predictivo()
                assert result is None

    def test_exception_handling(self, test_app):
        with test_app.app_context():
            with patch('src.services.predictor_service.InventoryMovementData.query') as mock_query, \
                 patch('src.services.predictor_service.current_app.logger.error') as mock_logger:
                
                mock_query.order_by.side_effect = Exception("DB Error")
                
                result = generar_grafico_predictivo()
                assert result is None
                mock_logger.assert_called()