terraform {
  required_version = ">= 0.14"

  required_providers {
    # Cloud Run support was added on 3.3.0
    google = ">= 3.3"
  }
}

variable "project_id" {
  description = "The GCP project ID for the project"
  type        = string
}

variable "container_image" {
  description = "The container image to deploy"
  type        = string
}

provider "google" {
  project = var.project_id
}

# Enables the Cloud Run API
resource "google_project_service" "run_api" {
  service = "run.googleapis.com"

  disable_on_destroy = false
}

# Create the Cloud Run service
resource "google_cloud_run_service" "run_service" {
  name     = "states"
  location = "us-central1"

  template {
    spec {
      containers {
        image = var.container_image
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  # Waits for the Cloud Run API to be enabled
  depends_on = [google_project_service.run_api]
}

# Allow unauthenticated users to invoke the service
resource "google_cloud_run_service_iam_member" "run_all_users" {
  service  = google_cloud_run_service.run_service.name
  location = google_cloud_run_service.run_service.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}


# Display the service URL
output "service_url" {
  value       = google_cloud_run_service.run_service.status[0].url
  description = "URL of state lookup API"
}


