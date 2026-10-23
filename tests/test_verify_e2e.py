import pytest
from unittest.mock import MagicMock, patch
from src.provisioning.verify_e2e import (
    parse_args,
    verify_bigquery_table,
    verify_discovery_engine,
    verify_healthz_endpoint,
    run_e2e_verification,
)

def test_verify_e2e_parse_args():
    args = parse_args(["--project", "test-project", "--url", "http://localhost:8080", "--skip-agent"])
    assert args.project == "test-project"
    assert args.url == "http://localhost:8080"
    assert args.skip_agent is True

def test_verify_bigquery_table_success():
    mock_client = MagicMock()
    mock_table = MagicMock()
    mock_table.num_rows = 25
    expected_cols = [
        "entry_id", "service_date", "equipment_model", "customer_name",
        "technician_name", "dealership_region", "labor_hours", "hourly_rate_usd",
        "parts_cost_usd", "is_warranty_claim", "task_category", "technician_notes"
    ]
    mock_fields = []
    for c in expected_cols:
        f = MagicMock()
        f.name = c
        mock_fields.append(f)
    mock_table.schema = mock_fields
    mock_client.get_table.return_value = mock_table

    result = verify_bigquery_table(
        client=mock_client,
        project_id="test-proj",
        dataset_id="test_ds",
        table_id="test_tbl",
    )
    assert result["success"] is True
    assert result["row_count"] == 25
    assert "entry_id" in result["columns"]

def test_verify_discovery_engine_success():
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_result = MagicMock()
    mock_result.document.derived_struct_data = {"title": "Warranty Guidelines"}
    mock_response.results = [mock_result]
    mock_client.search.return_value = mock_response

    result = verify_discovery_engine(
        client=mock_client,
        datastore_path="projects/123/locations/global/collections/default_collection/dataStores/ds-1",
        query="harvest emergency multiplier",
    )
    assert result["success"] is True
    assert result["hits"] == 1

def test_verify_healthz_endpoint_success():
    with patch("httpx.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"status": "ok"}
        mock_get.return_value = mock_resp

        result = verify_healthz_endpoint("http://localhost:8080/healthz")
        assert result["success"] is True
        assert result["status_code"] == 200

def test_run_e2e_verification_flow():
    with patch("src.provisioning.verify_e2e.verify_bigquery_table") as mock_bq, \
         patch("src.provisioning.verify_e2e.verify_discovery_engine") as mock_search, \
         patch("src.provisioning.verify_e2e.verify_healthz_endpoint") as mock_health:
        
        mock_bq.return_value = {"success": True, "row_count": 21, "columns": ["entry_id"]}
        mock_search.return_value = {"success": True, "hits": 3}
        mock_health.return_value = {"success": True, "status_code": 200}

        args = parse_args(["--project", "test-proj", "--skip-agent"])
        results = run_e2e_verification(args)
        assert results["overall_pass"] is True
