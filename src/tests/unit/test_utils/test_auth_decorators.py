import pytest
from flask import Flask, session
from src.app.utils.auth_decorators import role_required

@pytest.fixture
def app():
    app = Flask(__name__)
    app.secret_key = "test_secret_key"

    @app.route("/test_admin")
    @role_required(["admin"])
    def test_admin():
        return "Admin Access Granted"

    @app.route("/test_user")
    @role_required(["user", "admin"])
    def test_user():
        return "User Access Granted"

    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.mark.parametrize("route, role, expected_status, expected_response", [
    ("/test_admin", "admin", 200, b"Admin Access Granted"),
    ("/test_user", "user", 200, b"User Access Granted"),
    ("/test_user", "admin", 200, b"User Access Granted"),
    ("/test_admin", "user", 403, None),
    ("/test_user", "guest", 403, None),
    ("/test_admin", "invalid_role", 403, None),
])
def test_role_required_access(client, route, role, expected_status, expected_response):
    with client.session_transaction() as sess:
        sess["user_role"] = role  # 🔑 esta es la clave
    response = client.get(route)
    assert response.status_code == expected_status
    if expected_response:
        assert response.data == expected_response

def test_role_required_no_role(client):
    response = client.get("/test_admin")
    assert response.status_code == 403
