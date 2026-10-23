variable "network_name" {
  type        = string
  description = "The name of the VPC network"
  default     = "cimbal-secure-vpc"
}

variable "subnet_name" {
  type        = string
  description = "The name of the Direct VPC Egress subnet"
  default     = "cimbal-direct-egress-subnet"
}

variable "subnet_cidr" {
  type        = string
  description = "CIDR range for the Direct VPC Egress subnet"
  default     = "10.0.1.0/24"
}

variable "region" {
  type        = string
  description = "The GCP region for the subnet"
  default     = "us-central1"
}
