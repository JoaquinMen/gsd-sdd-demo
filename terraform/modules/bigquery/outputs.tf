output "dataset_id" {
  value       = google_bigquery_dataset.cimbal_dataset.dataset_id
  description = "The BigQuery dataset ID"
}

output "table_id" {
  value       = google_bigquery_table.billing_table.table_id
  description = "The BigQuery table ID"
}

output "table_fqn" {
  value       = "${google_bigquery_dataset.cimbal_dataset.project}.${google_bigquery_dataset.cimbal_dataset.dataset_id}.${google_bigquery_table.billing_table.table_id}"
  description = "The fully qualified BigQuery table name"
}
