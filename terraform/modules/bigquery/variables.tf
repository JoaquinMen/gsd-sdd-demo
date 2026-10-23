variable "dataset_id" {
  type        = string
  description = "The ID of the BigQuery dataset"
  default     = "cimbal_operations"
}

variable "table_id" {
  type        = string
  description = "The ID of the BigQuery table"
  default     = "equipment_service_billing"
}

variable "location" {
  type        = string
  description = "The regional location of the BigQuery dataset"
  default     = "us-central1"
}
