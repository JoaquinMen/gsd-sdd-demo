import pytest
from google.auth.credentials import Credentials
from google.adk.agents import LlmAgent

from src.agent.config import AppConfig
from src.agent.prompts import build_system_prompt
from src.agent.agent import build_root_agent

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
        iap_bypass_dev=True,
        iap_audience=None,
        port=8080,
    )

def test_build_system_prompt(mock_config):
    prompt = build_system_prompt(mock_config)
    assert isinstance(prompt, str)
    assert mock_config.bq_table_fqn in prompt
    assert "labor_hours" in prompt
    assert "hourly_rate_usd" in prompt
    assert "parts_cost_usd" in prompt
    assert "is_warranty_claim" in prompt
    assert "1.5x" in prompt or "1.5" in prompt
    assert "warranty" in prompt.lower()
    assert "manuals" in prompt.lower()

def test_build_root_agent(mock_config):
    creds = MockCredentials()
    agent = build_root_agent(mock_config, credentials=creds)
    assert isinstance(agent, LlmAgent)
    assert agent.name == "cimbal_operations_agent"
    assert agent.model == mock_config.gemini_model
    assert len(agent.tools) == 2
    assert hasattr(agent, "canonical_model")
    assert agent.canonical_model.client_kwargs.get("location") == "global"
