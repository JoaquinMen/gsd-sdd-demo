resource "google_service_account" "agent_sa" {
  account_id   = "sa-cimbal-agent"
  display_name = "Cimbal SA Operations Agent Runtime Service Account"
  description  = "Least-privilege identity executing the Cimbal SA multi-tool conversational agent"
}

# Vertex AI Gemini invocation
resource "google_project_iam_member" "aiplatform_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.agent_sa.email}"
}

# Vertex AI Search (Discovery Engine) read-only queries
resource "google_project_iam_member" "discoveryengine_viewer" {
  project = var.project_id
  role    = "roles/discoveryengine.viewer"
  member  = "serviceAccount:${google_service_account.agent_sa.email}"
}

# BigQuery query jobs execution
resource "google_project_iam_member" "bigquery_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.agent_sa.email}"
}

# BigQuery dataset-level read-only data access
resource "google_bigquery_dataset_iam_member" "dataset_viewer" {
  dataset_id = var.bq_dataset_id
  role       = "roles/bigquery.dataViewer"
  member     = "serviceAccount:${google_service_account.agent_sa.email}"
}

# Direct IAP: Grant Cloud Run Invoker to the IAP Service Agent
resource "google_cloud_run_v2_service_iam_member" "iap_invoker" {
  project  = var.project_id
  location = var.location
  name     = var.cloud_run_service_name
  role     = "roles/run.invoker"
  member   = "serviceAccount:service-${var.project_number}@gcp-sa-iap.iam.gserviceaccount.com"
}
