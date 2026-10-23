import pytest
from unittest.mock import MagicMock
from google.auth.credentials import Credentials
from google.adk.tools import VertexAiSearchTool
from google.adk.integrations.bigquery import BigQueryToolset
from google.adk.integrations.bigquery.config import WriteMode

from src.agent.config import AppConfig
from src.agent.tools.search_tool import build_search_tool
from src.agent.tools.billing_tool import build_billing_tool

class MockCredentials(Credentials):
    def refresh(self, request):
        pass

@pytest.fixture
def mock_config():
    return AppConfig(
        project_id="cimbal-test-project",
        location="us-central1",
        use_vertexai=True,
        gemini_model="gemini-3.5-flash",
        bq_dataset_id="cimbal_operations",
        bq_table_id="equipment_service_billing",
        gcs_docs_bucket="cimbal-docs",
        vertex_search_location="global",
        vertex_search_datastore_id="cimbal-equipment-policies-ds",
        iap_enabled=True,
        iap_bypass_dev=False,
        iap_audience="/projects/123/locations/us-central1/services/cimbal-agent",
        port=8080,
    )

def test_build_search_tool(mock_config):
    tool = build_search_tool(mock_config)
    assert isinstance(tool, VertexAiSearchTool)
    assert tool.bypass_multi_tools_limit is True
    assert tool.data_store_id == mock_config.vertex_search_datastore_path

def test_build_billing_tool_with_credentials(mock_config):
    creds = MockCredentials()
    toolset = build_billing_tool(mock_config, credentials=creds)
    assert isinstance(toolset, BigQueryToolset)
    assert toolset._tool_settings.write_mode == WriteMode.BLOCKED
    assert toolset._tool_settings.default_project_id == mock_config.project_id
    assert toolset._tool_settings.default_dataset_id == mock_config.bq_dataset_id

def test_build_billing_tool_default_adc(mock_config, monkeypatch):
    creds = MockCredentials()
    monkeypatch.setattr("google.auth.default", lambda: (creds, "mock-project"))
    toolset = build_billing_tool(mock_config)
    assert isinstance(toolset, BigQueryToolset)
    assert toolset._tool_settings.write_mode == WriteMode.BLOCKED
