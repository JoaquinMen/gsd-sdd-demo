"""Vertex AI Search tool builder for Cimbal SA policy corpus."""
from google.adk.tools import VertexAiSearchTool
from src.agent.config import AppConfig

def build_search_tool(config: AppConfig) -> VertexAiSearchTool:
    """Builds VertexAiSearchTool configured with bypass_multi_tools_limit=True.
    
    This enables concurrent multi-tool function calling alongside BigQueryToolset
    without triggering Vertex AI Gemini's multi-tool grounding constraint.
    """
    return VertexAiSearchTool(
        data_store_id=config.vertex_search_datastore_path,
        bypass_multi_tools_limit=True,
    )
