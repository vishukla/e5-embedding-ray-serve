import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_get_embedding():
    response = client.get("/embeddings", params={"sentence": "The quick brown fox"})
    assert response.status_code == 200
    data = response.json()
    assert "embedding" in data
    assert isinstance(data["embedding"], list)
    assert all(isinstance(x, float) for x in data["embedding"])

def test_bulk_embeddings():
    payload = {"sentences": ["Hello world", "FastAPI testing"]}
    response = client.post("/embeddings/bulk", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "embeddings" in data
    assert isinstance(data["embeddings"], list)
    assert len(data["embeddings"]) == 2
    for emb in data["embeddings"]:
        assert isinstance(emb, list)
        assert all(isinstance(x, float) for x in emb)

def test_similarity():
    payload = {
        "sentence_1": "The quick brown fox",
        "sentence_2": "A fast dark-colored fox"
    }
    response = client.post("/embeddings/similarity", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "similarity" in data
    assert isinstance(data["similarity"], float)
    assert 0.0 <= data["similarity"] <= 1.0

def test_search():
    payload = {
        "query": "fast fox",
        "sentences": ["slow turtle", "quick brown fox", "sleepy cat"]
    }
    response = client.post("/embeddings/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "sentence" in data
    assert "similarity" in data
    assert isinstance(data["sentence"], str)
    assert isinstance(data["similarity"], float)
    assert 0.0 <= data["similarity"] <= 1.0

def test_invalid_bulk_request():
    payload = {"sentences": []}
    response = client.post("/embeddings/bulk", json=payload)
    assert response.status_code == 400

def test_invalid_similarity_request():
    payload = {"sentence_1": "hello"}
    response = client.post("/embeddings/similarity", json=payload)
    assert response.status_code == 422  # missing required field
