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

def test_role_required_admin_access(client):
    with client.session_transaction() as sess:
        sess["role"] = "admin"
    response = client.get("/test_admin")
    assert response.status_code == 200
    assert response.data == b"Admin Access Granted"

def test_role_required_user_access(client):
    with client.session_transaction() as sess:
        sess["role"] = "user"
    response = client.get("/test_user")
    assert response.status_code == 200
    assert response.data == b"User Access Granted"

def test_role_required_forbidden(client):
    with client.session_transaction() as sess:
        sess["role"] = "guest"
    response = client.get("/test_admin")
    assert response.status_code == 403

def test_role_required_no_role(client):
    response = client.get("/test_admin")
    assert response.status_code == 403
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

        @app.route("/test_guest")
        @role_required(["guest"])
        def test_guest():
            return "Guest Access Granted"

        return app

    @pytest.fixture
    def client(app):
        return app.test_client()

    def test_role_required_admin_access(client):
        with client.session_transaction() as sess:
            sess["role"] = "admin"
        response = client.get("/test_admin")
        assert response.status_code == 200
        assert response.data == b"Admin Access Granted"

    def test_role_required_user_access(client):
        with client.session_transaction() as sess:
            sess["role"] = "user"
        response = client.get("/test_user")
        assert response.status_code == 200
        assert response.data == b"User Access Granted"

    def test_role_required_guest_access(client):
        with client.session_transaction() as sess:
            sess["role"] = "guest"
        response = client.get("/test_guest")
        assert response.status_code == 200
        assert response.data == b"Guest Access Granted"

    def test_role_required_forbidden_admin(client):
        with client.session_transaction() as sess:
            sess["role"] = "guest"
        response = client.get("/test_admin")
        assert response.status_code == 403

    def test_role_required_forbidden_user(client):
        with client.session_transaction() as sess:
            sess["role"] = "guest"
        response = client.get("/test_user")
        assert response.status_code == 403

    def test_role_required_no_role(client):
        response = client.get("/test_admin")
        assert response.status_code == 403

    def test_role_required_invalid_role(client):
        with client.session_transaction() as sess:
            sess["role"] = "invalid_role"
        response = client.get("/test_admin")
        assert response.status_code == 403
