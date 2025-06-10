import pytest
from unittest.mock import patch
from src.app import create_app

@pytest.fixture
def app():
    def bypass_role_required(*args, **kwargs):
        pass

    with patch('src.app.routes.movimientos_routes.role_required', new=bypass_role_required):
        app = create_app()
        app.config.update({
            "TESTING": True,
            "SECRET_KEY": "test-key",
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
        })
        yield app

@pytest.fixture
def client(app):
    return app.test_client()
