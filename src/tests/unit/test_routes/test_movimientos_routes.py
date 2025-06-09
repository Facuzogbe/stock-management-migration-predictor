import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, session
from src.app.routes.movimientos_routes import movimientos_bp

# ---------- MOCK DECORATOR ----------
def bypass_role_required(roles):
    def wrapper(f):
        return f
    return wrapper

# ---------- SETUP CLIENT ----------
import pytest
from src.app import create_app  # Ajustá esto si tu app se importa distinto

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            yield client

# ---------- TESTS ----------

@patch('src.app.routes.movimientos_routes.role_required', bypass_role_required)
@patch('src.app.routes.movimientos_routes.obtener_movimientos')
def test_index_movimientos_success(mock_obtener, client):
    mock_obtener.return_value = [{'id': 1, 'type': 'alta', 'quantity': 5}]
    with patch('src.app.routes.movimientos_routes.render_template') as mock_render:
        mock_render.return_value = 'ok'
        response = client.get('/movimientos/')
        assert response.status_code == 200
        mock_render.assert_called_with('Movimientos/index.html', movimientos=mock_obtener.return_value)

@patch('src.app.routes.movimientos_routes.role_required', bypass_role_required)
@patch('src.app.routes.movimientos_routes.obtener_movimientos', side_effect=Exception("DB error"))
def test_index_movimientos_error(mock_obtener, client):
    with patch('src.app.routes.movimientos_routes.render_template') as mock_render, \
         patch('src.app.routes.movimientos_routes.flash') as mock_flash:
        mock_render.return_value = 'ok'
        response = client.get('/movimientos/')
        assert response.status_code == 200
        mock_render.assert_called_with('Movimientos/index.html', movimientos=[])
        mock_flash.assert_called()

@patch('src.app.routes.movimientos_routes.role_required', bypass_role_required)
@patch('src.app.routes.movimientos_routes.Product.query')
@patch('src.app.routes.movimientos_routes.obtener_tipos_movimiento')
def test_get_nuevo_movimiento(mock_tipos, mock_query, client):
    mock_query.filter_by.return_value.order_by.return_value.all.return_value = []
    mock_tipos.return_value = ['alta', 'baja']
    with patch('src.app.routes.movimientos_routes.render_template') as mock_render:
        mock_render.return_value = 'ok'
        response = client.get('/movimientos/nuevo')
        assert response.status_code == 200
        mock_render.assert_called()

# -------- POST /nuevo: success --------
@patch('src.app.routes.movimientos_routes.role_required', bypass_role_required)
@patch('src.app.routes.movimientos_routes.Product.query')
@patch('src.app.routes.movimientos_routes.obtener_tipos_movimiento')
@patch('src.app.routes.movimientos_routes.registrar_movimiento')
def test_post_nuevo_movimiento_success(mock_registrar, mock_tipos, mock_query, client):
    mock_query.filter_by.return_value.order_by.return_value.all.return_value = []
    mock_tipos.return_value = ['alta']
    mock_registrar.return_value = MagicMock()
    data = {
        'product_id': '1',
        'movement_type': 'alta',
        'quantity': '10',
        'order_id': '123',
        'notes': 'nota de prueba'
    }
    with patch('src.app.routes.movimientos_routes.flash'), \
         patch('src.app.routes.movimientos_routes.redirect') as mock_redirect, \
         patch('src.app.routes.movimientos_routes.url_for') as mock_url:
        mock_url.return_value = '/movimientos/'
        response = client.post('/movimientos/nuevo', data=data)
        mock_redirect.assert_called()
        assert response.status_code == 302 or response.status_code == 200

# -------- POST /nuevo: Faltan campos --------
@patch('src.app.routes.movimientos_routes.role_required', bypass_role_required)
@patch('src.app.routes.movimientos_routes.Product.query')
@patch('src.app.routes.movimientos_routes.obtener_tipos_movimiento')
def test_post_nuevo_movimiento_faltan_campos(mock_tipos, mock_query, client):
    mock_query.filter_by.return_value.order_by.return_value.all.return_value = []
    mock_tipos.return_value = ['alta']
    casos = [
        {'movement_type': 'alta', 'quantity': '10'},  # Falta product_id
        {'product_id': '1', 'quantity': '10'},        # Falta movement_type
        {'product_id': '1', 'movement_type': 'alta'}  # Falta quantity
    ]
    for data in casos:
        with patch('src.app.routes.movimientos_routes.render_template') as mock_render, \
             patch('src.app.routes.movimientos_routes.flash'):
            mock_render.return_value = 'ok'
            response = client.post('/movimientos/nuevo', data=data)
            assert response.status_code == 200
            mock_render.assert_called()

# -------- POST /nuevo: cantidad inválida --------
@patch('src.app.routes.movimientos_routes.role_required', bypass_role_required)
@patch('src.app.routes.movimientos_routes.Product.query')
@patch('src.app.routes.movimientos_routes.obtener_tipos_movimiento')
def test_post_nuevo_movimiento_cantidad_invalida(mock_tipos, mock_query, client):
    mock_query.filter_by.return_value.order_by.return_value.all.return_value = []
    mock_tipos.return_value = ['alta']
    casos = [
        {'product_id': '1', 'movement_type': 'alta', 'quantity': 'abc'},  # No es número
        {'product_id': '1', 'movement_type': 'alta', 'quantity': '0'},    # Cero
        {'product_id': '1', 'movement_type': 'alta', 'quantity': '-5'},   # Negativo
    ]
    for data in casos:
        with patch('src.app.routes.movimientos_routes.render_template') as mock_render, \
             patch('src.app.routes.movimientos_routes.flash'):
            mock_render.return_value = 'ok'
            response = client.post('/movimientos/nuevo', data=data)
            assert response.status_code == 200
            mock_render.assert_called()

# -------- POST /nuevo: excepción inesperada --------
@patch('src.app.routes.movimientos_routes.role_required', bypass_role_required)
@patch('src.app.routes.movimientos_routes.Product.query')
@patch('src.app.routes.movimientos_routes.obtener_tipos_movimiento')
@patch('src.app.routes.movimientos_routes.registrar_movimiento', side_effect=Exception("Fallo interno"))
@patch('src.app.routes.movimientos_routes.db.session.rollback')
def test_post_nuevo_movimiento_exception(mock_rollback, mock_registrar, mock_tipos, mock_query, client):
    mock_query.filter_by.return_value.order_by.return_value.all.return_value = []
    mock_tipos.return_value = ['alta']
    data = {
        'product_id': '1',
        'movement_type': 'alta',
        'quantity': '5',
    }
    with patch('src.app.routes.movimientos_routes.render_template') as mock_render, \
         patch('src.app.routes.movimientos_routes.flash'):
        mock_render.return_value = 'ok'
        response = client.post('/movimientos/nuevo', data=data)
        assert response.status_code == 200
        mock_render.assert_called()
        mock_rollback.assert_called()
