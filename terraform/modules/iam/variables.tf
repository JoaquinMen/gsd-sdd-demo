variable "project_id" {
  type        = string
  description = "Target GCP Project ID"
}

variable "project_number" {
  type        = string
  description = "Target GCP Project Number"
}

variable "cloud_run_service_name" {
  type        = string
  description = "Cloud Run service name for IAP invoker binding"
}

variable "location" {
  type        = string
  description = "Cloud Run service location"
  default     = "us-central1"
}

variable "bq_dataset_id" {
  type        = string
  description = "BigQuery dataset ID for dataViewer binding"
}
