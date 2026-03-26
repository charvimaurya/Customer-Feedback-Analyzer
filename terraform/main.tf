provider "google" {
  project = var.project_id
  region  = var.region
}

# 1. Artifact Registry for Docker images
resource "google_artifact_registry_repository" "repo" {
  location      = var.region
  repository_id = var.app_name
  description   = "Docker repository for Customer Feedback Analyzer"
  format        = "DOCKER"
}

# 2. Cloud SQL Database (PostgreSQL)
resource "google_sql_database_instance" "instance" {
  name             = "${var.app_name}-db-instance"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier = "db-f1-micro" # Smallest instance for cost efficiency
    ip_configuration {
      ipv4_enabled = true
    }
  }
  deletion_protection = false # Set to true for production
}

resource "google_sql_database" "database" {
  name     = "customer_feedback"
  instance = google_sql_database_instance.instance.name
}

resource "google_sql_user" "users" {
  name     = "user"
  instance = google_sql_database_instance.instance.name
  password = var.db_password
}

# 3. Cloud Run Service for API
resource "google_cloud_run_v2_service" "api" {
  name     = "${var.app_name}-api"
  location = var.region

  template {
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.repo.name}/api:latest"
      
      env {
        name  = "DATABASE_URL"
        value = "postgresql://user:${var.db_password}@${google_sql_database_instance.instance.public_ip_address}:5432/customer_feedback"
      }
      
      ports {
        container_port = 8000
      }
    }
    
    # Cloud SQL Connection
    scaling {
      max_instance_count = 5
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  depends_on = [google_sql_database.database]
}

# 4. Cloud Run Service for Streamlit UI
resource "google_cloud_run_v2_service" "ui" {
  name     = "${var.app_name}-ui"
  location = var.region

  template {
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.repo.name}/ui:latest"
      
      env {
        name  = "API_URL"
        value = google_cloud_run_v2_service.api.uri
      }
      
      ports {
        container_port = 8501
      }
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

# 5. Make services public (optional, for demo)
resource "google_cloud_run_v2_service_iam_member" "api_public" {
  location = google_cloud_run_v2_service.api.location
  name     = google_cloud_run_v2_service.api.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_v2_service_iam_member" "ui_public" {
  location = google_cloud_run_v2_service.ui.location
  name     = google_cloud_run_v2_service.ui.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
