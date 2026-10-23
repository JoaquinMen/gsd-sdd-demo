import pytest
from unittest.mock import MagicMock, patch
from src.provisioning.setup_discovery_engine import setup_discovery_engine_pipeline

def test_setup_discovery_engine_pipeline(tmp_path):
    # Create sample docs in tmp_path
    doc1 = tmp_path / "equipment_warranty_guidelines.pdf"
    doc1.write_bytes(b"%PDF-1.4 mock content")
    
    with patch("src.provisioning.setup_discovery_engine.storage.Client") as mock_storage_cls, \
         patch("src.provisioning.setup_discovery_engine.discoveryengine.DataStoreServiceClient") as mock_ds_cls, \
         patch("src.provisioning.setup_discovery_engine.discoveryengine.DocumentServiceClient") as mock_doc_cls:
        
        mock_storage_client = MagicMock()
        mock_storage_cls.return_value = mock_storage_client
        mock_bucket = MagicMock()
        mock_storage_client.bucket.return_value = mock_bucket
        mock_storage_client.get_bucket.return_value = mock_bucket
        
        mock_ds_client = MagicMock()
        mock_ds_cls.return_value = mock_ds_client
        mock_ds_client.get_data_store.return_value = MagicMock()
        
        mock_doc_client = MagicMock()
        mock_doc_cls.return_value = mock_doc_client
        mock_operation = MagicMock()
        mock_doc_client.import_documents.return_value = mock_operation
        
        result = setup_discovery_engine_pipeline(
            project_id="test-project",
            location="us-central1",
            bucket_name="test-bucket",
            datastore_id="test-ds",
            docs_dir=str(tmp_path),
            wait_for_import=False
        )
        
        assert result["bucket_name"] == "test-bucket"
        assert result["datastore_id"] == "test-ds"
        assert mock_bucket.blob.called
        assert mock_doc_client.import_documents.called
