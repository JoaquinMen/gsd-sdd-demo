variable "bucket_name" {
  type        = string
  description = "The name of the Cloud Storage bucket"
}

variable "location" {
  type        = string
  description = "The regional location of the bucket"
  default     = "us-central1"
}
