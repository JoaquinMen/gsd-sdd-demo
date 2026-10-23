output "network_id" {
  value       = google_compute_network.vpc_network.id
  description = "The ID of the VPC network"
}

output "network_name" {
  value       = google_compute_network.vpc_network.name
  description = "The name of the VPC network"
}

output "subnet_id" {
  value       = google_compute_subnetwork.direct_egress_subnet.id
  description = "The ID of the Direct VPC Egress subnet"
}

output "subnet_name" {
  value       = google_compute_subnetwork.direct_egress_subnet.name
  description = "The name of the Direct VPC Egress subnet"
}
