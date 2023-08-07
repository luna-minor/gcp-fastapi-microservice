"""Unit test Health Check endpoint"""

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def test_client() -> TestClient:
    # Do something before the test
    return TestClient(app)


def test_healthcheck_endpoint(test_client):
    response = test_client.get("/healthcheck")
    assert response.status_code == 200
    assert response.json() == {"message": "Service is up", "status": "OK"}


def test_api_root(test_client):
    response = test_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Service is up", "status": "OK"}
