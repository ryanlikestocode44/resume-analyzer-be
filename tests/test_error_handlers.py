import pytest
from flask import Flask
from werkzeug.exceptions import BadRequest, RequestEntityTooLarge
from error_handlers import register_error_handlers

@pytest.fixture
def client():
    app = Flask(__name__)
    register_error_handlers(app)

    @app.route("/badrequest")
    def bad_request():
        raise BadRequest()

    @app.route("/toolarge")
    def too_large():
        raise RequestEntityTooLarge()

    @app.route("/crash")
    def crash():
        raise Exception("Simulated crash")

    return app.test_client()

def test_400_bad_request(client):
    response = client.get("/badrequest")
    assert response.status_code == 400
    assert response.get_json()["error"] == "Permintaan tidak valid (bad request)"

def test_404_not_found(client):
    response = client.get("/nonexistent")
    assert response.status_code == 404
    assert response.get_json()["error"] == "Endpoint tidak ditemukan"

def test_500_internal_error(client):
    response = client.get("/crash")
    assert response.status_code == 500
    assert response.get_json()["error"] == "Terjadi kesalahan tak terduga"

def test_413_too_large(client):
    response = client.get("/toolarge")
    assert response.status_code == 413
    assert response.get_json()["error"] == "File terlalu besar"
