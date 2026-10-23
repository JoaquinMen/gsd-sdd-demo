output "bucket_name" {
  value       = google_storage_bucket.docs_bucket.name
  description = "The name of the documentation storage bucket"
}

output "bucket_url" {
  value       = google_storage_bucket.docs_bucket.url
  description = "The gs:// URL of the bucket"
}
