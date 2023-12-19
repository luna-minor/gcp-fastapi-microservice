"""Unit test Health Check endpoint"""

import pytest
from config.service_config import SERVICE_CONFIG
from fastapi.testclient import TestClient
from main import app


@pytest.fixture(scope="module")
def test_client() -> TestClient:
    return TestClient(app)


def test_healthcheck_endpoint(test_client):
    response = test_client.get(SERVICE_CONFIG.HEALTH_CHECK_ROUTE)
    assert response.status_code == 200
    assert response.json() == {"message": "Service is up", "status": "OK"}
