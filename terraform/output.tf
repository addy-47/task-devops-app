output "cloud_run_url" {
  description = "URL of the Cloud Run service"
  value       = google_cloud_run_service.task_app.status[0].url
}

output "database_ip" {
  description = "IP address of the database"
  value       = google_sql_database_instance.postgres.public_ip_address
}

output "artifact_registry_url" {
  description = "URL of the Artifact Registry repository"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/task-app"
}

output "database_connection_name" {
  description = "Database connection name for Cloud SQL Proxy"
  value       = google_sql_database_instance.postgres.connection_name
}
