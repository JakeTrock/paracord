import json

import pytest

from app import app
from fastapi.testclient import TestClient


client = TestClient(app.app)

#tests all enclave routes exist
def test_enclave_routes():
    response = client.get("/Enclave/fake/")
    assert response.status_code != 404
    response = client.post("/Enclave")
    assert response.status_code != 404
    response = client.patch("/Enclave/fake/")
    assert response.status_code != 404
    response = client.delete("/Enclave/fake/")
    assert response.status_code != 404

#tests all shard routes exist
def test_shard_routes():
    response = client.get("/Shards/fake/")
    assert response.status_code != 404
    response = client.post("/Shard")
    assert response.status_code != 404
    response = client.patch("/Shard/fake/")
    assert response.status_code != 404
    response = client.delete("/Shard/fake/")
    assert response.status_code != 404

