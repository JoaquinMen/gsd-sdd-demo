resource "google_compute_network" "vpc_network" {
  name                    = var.network_name
  auto_create_subnetworks = false
  description             = "Custom VPC network for Cimbal SA secure operations"
}

resource "google_compute_subnetwork" "direct_egress_subnet" {
  name                     = var.subnet_name
  ip_cidr_range            = var.subnet_cidr
  region                   = var.region
  network                  = google_compute_network.vpc_network.id
  private_ip_google_access = true
  description              = "Dedicated subnet for Cloud Run Direct VPC Egress with Private Google Access enabled"
}

resource "google_compute_firewall" "allow_internal" {
  name        = "${var.network_name}-allow-internal"
  network     = google_compute_network.vpc_network.name
  description = "Allow internal communication within the VPC"

  allow {
    protocol = "icmp"
  }

  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }

  allow {
    protocol = "udp"
    ports    = ["0-65535"]
  }

  source_ranges = [var.subnet_cidr]
}
