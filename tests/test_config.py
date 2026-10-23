import os
import pytest
from src.agent.config import AppConfig, _ensure_ssl_cert_file

def test_app_config_valid(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "test-cimbal-project")
    monkeypatch.setenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    monkeypatch.setenv("BQ_DATASET_ID", "test_dataset")
    monkeypatch.setenv("BQ_TABLE_ID", "test_table")
    monkeypatch.setenv("GCS_DOCS_BUCKET", "test-bucket")
    monkeypatch.setenv("VERTEX_SEARCH_DATASTORE_ID", "test-ds")
    monkeypatch.setenv("IAP_ENABLED", "TRUE")
    monkeypatch.setenv("IAP_AUDIENCE", "/projects/123/locations/us-central1/services/test-service")
    
    cfg = AppConfig.from_env()
    assert cfg.project_id == "test-cimbal-project"
    assert cfg.location == "us-central1"
    assert cfg.bq_table_fqn == "test-cimbal-project.test_dataset.test_table"
    assert "test-ds" in cfg.vertex_search_datastore_path
    assert cfg.iap_enabled is True
    assert cfg.iap_audience == "/projects/123/locations/us-central1/services/test-service"

def test_app_config_missing_required(monkeypatch):
    monkeypatch.delenv("GOOGLE_CLOUD_PROJECT", raising=False)
    with pytest.raises(ValueError, match="GOOGLE_CLOUD_PROJECT"):
        AppConfig.from_env()

def test_ensure_ssl_cert_file(monkeypatch):
    monkeypatch.delenv("SSL_CERT_FILE", raising=False)
    cert_path = _ensure_ssl_cert_file()
    assert cert_path is not None
    assert os.environ.get("SSL_CERT_FILE") is not None
