variable "service_name" {
  type        = string
  description = "The name of the Cloud Run service"
  default     = "cimbal-ops-portal"
}

variable "location" {
  type        = string
  description = "The GCP region for the Cloud Run service"
  default     = "us-central1"
}

variable "image" {
  type        = string
  description = "Container image URI"
  default     = "us-central1-docker.pkg.dev/cimbal-ag-prod/cimbal-app/agent-portal:latest"
}

variable "network_id" {
  type        = string
  description = "The ID of the VPC network"
}

variable "subnet_id" {
  type        = string
  description = "The ID of the Direct VPC Egress subnet"
}

variable "service_account_email" {
  type        = string
  description = "The runtime service account email"
}

variable "project_id" {
  type        = string
  description = "Target GCP Project ID"
}

variable "bq_dataset_id" {
  type        = string
  description = "BigQuery dataset ID"
  default     = "cimbal_operations"
}

variable "bq_table_id" {
  type        = string
  description = "BigQuery table ID"
  default     = "equipment_service_billing"
}

variable "gcs_bucket_name" {
  type        = string
  description = "GCS bucket name for documentation"
}

variable "datastore_id" {
  type        = string
  description = "Vertex AI Search DataStore ID"
  default     = "cimbal-equipment-policies-ds"
}
