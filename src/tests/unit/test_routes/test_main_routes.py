# test_main_routes.py

import pytest
from flask import Flask
from src.app.routes.main_routes import main_bp
from pathlib import Path
import os


@pytest.fixture
def app():
    app = Flask(__name__)
    app.secret_key = "test_secret_key"
    app.config['TESTING'] = True

    # Setup de templates
    test_templates_dir = Path(__file__).parent / 'test_templates'
    os.makedirs(test_templates_dir / 'login', exist_ok=True)

    # Crear templates con mensajes variables
    with open(test_templates_dir / 'login' / 'login.html', 'w') as f:
        f.write("""
            <h1>Login</h1>
            {% if error %}
                <p>{{ error }}</p>
            {% endif %}
        """)
    with open(test_templates_dir / 'home.html', 'w') as f:
        f.write("<h1>Home</h1>")

    app.template_folder = test_templates_dir
    app.register_blueprint(main_bp)
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def test_login_get(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Login" in response.data


def test_login_post_valid_credentials(client):
    response = client.post("/login", data={"username": "Admin", "password": "stock2025"}, follow_redirects=False)
    assert response.status_code == 302
    assert response.location.endswith("/home")

    with client.session_transaction() as sess:
        assert sess["username"] == "Admin"
        assert sess["role"] == "admin"


def test_login_post_invalid_credentials(client):
    response = client.post("/login", data={"username": "Invalido", "password": "mal"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Credenciales incorrectas" in response.data


def test_login_redirect_if_already_logged_in(client):
    # Loguearse
    client.post("/login", data={"username": "Admin", "password": "stock2025"}, follow_redirects=False)

    # Acceder de nuevo a /login debería redirigir a /home
    response = client.get("/login", follow_redirects=False)
    assert response.status_code == 302
    assert response.location.endswith("/home")


def test_home_authenticated(client):
    client.post("/login", data={"username": "Admin", "password": "stock2025"})
    response = client.get("/home")
    assert response.status_code == 200
    assert b"Home" in response.data


def test_home_unauthenticated(client):
    response = client.get("/home", follow_redirects=False)
    assert response.status_code == 302
    assert response.location.endswith("/login")


def test_logout_clears_session(client):
    client.post("/login", data={"username": "Admin", "password": "stock2025"})
    response = client.get("/logout", follow_redirects=False)
    assert response.status_code == 302
    assert response.location.endswith("/login")

    with client.session_transaction() as sess:
        assert "username" not in sess
        assert "role" not in sess
