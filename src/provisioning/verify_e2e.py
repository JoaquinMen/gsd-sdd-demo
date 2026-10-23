"""Live end-to-end verification and diagnostic smoke test CLI for Cimbal SA."""
import os
import sys
import argparse
import time
from typing import Any
import httpx
from dotenv import load_dotenv

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Cimbal SA End-to-End Live Verification Suite")
    parser.add_argument("--project", default=os.getenv("GOOGLE_CLOUD_PROJECT", "cimbal-ag-prod"), help="GCP Project ID")
    parser.add_argument("--location", default=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"), help="GCP Region")
    parser.add_argument("--dataset", default=os.getenv("BQ_DATASET_ID", "cimbal_operations"), help="BigQuery Dataset ID")
    parser.add_argument("--table", default=os.getenv("BQ_TABLE_ID", "equipment_service_billing"), help="BigQuery Table ID")
    parser.add_argument("--datastore", default=os.getenv("VERTEX_SEARCH_DATASTORE_ID", "cimbal-equipment-policies-ds"), help="Discovery Engine DataStore ID")
    parser.add_argument("--url", default="http://localhost:8080/healthz", help="Agent service URL for health check")
    parser.add_argument("--skip-agent", action="store_true", help="Skip agent LLM roundtrip probe")
    return parser

def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    return build_parser().parse_args(args)

def verify_bigquery_table(
    client: Any, project_id: str, dataset_id: str, table_id: str
) -> dict[str, Any]:
    """Probes BigQuery table existence, schema compliance, and row count."""
    table_ref = f"{project_id}.{dataset_id}.{table_id}"
    try:
        table = client.get_table(table_ref)
        columns = [field.name for field in table.schema]
        expected_columns = [
            "entry_id", "service_date", "equipment_model", "customer_name",
            "technician_name", "dealership_region", "labor_hours", "hourly_rate_usd",
            "parts_cost_usd", "is_warranty_claim", "task_category", "technician_notes"
        ]
        missing_columns = [c for c in expected_columns if c not in columns]
        
        return {
            "success": len(missing_columns) == 0 and table.num_rows > 0,
            "table": table_ref,
            "row_count": table.num_rows,
            "columns": columns,
            "missing_columns": missing_columns,
        }
    except Exception as exc:
        return {
            "success": False,
            "table": table_ref,
            "error": str(exc),
        }

def verify_discovery_engine(
    client: Any, datastore_path: str, query: str = "warranty harvest emergency 1.5x"
) -> dict[str, Any]:
    """Probes Discovery Engine DataStore for document retrieval."""
    try:
        serving_config = f"{datastore_path}/servingConfigs/default_search"
        request = {
            "serving_config": serving_config,
            "query": query,
            "page_size": 3,
        }
        response = client.search(request)
        hits = len(list(response.results))
        return {
            "success": hits > 0,
            "datastore_path": datastore_path,
            "hits": hits,
            "query": query,
        }
    except Exception as exc:
        return {
            "success": False,
            "datastore_path": datastore_path,
            "error": str(exc),
        }

def verify_healthz_endpoint(url: str) -> dict[str, Any]:
    """Probes Cloud Run / FastAPI /healthz endpoint."""
    try:
        resp = httpx.get(url, timeout=5.0)
        return {
            "success": resp.status_code == 200,
            "status_code": resp.status_code,
            "url": url,
            "payload": resp.json() if resp.status_code == 200 else None,
        }
    except Exception as exc:
        return {
            "success": False,
            "url": url,
            "error": str(exc),
        }

def run_e2e_verification(args: argparse.Namespace) -> dict[str, Any]:
    """Runs all verification probes and outputs formatted diagnostic results."""
    print("================================================================================")
    print("CIMBAL SA - End-to-End Environment & Infrastructure Verification Suite")
    print(f"Target: Project={args.project} | URL={args.url}")
    print("================================================================================")

    results = {}
    overall_pass = True

    # 1. BigQuery Table Probe
    print("\n[Probe 1/3] Verifying BigQuery Warehouse Schema & Seeding...")
    try:
        from google.cloud import bigquery
        bq_client = bigquery.Client(project=args.project)
        bq_res = verify_bigquery_table(bq_client, args.project, args.dataset, args.table)
    except Exception as e:
        bq_res = {"success": False, "error": str(e)}

    results["bigquery"] = bq_res
    if bq_res["success"]:
        print(f"  ✓ PASS: Table {args.dataset}.{args.table} verified ({bq_res.get('row_count')} rows)")
    else:
        print(f"  ✗ FAIL: {bq_res.get('error', 'Missing columns or empty table')}")
        overall_pass = False

    # 2. Discovery Engine Search Probe
    print("\n[Probe 2/3] Verifying Vertex AI Search / Discovery Engine DataStore...")
    try:
        from google.cloud import discoveryengine_v1 as discoveryengine
        ds_client = discoveryengine.SearchServiceClient()
        ds_path = (
            f"projects/{args.project}/locations/global/collections/default_collection/"
            f"dataStores/{args.datastore}"
        )
        ds_res = verify_discovery_engine(ds_client, ds_path)
    except Exception as e:
        ds_res = {"success": False, "error": str(e)}

    results["discovery_engine"] = ds_res
    if ds_res["success"]:
        print(f"  ✓ PASS: DataStore {args.datastore} returned {ds_res.get('hits')} document hits")
    else:
        print(f"  ✗ FAIL: {ds_res.get('error', 'Search request failed')}")
        overall_pass = False

    # 3. Endpoint Health Probe
    print(f"\n[Probe 3/3] Verifying Cloud Run / FastAPI Service ({args.url})...")
    health_res = verify_healthz_endpoint(args.url)
    results["healthz"] = health_res
    if health_res["success"]:
        print(f"  ✓ PASS: Endpoint active (HTTP {health_res['status_code']})")
    else:
        print(f"  ✗ FAIL: Endpoint unreachable ({health_res.get('error')})")
        overall_pass = False

    results["overall_pass"] = overall_pass
    print("\n================================================================================")
    if overall_pass:
        print("OVERALL VERIFICATION: PASS (All core infrastructure verified)")
    else:
        print("OVERALL VERIFICATION: INCOMPLETE (Review failed probes above)")
    print("================================================================================")
    return results

def main():
    load_dotenv()
    args = parse_args()
    results = run_e2e_verification(args)
    if not results["overall_pass"]:
        sys.exit(1)

if __name__ == "__main__":
    main()
