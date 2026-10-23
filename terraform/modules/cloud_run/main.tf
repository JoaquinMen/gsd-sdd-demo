resource "google_cloud_run_v2_service" "cimbal_service" {
  name        = var.service_name
  location    = var.location
  description = "Cimbal SA Secure Operations & Agriculture Intelligence Agent Portal"
  ingress     = "INGRESS_TRAFFIC_ALL" # Protected natively by Direct IAP

  # Native Direct IAP activation on Cloud Run
  iap_enabled = true

  template {
    service_account = var.service_account_email

    # Direct VPC Egress configuration
    vpc_access {
      egress = "ALL_TRAFFIC"
      network_interfaces {
        network    = var.network_id
        subnetwork = var.subnet_id
        tags       = ["cimbal-agent", "direct-vpc-egress"]
      }
    }

    scaling {
      min_instance_count = 1
      max_instance_count = 10
    }

    containers {
      image = var.image

      resources {
        limits = {
          cpu    = "2"
          memory = "2Gi"
        }
      }

      ports {
        container_port = 8080
      }

      env {
        name  = "GOOGLE_CLOUD_PROJECT"
        value = var.project_id
      }
      env {
        name  = "GOOGLE_CLOUD_LOCATION"
        value = var.location
      }
      env {
        name  = "GOOGLE_GENAI_USE_VERTEXAI"
        value = "TRUE"
      }
      env {
        name  = "GEMINI_MODEL"
        value = "gemini-3.5-flash"
      }
      env {
        name  = "BQ_DATASET_ID"
        value = var.bq_dataset_id
      }
      env {
        name  = "BQ_TABLE_ID"
        value = var.bq_table_id
      }
      env {
        name  = "GCS_DOCS_BUCKET"
        value = var.gcs_bucket_name
      }
      env {
        name  = "VERTEX_SEARCH_LOCATION"
        value = "global"
      }
      env {
        name  = "VERTEX_SEARCH_DATASTORE_ID"
        value = var.datastore_id
      }
      env {
        name  = "IAP_ENABLED"
        value = "TRUE"
      }
      env {
        name  = "IAP_BYPASS_DEV"
        value = "FALSE"
      }
    }
  }
}
