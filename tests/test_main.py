from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200

def test_create_task():
    response = client.post("/tasks", json={"title": "Buy milk", "description": "2% please"})
    assert response.status_code == 201
    assert response.json()["title"] == "Buy milk"

def test_list_tasks():
    response = client.get("/tasks")
    assert response.status_code == 200
    assert isinstance(response.json(), list)