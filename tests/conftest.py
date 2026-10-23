"""Pytest configuration, environment fixtures, and mocks for Cimbal SA test suite."""
import os
import pytest
from google.auth.credentials import Credentials

from src.agent.config import AppConfig

@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Sets standard mock environment variables for test isolation."""
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "cimbal-operations-prod")
    monkeypatch.setenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    monkeypatch.setenv("GOOGLE_GENAI_USE_VERTEXAI", "TRUE")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-3.5-flash")
    monkeypatch.setenv("BQ_DATASET_ID", "cimbal_operations")
    monkeypatch.setenv("BQ_TABLE_ID", "equipment_service_billing")
    monkeypatch.setenv("GCS_DOCS_BUCKET", "cimbal-operations-prod-equipment-docs")
    monkeypatch.setenv("VERTEX_SEARCH_LOCATION", "global")
    monkeypatch.setenv("VERTEX_SEARCH_DATASTORE_ID", "cimbal-equipment-policies-ds")
    monkeypatch.setenv("IAP_ENABLED", "TRUE")
    monkeypatch.setenv("IAP_BYPASS_DEV", "TRUE")
    monkeypatch.setenv("IAP_AUDIENCE", "/projects/123/locations/us-central1/services/cimbal-agent")
    monkeypatch.setenv("PORT", "8080")

class MockCredentials(Credentials):
    """Reusable mock credentials for Google Cloud services."""
    def refresh(self, request):
        pass

@pytest.fixture
def mock_credentials():
    return MockCredentials()

@pytest.fixture
def test_app_config():
    return AppConfig.from_env()
