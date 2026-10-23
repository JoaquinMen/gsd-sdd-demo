import os
import argparse
import sys
from dotenv import load_dotenv

from src.provisioning.generate_documents import generate_all_equipment_docs
from src.provisioning.setup_discovery_engine import setup_discovery_engine_pipeline
from src.provisioning.seed_warehouse import seed_bigquery_billing_table

def run_unified_setup(
    skip_pdfs: bool = False,
    skip_search: bool = False,
    skip_bigquery: bool = False,
    wait: bool = False,
    docs_dir: str = "data/equipment_docs",
    days_back: int = 21
):
    load_dotenv()
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "cimbal-ag-prod")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    bucket_name = os.getenv("GCS_DOCS_BUCKET", f"{project_id}-equipment-docs")
    datastore_id = os.getenv("VERTEX_SEARCH_DATASTORE_ID", "cimbal-equipment-policies-ds")
    bq_dataset_id = os.getenv("BQ_DATASET_ID", "cimbal_operations")
    bq_table_id = os.getenv("BQ_TABLE_ID", "equipment_service_billing")

    print("================================================================================")
    print("CIMBAL SA - Unified Infrastructure & Data Provisioning Pipeline")
    print(f"Target Project: {project_id} | Location: {location}")
    print("================================================================================")

    if not skip_pdfs:
        print("\n[Step 1/3] Generating Cimbal SA equipment policy & manual PDFs...")
        pdfs = generate_all_equipment_docs(output_dir=docs_dir)
        for p in pdfs:
            print(f"  ✓ Created: {p}")
    else:
        print("\n[Step 1/3] Skipping PDF generation (--skip-pdfs).")

    if not skip_search:
        print(f"\n[Step 2/3] Staging PDFs to gs://{bucket_name} and indexing in DataStore '{datastore_id}'...")
        res_search = setup_discovery_engine_pipeline(
            project_id=project_id,
            location=location,
            bucket_name=bucket_name,
            datastore_id=datastore_id,
            docs_dir=docs_dir,
            wait_for_import=wait
        )
        print(f"  ✓ GCS Bucket & Docs staged: {len(res_search['uploaded_files'])} files")
        print(f"  ✓ Discovery Engine DataStore: {res_search['datastore_path']}")
    else:
        print("\n[Step 2/3] Skipping Discovery Engine setup (--skip-search).")

    if not skip_bigquery:
        print(f"\n[Step 3/3] Seeding BigQuery table {project_id}.{bq_dataset_id}.{bq_table_id}...")
        res_bq = seed_bigquery_billing_table(
            project_id=project_id,
            dataset_id=bq_dataset_id,
            table_id=bq_table_id,
            location=location,
            days_back=days_back,
            wait_for_job=wait
        )
        print(f"  ✓ Seeded {res_bq['total_rows_seeded']} service billing rows (Job ID: {res_bq['job_id']})")
    else:
        print("\n[Step 3/3] Skipping BigQuery seeding (--skip-bigquery).")

    print("\n================================================================================")
    print("Provisioning pipeline completed successfully.")
    print("================================================================================")

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Cimbal SA Master Data & Infrastructure Provisioning CLI")
    parser.add_argument("--wait", action="store_true", help="Wait for asynchronous cloud operations to complete")
    parser.add_argument("--skip-pdfs", action="store_true", help="Skip local PDF generation")
    parser.add_argument("--skip-search", action="store_true", help="Skip Cloud Storage and Vertex AI Search setup")
    parser.add_argument("--skip-bigquery", action="store_true", help="Skip BigQuery dataset/table creation and seeding")
    parser.add_argument("--docs-dir", default="data/equipment_docs", help="Directory for generated PDF documents")
    parser.add_argument("--days-back", type=int, default=21, help="Number of rolling days of synthetic billing logs to seed")
    return parser

def parse_args(args=None) -> argparse.Namespace:
    return build_parser().parse_args(args)

def main():
    args = parse_args()
    run_unified_setup(
        skip_pdfs=args.skip_pdfs,
        skip_search=args.skip_search,
        skip_bigquery=args.skip_bigquery,
        wait=args.wait,
        docs_dir=args.docs_dir,
        days_back=args.days_back
    )

if __name__ == "__main__":
    main()
