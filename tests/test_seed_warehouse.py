import datetime
import pytest
from unittest.mock import MagicMock, patch
from src.provisioning.seed_warehouse import (
    BILLING_SCHEMA,
    generate_synthetic_billing_rows,
    seed_bigquery_billing_table
)

def test_schema_has_all_required_columns():
    col_names = [f.name for f in BILLING_SCHEMA]
    expected_cols = [
        "entry_id", "service_date", "equipment_model", "customer_name",
        "technician_name", "dealership_region", "labor_hours", "hourly_rate_usd",
        "parts_cost_usd", "is_warranty_claim", "task_category", "technician_notes"
    ]
    for col in expected_cols:
        assert col in col_names, f"Expected {col} in BILLING_SCHEMA"

def test_generate_synthetic_billing_rows_dynamic_dates():
    today = datetime.date.today()
    rows = generate_synthetic_billing_rows(days_back=21, reference_date=today)
    
    assert len(rows) > 50, "Expected at least 50 synthetic service rows"
    
    dates = {r["service_date"] for r in rows}
    assert str(today) in dates or any(r["service_date"] <= str(today) for r in rows)
    
    # Check that required fields exist and are typed properly
    for row in rows:
        assert "entry_id" in row
        assert "equipment_model" in row
        assert "labor_hours" in row and isinstance(row["labor_hours"], (int, float))
        assert "is_warranty_claim" in row and isinstance(row["is_warranty_claim"], bool)
        assert "dealership_region" in row

def test_seed_bigquery_billing_table_mocked():
    with patch("src.provisioning.seed_warehouse.bigquery.Client") as mock_bq_cls:
        mock_client = MagicMock()
        mock_bq_cls.return_value = mock_client
        
        mock_job = MagicMock()
        mock_client.load_table_from_json.return_value = mock_job
        
        result = seed_bigquery_billing_table(
            project_id="test-project",
            dataset_id="cimbal_operations",
            table_id="equipment_service_billing",
            location="us-central1",
            wait_for_job=True
        )
        
        assert result["total_rows_seeded"] > 0
        assert mock_client.load_table_from_json.called
        assert mock_job.result.called
