"""BigQuery analytics toolset builder for Cimbal SA equipment service billing."""
import google.auth
from google.auth.credentials import Credentials
from google.adk.integrations.bigquery import BigQueryToolset, BigQueryCredentialsConfig
from google.adk.integrations.bigquery.config import BigQueryToolConfig, WriteMode
from src.agent.config import AppConfig

def build_billing_tool(
    config: AppConfig, credentials: Credentials | None = None
) -> BigQueryToolset:
    """Builds BigQueryToolset configured with WriteMode.BLOCKED for read-only security.
    
    Guarantees no DML/DDL (INSERT, UPDATE, DELETE, DROP) can be executed by the agent runtime.
    """
    if credentials is None:
        credentials, _ = google.auth.default()

    credentials_config = BigQueryCredentialsConfig(credentials=credentials)
    tool_config = BigQueryToolConfig(
        write_mode=WriteMode.BLOCKED,
        default_project_id=config.project_id,
        default_dataset_id=config.bq_dataset_id,
        location=config.location,
    )
    return BigQueryToolset(
        credentials_config=credentials_config,
        bigquery_tool_config=tool_config,
    )
