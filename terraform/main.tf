
# VPC Network for private communication
resource "google_compute_network" "vpc" {
  name                    = "task-app-vpc"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "subnet" {
  name          = "task-app-subnet"
  ip_cidr_range = "10.1.0.0/24"
  region        = var.region
  network       = google_compute_network.vpc.id
}

# Private service connection for Cloud SQL
resource "google_compute_global_address" "private_ip_address" {
  name          = "private-ip-address"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.vpc.id
}

resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.vpc.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_address.name]
}

# VPC Connector for Cloud Run to access private resources
resource "google_vpc_access_connector" "connector" {
  name          = "task-app-connector"
  region        = var.region
  ip_cidr_range = "10.2.0.0/28"
  network       = google_compute_network.vpc.name
}


# Service Account for Cloud Run with minimal permissions
resource "google_service_account" "cloud_run_sa" {
  account_id   = "cloud-run-sa"
  display_name = "Cloud Run Service Account"
}

# Grant minimal permissions to Cloud Run SA
resource "google_project_iam_member" "cloud_run_sql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

resource "google_secret_manager_secret_iam_member" "cloud_run_secret_access" {
  secret_id = google_secret_manager_secret.db_password.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

resource "google_cloud_run_service" "task_app" {
  name     = "task-app"
  location = var.region

  template {
    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale"                    = "2"
        "autoscaling.knative.dev/minScale"                    = "1"
        "run.googleapis.com/cloudsql-instances"               = google_sql_database_instance.postgres.connection_name
        "run.googleapis.com/vpc-access-connector"             = google_vpc_access_connector.connector.name
        "run.googleapis.com/vpc-access-egress"                = "private-ranges-only"
        "run.googleapis.com/execution-environment"            = "gen2"
        "run.googleapis.com/cpu-throttling"                   = "false"
      }
    }

    spec {
      service_account_name = google_service_account.cloud_run_sa.email
    
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/task-app/task-app:latest"

        ports {
          container_port = 8000
        }

        env {
          name = "DATABASE_URL"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.db_password.secret_id
              key  = "latest"
            }
          }
        }

        env {
          name  = "DB_HOST"
          value = google_sql_database_instance.postgres.private_ip_address
        }

        env {
          name  = "DB_NAME"
          value = google_sql_database.database.name
        }

        env {
          name  = "DB_USER"
          value = var.db_username
        }

        env {
          name  = "ENVIRONMENT"
          value = var.environment
        }

        resources {
          limits = {
            cpu    = "1000m"
            memory = "512Mi"
          }
          requests = {
            cpu    = "100m"
            memory = "128Mi"
          }
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  depends_on = [
    google_sql_database_instance.postgres,
    google_vpc_access_connector.connector,
    google_service_networking_connection.private_vpc_connection
  ]
}

# Cloud Run IAM with conditions
resource "google_cloud_run_service_iam_binding" "default" {
  location = google_cloud_run_service.task_app.location
  project  = google_cloud_run_service.task_app.project
  service  = google_cloud_run_service.task_app.name
  role     = "roles/run.invoker"

  members = [
    "allUsers"  
  ]
}
