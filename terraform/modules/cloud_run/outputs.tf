output "service_id" {
  value       = google_cloud_run_v2_service.cimbal_service.id
  description = "The ID of the Cloud Run service"
}

output "service_uri" {
  value       = google_cloud_run_v2_service.cimbal_service.uri
  description = "The URI of the Cloud Run service"
}

output "service_name" {
  value       = google_cloud_run_v2_service.cimbal_service.name
  description = "The name of the Cloud Run service"
}
