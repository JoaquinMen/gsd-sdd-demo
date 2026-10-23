variable "project_id" {
  type        = string
  description = "Target Google Cloud Project ID"
  default     = "cimbal-ag-prod"
}

variable "project_number" {
  type        = string
  description = "Target Google Cloud Project Number"
  default     = "123456789012"
}

variable "region" {
  type        = string
  description = "Default regional compute and storage location"
  default     = "us-central1"
}

variable "vpc_network_name" {
  type        = string
  description = "Custom VPC network name"
  default     = "cimbal-secure-vpc"
}

variable "vpc_subnet_name" {
  type        = string
  description = "Direct VPC Egress subnet name"
  default     = "cimbal-direct-egress-subnet"
}

variable "vpc_subnet_cidr" {
  type        = string
  description = "CIDR block for Direct VPC Egress subnet"
  default     = "10.0.1.0/24"
}

variable "cloud_run_service_name" {
  type        = string
  description = "Cloud Run service identifier"
  default     = "cimbal-ops-portal"
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
  default     = "cimbal-ag-prod-equipment-docs"
}

variable "datastore_id" {
  type        = string
  description = "Discovery Engine DataStore ID"
  default     = "cimbal-equipment-policies-ds"
}

variable "container_image" {
  type        = string
  description = "Container image URI for Cloud Run"
  default     = "us-central1-docker.pkg.dev/cimbal-ag-prod/cimbal-app/agent-portal:latest"
}
