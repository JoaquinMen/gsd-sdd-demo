output "vpc_network_name" {
  value       = module.vpc.network_name
  description = "The name of the VPC network"
}

output "direct_egress_subnet_name" {
  value       = module.vpc.subnet_name
  description = "The name of the Direct VPC Egress subnet"
}

output "cloud_run_uri" {
  value       = module.cloud_run.service_uri
  description = "The Direct IAP secured URI of the Cloud Run portal"
}

output "bigquery_table_fqn" {
  value       = module.bigquery.table_fqn
  description = "Fully qualified BigQuery service billing table name"
}

output "gcs_docs_bucket_url" {
  value       = module.storage.bucket_url
  description = "Documentation staging bucket URL"
}

output "agent_service_account_email" {
  value       = module.iam.service_account_email
  description = "Runtime service account email address"
}
