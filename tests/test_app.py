import json
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from google.genai import types
from google.adk.events import Event

from src.agent.config import AppConfig
from src.agent.main import create_app

@pytest.fixture
def test_config():
    return AppConfig(
        project_id="test-cimbal-project",
        location="us-central1",
        use_vertexai=True,
        gemini_model="gemini-3.5-flash",
        bq_dataset_id="cimbal_operations",
        bq_table_id="equipment_service_billing",
        gcs_docs_bucket="cimbal-docs",
        vertex_search_location="global",
        vertex_search_datastore_id="cimbal-equipment-policies-ds",
        iap_enabled=True,
        iap_bypass_dev=True,
        iap_audience=None,
        port=8080,
    )

@pytest.fixture
def mock_runner():
    runner = MagicMock()
    runner.app_name = "test_app"
    runner.session_service = AsyncMock()
    runner.session_service.get_session.return_value = None
    runner.session_service.create_session.return_value = MagicMock(id="session-1")

    # Mock run_async as an async generator
    async def mock_run_async(*args, **kwargs):
        part1 = types.Part.from_text(text="Harvest emergency rate ")
        event1 = Event(message=types.Content(role="model", parts=[part1]))
        part2 = types.Part.from_text(text="is 1.5x according to warranty guidelines.")
        event2 = Event(message=types.Content(role="model", parts=[part2]))
        yield event1
        yield event2

    runner.run_async = mock_run_async
    return runner

def test_healthz_endpoint(test_config, mock_runner):
    app = create_app(config=test_config, runner=mock_runner)
    client = TestClient(app)

    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["project"] == test_config.project_id

def test_root_frontend_endpoint(test_config, mock_runner):
    app = create_app(config=test_config, runner=mock_runner)
    client = TestClient(app)

    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Cimbal SA" in response.text
    assert "dev-engineer@cimbal.com" in response.text

def test_chat_stream_endpoint(test_config, mock_runner):
    app = create_app(config=test_config, runner=mock_runner)
    client = TestClient(app)

    payload = {"prompt": "What is the emergency labor multiplier?"}
    response = client.post("/api/v1/chat/stream", json=payload)
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]

    lines = [line.strip() for line in response.text.split("\n") if line.strip()]
    assert any("Harvest emergency rate" in line for line in lines)
    assert any("[DONE]" in line for line in lines)

def test_iap_unauthorized_when_not_bypassed():
    prod_config = AppConfig(
        project_id="test-cimbal-project",
        location="us-central1",
        use_vertexai=True,
        gemini_model="gemini-3.5-flash",
        bq_dataset_id="cimbal_operations",
        bq_table_id="equipment_service_billing",
        gcs_docs_bucket="cimbal-docs",
        vertex_search_location="global",
        vertex_search_datastore_id="cimbal-equipment-policies-ds",
        iap_enabled=True,
        iap_bypass_dev=False,  # Enforce strict IAP
        iap_audience="/projects/123/locations/us-central1/services/cimbal-agent",
        port=8080,
    )
    mock_runner = MagicMock()
    app = create_app(config=prod_config, runner=mock_runner)
    client = TestClient(app)

    # Missing IAP header in production should reject root
    response = client.get("/")
    assert response.status_code == 401
    assert "Missing IAP assertion" in response.json()["detail"]
