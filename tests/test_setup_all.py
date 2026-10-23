import pytest
from unittest.mock import patch

from src.provisioning.setup_all import parse_args, run_unified_setup

def test_setup_all_arg_parser():
    args = parse_args(["--skip-pdfs", "--skip-search", "--skip-bigquery", "--wait"])
    assert args.skip_pdfs is True
    assert args.skip_search is True
    assert args.skip_bigquery is True
    assert args.wait is True

def test_run_unified_setup_all_skipped(capsys):
    run_unified_setup(skip_pdfs=True, skip_search=True, skip_bigquery=True)
    captured = capsys.readouterr()
    assert "Skipping PDF generation" in captured.out
    assert "Skipping Discovery Engine setup" in captured.out
    assert "Skipping BigQuery seeding" in captured.out

@patch("src.provisioning.setup_all.generate_all_equipment_docs")
@patch("src.provisioning.setup_all.setup_discovery_engine_pipeline")
@patch("src.provisioning.setup_all.seed_bigquery_billing_table")
def test_run_unified_setup_calls_steps(mock_seed, mock_search, mock_pdfs):
    mock_pdfs.return_value = ["doc1.pdf", "doc2.pdf"]
    mock_search.return_value = {"uploaded_files": ["doc1.pdf"], "datastore_path": "projects/123/locations/global/collections/default_collection/dataStores/ds-1"}
    mock_seed.return_value = {"total_rows_seeded": 10, "job_id": "job-123"}

    run_unified_setup(skip_pdfs=False, skip_search=False, skip_bigquery=False)
    assert mock_pdfs.called
    assert mock_search.called
    assert mock_seed.called
