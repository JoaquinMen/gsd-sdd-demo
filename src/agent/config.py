import os
import certifi
from dataclasses import dataclass
from dotenv import load_dotenv

def _ensure_ssl_cert_file() -> str:
    """Ensure SSL_CERT_FILE and REQUESTS_CA_BUNDLE point to a valid root CA bundle."""
    existing = os.getenv("SSL_CERT_FILE")
    if existing and os.path.exists(existing):
        os.environ["REQUESTS_CA_BUNDLE"] = existing
        return existing
        
    system_cas = [
        "/etc/ssl/certs/ca-certificates.crt",
        "/etc/ssl/cert.pem",
        certifi.where()
    ]
    for ca in system_cas:
        if os.path.exists(ca):
            os.environ["SSL_CERT_FILE"] = ca
            os.environ["REQUESTS_CA_BUNDLE"] = ca
            return ca
            
    cert_path = certifi.where()
    os.environ["SSL_CERT_FILE"] = cert_path
    os.environ["REQUESTS_CA_BUNDLE"] = cert_path
    return cert_path

@dataclass(frozen=True)
class AppConfig:
    project_id: str
    location: str
    use_vertexai: bool
    gemini_model: str
    bq_dataset_id: str
    bq_table_id: str
    gcs_docs_bucket: str
    vertex_search_location: str
    vertex_search_datastore_id: str
    iap_enabled: bool
    iap_bypass_dev: bool
    iap_audience: str | None
    port: int

    @property
    def bq_table_fqn(self) -> str:
        return f"{self.project_id}.{self.bq_dataset_id}.{self.bq_table_id}"

    @property
    def vertex_search_datastore_path(self) -> str:
        return (
            f"projects/{self.project_id}/locations/{self.vertex_search_location}/"
            f"collections/default_collection/dataStores/{self.vertex_search_datastore_id}"
        )

    @classmethod
    def from_env(cls) -> "AppConfig":
        load_dotenv()
        _ensure_ssl_cert_file()

        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        if not project_id:
            raise ValueError("Environment variable GOOGLE_CLOUD_PROJECT is required.")

        return cls(
            project_id=project_id,
            location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
            use_vertexai=os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "TRUE").upper() == "TRUE",
            gemini_model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash"),
            bq_dataset_id=os.getenv("BQ_DATASET_ID", "cimbal_operations"),
            bq_table_id=os.getenv("BQ_TABLE_ID", "equipment_service_billing"),
            gcs_docs_bucket=os.getenv("GCS_DOCS_BUCKET", f"{project_id}-equipment-docs"),
            vertex_search_location=os.getenv("VERTEX_SEARCH_LOCATION", "global"),
            vertex_search_datastore_id=os.getenv("VERTEX_SEARCH_DATASTORE_ID", "cimbal-equipment-policies-ds"),
            iap_enabled=os.getenv("IAP_ENABLED", "TRUE").upper() == "TRUE",
            iap_bypass_dev=os.getenv("IAP_BYPASS_DEV", "FALSE").upper() == "TRUE",
            iap_audience=os.getenv("IAP_AUDIENCE"),
            port=int(os.getenv("PORT", "8080"))
        )
