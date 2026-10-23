terraform {
  required_version = ">= 1.6.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.20.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# 1. Custom VPC & Subnet with Private Google Access (Direct Egress)
module "vpc" {
  source       = "./modules/vpc"
  network_name = var.vpc_network_name
  subnet_name  = var.vpc_subnet_name
  subnet_cidr  = var.vpc_subnet_cidr
  region       = var.region
}

# 2. BigQuery Analytical Warehouse
module "bigquery" {
  source     = "./modules/bigquery"
  dataset_id = var.bq_dataset_id
  table_id   = var.bq_table_id
  location   = var.region
}

# 3. Cloud Storage Documentation Staging Bucket
module "storage" {
  source      = "./modules/storage"
  bucket_name = var.gcs_bucket_name
  location    = var.region
}

# 4. IAM & Least-Privilege Service Account Roles
module "iam" {
  source                 = "./modules/iam"
  project_id             = var.project_id
  project_number         = var.project_number
  cloud_run_service_name = var.cloud_run_service_name
  location               = var.region
  bq_dataset_id          = module.bigquery.dataset_id
}

# 5. Cloud Run with Direct IAP and Direct VPC Egress
module "cloud_run" {
  source                = "./modules/cloud_run"
  service_name          = var.cloud_run_service_name
  location              = var.region
  image                 = var.container_image
  network_id            = module.vpc.network_id
  subnet_id             = module.vpc.subnet_id
  service_account_email = module.iam.service_account_email
  project_id            = var.project_id
  bq_dataset_id         = module.bigquery.dataset_id
  bq_table_id           = module.bigquery.table_id
  gcs_bucket_name       = module.storage.bucket_name
  datastore_id          = var.datastore_id
}
