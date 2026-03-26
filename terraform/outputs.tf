output "api_url" {
  description = "The URL of the API service"
  value       = google_cloud_run_v2_service.api.uri
}

output "ui_url" {
  description = "The URL of the Streamlit UI service"
  value       = google_cloud_run_v2_service.ui.uri
}

output "db_instance_ip" {
  description = "Public IP of the database instance"
  value       = google_sql_database_instance.instance.public_ip_address
}

output "artifact_registry_repo" {
  description = "The Artifact Registry repository path"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${var.app_name}"
}
