output "service_account_email" {
  value       = google_service_account.agent_sa.email
  description = "The email address of the runtime service account"
}

output "service_account_id" {
  value       = google_service_account.agent_sa.id
  description = "The fully qualified ID of the runtime service account"
}
