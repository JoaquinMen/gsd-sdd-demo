"""Root agent builder and module-level agent export for Cimbal SA."""
import logging
from google.auth.credentials import Credentials
from google.adk.agents import LlmAgent

from src.agent.config import AppConfig
from src.agent.prompts import build_system_prompt
from src.agent.tools.search_tool import build_search_tool
from src.agent.tools.billing_tool import build_billing_tool

logger = logging.getLogger("cimbal.agent")

def build_root_agent(
    config: AppConfig, credentials: Credentials | None = None
) -> LlmAgent:
    """Builds and configures the single-agent router for Cimbal SA.
    
    Binds both unstructured VertexAiSearchTool (with bypass_multi_tools_limit=True)
    and structured BigQueryToolset (with WriteMode.BLOCKED).
    Ensures model endpoint is directed to Vertex AI 'global' publisher location.
    """
    search_tool = build_search_tool(config)
    billing_tool = build_billing_tool(config, credentials=credentials)
    instruction = build_system_prompt(config)

    agent = LlmAgent(
        name="cimbal_operations_agent",
        description="Unified operations assistant for Cimbal SA agricultural equipment intelligence.",
        model=config.gemini_model,
        instruction=instruction,
        tools=[search_tool, billing_tool],
    )

    # Route Vertex AI Gemini foundation model calls to the 'global' publisher endpoint
    if hasattr(agent, "canonical_model") and agent.canonical_model is not None:
        agent.canonical_model.client_kwargs = {"location": "global"}

    return agent

# Export module-level root_agent when valid environment configuration is present
try:
    _cfg = AppConfig.from_env()
    root_agent = build_root_agent(_cfg)
except Exception as e:
    logger.debug("Deferred module-level root_agent initialization: %s", e)
    root_agent = None
