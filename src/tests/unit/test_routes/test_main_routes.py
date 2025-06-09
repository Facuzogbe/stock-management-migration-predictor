import pytest
from flask import session
from src.app.routes.main_routes import main_bp, USER_DATA
from flask import Flask

@pytest.fixture
def app():
    app = Flask(__name__)
    app.secret_key = "test_secret_key"
    app.register_blueprint(main_bp)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_login_get(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Login" in response.data  # Assuming the login page contains "Login"

def test_login_post_valid_credentials(client):
    response = client.post("/login", data={"username": "Admin", "password": "stock2025"})
    with client.session_transaction() as session:
        assert session["username"] == "Admin"
        assert session["role"] == "admin"
    assert response.status_code == 302
    assert response.location.endswith("/home")

def test_login_post_invalid_credentials(client):
    response = client.post("/login", data={"username": "InvalidUser", "password": "wrongpassword"})
    assert response.status_code == 200
    assert b"Credenciales incorrectas" in response.data

def test_home_authenticated(client):
    with client.session_transaction() as session:
        session["username"] = "Admin"
    response = client.get("/home")
    assert response.status_code == 200
    assert b"Home" in response.data  # Assuming the home page contains "Home"

def test_home_unauthenticated(client):
    response = client.get("/home")
    assert response.status_code == 302
    assert response.location.endswith("/login")

def test_logout(client):
    with client.session_transaction() as session:
        session["username"] = "Admin"
    response = client.get("/logout")
    with client.session_transaction() as session:
        assert "username" not in session
    assert response.status_code == 302
    assert response.location.endswith("/login")