import os
from pathlib import Path
from google.cloud import storage
from google.cloud import discoveryengine_v1 as discoveryengine
from google.api_core.exceptions import NotFound, AlreadyExists

def ensure_gcs_bucket_and_upload_docs(
    project_id: str,
    location: str,
    bucket_name: str,
    docs_dir: str = "data/equipment_docs"
) -> list[str]:
    storage_client = storage.Client(project=project_id)
    
    try:
        bucket = storage_client.get_bucket(bucket_name)
    except NotFound:
        bucket = storage_client.create_bucket(bucket_name, location=location)
    
    uploaded_uris = []
    p = Path(docs_dir)
    if p.exists():
        for pdf_path in p.glob("*.pdf"):
            blob = bucket.blob(pdf_path.name)
            blob.upload_from_filename(str(pdf_path), content_type="application/pdf")
            uploaded_uris.append(f"gs://{bucket_name}/{pdf_path.name}")
            
    return uploaded_uris

def ensure_vertex_search_datastore(
    project_id: str,
    location: str,
    datastore_id: str,
    display_name: str = "Cimbal Equipment Knowledge Base"
) -> str:
    client = discoveryengine.DataStoreServiceClient()
    parent = f"projects/{project_id}/locations/{location}/collections/default_collection"
    datastore_name = f"{parent}/dataStores/{datastore_id}"
    
    try:
        client.get_data_store(name=datastore_name)
    except NotFound:
        datastore = discoveryengine.DataStore(
            display_name=display_name,
            industry_vertical=discoveryengine.IndustryVertical.GENERIC,
            solution_types=[discoveryengine.SolutionType.SOLUTION_TYPE_SEARCH],
            content_config=discoveryengine.DataStore.ContentConfig.CONTENT_REQUIRED
        )
        operation = client.create_data_store(
            parent=parent,
            data_store=datastore,
            data_store_id=datastore_id
        )
        operation.result()
        
    return datastore_name

def import_docs_into_datastore(
    project_id: str,
    location: str,
    datastore_id: str,
    bucket_name: str,
    wait_for_completion: bool = False
):
    doc_client = discoveryengine.DocumentServiceClient()
    parent = (
        f"projects/{project_id}/locations/{location}/collections/default_collection/"
        f"dataStores/{datastore_id}/branches/default_branch"
    )
    
    request = discoveryengine.ImportDocumentsRequest(
        parent=parent,
        gcs_source=discoveryengine.GcsSource(
            input_uris=[f"gs://{bucket_name}/*.pdf"],
            data_schema="content"
        ),
        reconciliation_mode=discoveryengine.ImportDocumentsRequest.ReconciliationMode.INCREMENTAL
    )
    
    operation = doc_client.import_documents(request=request)
    if wait_for_completion:
        operation.result()
    return operation

def setup_discovery_engine_pipeline(
    project_id: str,
    location: str,
    bucket_name: str,
    datastore_id: str,
    docs_dir: str = "data/equipment_docs",
    wait_for_import: bool = False
) -> dict:
    uploaded = ensure_gcs_bucket_and_upload_docs(project_id, location, bucket_name, docs_dir)
    ds_path = ensure_vertex_search_datastore(project_id, location, datastore_id)
    op = import_docs_into_datastore(project_id, location, datastore_id, bucket_name, wait_for_completion=wait_for_import)
    
    return {
        "bucket_name": bucket_name,
        "datastore_id": datastore_id,
        "datastore_path": ds_path,
        "uploaded_files": uploaded,
        "operation": str(op)
    }
