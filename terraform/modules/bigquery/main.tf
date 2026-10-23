resource "google_bigquery_dataset" "cimbal_dataset" {
  dataset_id                  = var.dataset_id
  location                    = var.location
  description                 = "Cimbal SA Agricultural Equipment Operations & Field Service Warehouse"
  default_table_expiration_ms = null
}

resource "google_bigquery_table" "billing_table" {
  dataset_id = google_bigquery_dataset.cimbal_dataset.dataset_id
  table_id   = var.table_id

  description = "Equipment field service logs, technician labor hours, parts costs, and warranty classification"

  time_partitioning {
    type  = "DAY"
    field = "service_date"
  }

  clustering = ["equipment_model", "technician_name", "dealership_region"]

  schema = jsonencode([
    { name = "entry_id", type = "STRING", mode = "REQUIRED", description = "Unique service log entry identifier (e.g., SRV-2001)" },
    { name = "service_date", type = "DATE", mode = "REQUIRED", description = "Date the service was performed (YYYY-MM-DD)" },
    { name = "equipment_model", type = "STRING", mode = "REQUIRED", description = "Machinery model (e.g., Combine Harvester X9, Tractor 8R)" },
    { name = "customer_name", type = "STRING", mode = "REQUIRED", description = "Farm or agribusiness client name" },
    { name = "technician_name", type = "STRING", mode = "REQUIRED", description = "Certified field technician name" },
    { name = "dealership_region", type = "STRING", mode = "REQUIRED", description = "Regional dealership hub (Midwest, South, West)" },
    { name = "labor_hours", type = "FLOAT64", mode = "REQUIRED", description = "Number of technician labor hours logged" },
    { name = "hourly_rate_usd", type = "FLOAT64", mode = "REQUIRED", description = "Billing rate in USD per labor hour" },
    { name = "parts_cost_usd", type = "FLOAT64", mode = "REQUIRED", description = "Replacement parts and consumables cost in USD" },
    { name = "is_warranty_claim", type = "BOOL", mode = "REQUIRED", description = "True if covered under OEM warranty, False if customer billed" },
    { name = "task_category", type = "STRING", mode = "REQUIRED", description = "Service category (Diagnostics, Overhaul, Hydraulics, Maintenance)" },
    { name = "technician_notes", type = "STRING", mode = "NULLABLE", description = "Detailed field service notes and diagnostic codes" }
  ])
}
