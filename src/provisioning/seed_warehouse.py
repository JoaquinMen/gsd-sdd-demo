import datetime
from google.cloud import bigquery
from google.api_core.exceptions import NotFound

BILLING_SCHEMA = [
    bigquery.SchemaField("entry_id", "STRING", mode="REQUIRED", description="Unique service log ID"),
    bigquery.SchemaField("service_date", "DATE", mode="REQUIRED", description="Date work was performed"),
    bigquery.SchemaField("equipment_model", "STRING", mode="REQUIRED", description="Machinery model"),
    bigquery.SchemaField("customer_name", "STRING", mode="REQUIRED", description="Farm or agribusiness client"),
    bigquery.SchemaField("technician_name", "STRING", mode="REQUIRED", description="Field technician name"),
    bigquery.SchemaField("dealership_region", "STRING", mode="REQUIRED", description="Regional dealership hub"),
    bigquery.SchemaField("labor_hours", "FLOAT", mode="REQUIRED", description="Labor hours logged"),
    bigquery.SchemaField("hourly_rate_usd", "FLOAT", mode="REQUIRED", description="Hourly labor rate in USD"),
    bigquery.SchemaField("parts_cost_usd", "FLOAT", mode="REQUIRED", description="Parts cost in USD"),
    bigquery.SchemaField("is_warranty_claim", "BOOLEAN", mode="REQUIRED", description="True if OEM warranty"),
    bigquery.SchemaField("task_category", "STRING", mode="REQUIRED", description="Work category"),
    bigquery.SchemaField("technician_notes", "STRING", mode="NULLABLE", description="Service details"),
]

TECHNICIANS = [
    {"name": "Carlos Rossi", "region": "Midwest", "rate": 140.0},
    {"name": "Sarah Jenkins", "region": "Midwest", "rate": 140.0},
    {"name": "Lucas Morales", "region": "South", "rate": 130.0},
    {"name": "Elena Vance", "region": "South", "rate": 130.0},
    {"name": "David Kim", "region": "West", "rate": 150.0},
    {"name": "Rachel Miller", "region": "West", "rate": 150.0},
]

EQUIPMENT_MODELS = [
    "Combine Harvester X9 1000",
    "Tractor 8R 410",
    "Planter ExactEmerge 24R",
    "High-Clearance Sprayer 408R"
]

FARMS = [
    "Prairie View Agro LLC",
    "Golden Wheat Farms Inc.",
    "Red River Ranch & Co.",
    "Sunbelt Cotton Growers",
    "Valley Orchard Operations"
]

CATEGORIES = [
    "Diagnostics",
    "Hydraulics",
    "Engine Overhaul",
    "Telematics",
    "Preventive Maintenance"
]

def generate_synthetic_billing_rows(
    days_back: int = 21,
    reference_date: datetime.date | None = None
) -> list[dict]:
    ref = reference_date or datetime.date.today()
    rows = []
    log_counter = 1001

    for day_offset in range(days_back, -1, -1):
        current_date = ref - datetime.timedelta(days=day_offset)
        # Skip Sundays
        if current_date.weekday() == 6:
            continue
            
        for i, tech in enumerate(TECHNICIANS):
            # Generate 1 to 2 entries per technician per working day
            eq = EQUIPMENT_MODELS[(log_counter + i) % len(EQUIPMENT_MODELS)]
            cust = FARMS[(log_counter + i * 2) % len(FARMS)]
            cat = CATEGORIES[(log_counter + i * 3) % len(CATEGORIES)]
            
            hours = 4.0 if (log_counter % 3 == 0) else 6.5
            is_warranty = (log_counter % 2 == 0)
            parts_cost = 0.0 if is_warranty else (150.0 * (log_counter % 5 + 1))
            
            notes = f"Routine service on {eq} - checked filters and hydraulic pressure."
            if cat == "Hydraulics":
                notes = "Addressed hydraulic high-pressure rail fault (DTC E-102); replaced relief valve seal."
            elif cat == "Telematics":
                notes = "Calibrated GPS auto-guidance receiver and updated ECU telematics firmware."
                
            rows.append({
                "entry_id": f"LOG-{log_counter}",
                "service_date": current_date.isoformat(),
                "equipment_model": eq,
                "customer_name": cust,
                "technician_name": tech["name"],
                "dealership_region": tech["region"],
                "labor_hours": hours,
                "hourly_rate_usd": tech["rate"],
                "parts_cost_usd": parts_cost,
                "is_warranty_claim": is_warranty,
                "task_category": cat,
                "technician_notes": notes
            })
            log_counter += 1

    # Add explicit emergency harvest weekend entries with 1.5x multiplier
    harvest_emergency_entry = {
        "entry_id": f"LOG-{log_counter}",
        "service_date": (ref - datetime.timedelta(days=5)).isoformat(),
        "equipment_model": "Combine Harvester X9 1000",
        "customer_name": "Prairie View Agro LLC",
        "technician_name": "Carlos Rossi",
        "dealership_region": "Midwest",
        "labor_hours": 8.0,
        "hourly_rate_usd": 210.0, # 140 * 1.5
        "parts_cost_usd": 1250.0,
        "is_warranty_claim": True,
        "task_category": "Hydraulics",
        "technician_notes": "Emergency harvest night repair: Hydraulic cylinder leak on main feederhouse (pre-authorized 1.5x rate)."
    }
    rows.append(harvest_emergency_entry)

    return rows

def seed_bigquery_billing_table(
    project_id: str,
    dataset_id: str,
    table_id: str,
    location: str = "us-central1",
    days_back: int = 21,
    wait_for_job: bool = True
) -> dict:
    client = bigquery.Client(project=project_id)
    dataset_ref = bigquery.DatasetReference(project_id, dataset_id)
    
    try:
        client.get_dataset(dataset_ref)
    except NotFound:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = location
        dataset.description = "Cimbal SA Agricultural Equipment Operations & Field Service Warehouse"
        client.create_dataset(dataset, exists_ok=True)
        
    table_ref = dataset_ref.table(table_id)
    table = bigquery.Table(table_ref, schema=BILLING_SCHEMA)
    table.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY,
        field="service_date"
    )
    table.clustering_fields = ["equipment_model", "technician_name", "dealership_region"]
    client.create_table(table, exists_ok=True)
    
    rows = generate_synthetic_billing_rows(days_back=days_back)
    
    job_config = bigquery.LoadJobConfig(
        schema=BILLING_SCHEMA,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
    )
    
    load_job = client.load_table_from_json(rows, table_ref, job_config=job_config)
    if wait_for_job:
        load_job.result()
        
    return {
        "project_id": project_id,
        "dataset_id": dataset_id,
        "table_id": table_id,
        "table_fqn": f"{project_id}.{dataset_id}.{table_id}",
        "total_rows_seeded": len(rows),
        "job_id": load_job.job_id
    }
