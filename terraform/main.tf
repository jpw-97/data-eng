terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

data "google_project" "project" {
  project_id = var.project_id
}

resource "google_storage_bucket" "epd_pollen_datasets" {
  name          = "${var.project_id}-epd-pollen-datasets"
  location      = var.region
  force_destroy = true
  uniform_bucket_level_access = true
  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }
}

resource "google_bigquery_dataset" "raw_dataset" {
  dataset_id = "raw"
  location   = var.region
}

resource "google_bigquery_dataset" "analytics_dataset" {
  dataset_id = "analytics"
  location   = var.region
}
