"""
Beginner-friendly tests for the FastAPI /chat endpoint.

How these tests help:
- They verify your API returns the expected JSON shape.
- They verify errors are handled correctly (HTTP 500).
- They avoid real Azure/OpenAI calls by mocking `run_agent`.
"""

from fastapi.testclient import TestClient

# Import the FastAPI app object from your project
from app.main import app


def test_chat_endpoint_success(monkeypatch):
    """
    Test the happy path:
    - client sends session_id + message
    - mocked agent returns a fake response
    - API should return 200 with session_id and response
    """

    async def fake_run_agent(_messages):
        return "Hello from mocked agent"

    # Replace real run_agent with fake one for this test only
    monkeypatch.setattr("app.main.run_agent", fake_run_agent)

    client = TestClient(app)
    payload = {"session_id": "test-session-1", "message": "Hi"}

    response = client.post("/chat", json=payload)

    assert response.status_code == 200
    assert response.json() == {
        "session_id": "test-session-1",
        "response": "Hello from mocked agent",
    }


def test_chat_endpoint_returns_500_on_agent_error(monkeypatch):
    """
    Test error path:
    - mocked agent raises an exception
    - API should catch it and return HTTP 500
    """

    async def fake_run_agent_raises(_messages):
        raise RuntimeError("Agent failed")

    monkeypatch.setattr("app.main.run_agent", fake_run_agent_raises)

    client = TestClient(app)
    payload = {"session_id": "test-session-2", "message": "Hi"}

    response = client.post("/chat", json=payload)

    assert response.status_code == 500
    assert response.json()["detail"] == "Agent failed"


def test_chat_endpoint_validation_error():
    """
    Test request validation:
    - session_id is required by ChatRequest schema
    - missing it should return 422 (validation error)
    """

    client = TestClient(app)

    # Intentionally missing `session_id`
    response = client.post("/chat", json={"message": "Hi"})

    assert response.status_code == 422
