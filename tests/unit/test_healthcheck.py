"""Unit test Health Check endpoint"""

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture(scope="module")
def test_client() -> TestClient:
    return TestClient(app)


def test_healthcheck_endpoint(test_client):
    response = test_client.get("/healthcheck")
    assert response.status_code == 200
    assert response.json() == {"message": "Service is up", "status": "OK"}

