# Generate random password for database
resource "random_password" "db_password" {
  length  = 16
  special = true
}

# Store database password in Secret Manager
resource "google_secret_manager_secret" "db_password" {
  secret_id = "database-password"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "db_password" {
  secret      = google_secret_manager_secret.db_password.id
  secret_data = random_password.db_password.result
}

# Artifact Registry Repository
resource "google_artifact_registry_repository" "task_app_repo" {
  location      = var.region
  repository_id = "task-app"
  description   = "Docker repository for task app"
  format        = "DOCKER"
}

# Cloud SQL Instance (PostgreSQL) 
resource "google_sql_database_instance" "postgres" {
  name             = "task-app-db"
  database_version = "POSTGRES_14"
  region           = var.region
  deletion_protection = true  # Enable deletion protection


    settings {
        tier              = "db-f1-micro"
        availability_type = "ZONAL"
        disk_type         = "PD_SSD"  # Use SSD for better performance
        disk_size         = 2
        disk_autoresize   = true
        disk_autoresize_limit = 5

    # Security configurations
    database_flags {
      name  = "log_checkpoints"
      value = "on"
    }

    database_flags {
      name  = "log_connections"
      value = "on"
    }

    database_flags {
      name  = "log_disconnections"
      value = "on"
    }
    
    # Fix for MEDIUM: Log lock waits
    database_flags {
      name  = "log_lock_waits"
      value = "on"
    }

    # Fix for MEDIUM: Enable temporary file logging
    database_flags {
      name  = "log_temp_files"
      value = "0" # Log all temporary files
    }

    backup_configuration {
      enabled                        = true
      start_time                     = "03:00"
      point_in_time_recovery_enabled = true
      backup_retention_settings {
        retained_backups = 2
        retention_unit   = "COUNT"
      }
    }

    # tfsec:ignore:google-sql-encrypt-in-transit-data
    ip_configuration {
      ipv4_enabled                                  = false  
      private_network                               = google_compute_network.vpc.id
      enable_private_path_for_google_cloud_services = true
      # Fix for HIGH: Require SSL/TLS for all connections
      ssl_mode = "REQUIRED"
    }

    maintenance_window {
      day          = 7  # Sunday
      hour         = 3  # 3 AM
      update_track = "stable"
    }
  }

  depends_on = [google_service_networking_connection.private_vpc_connection]
}

# Database
resource "google_sql_database" "database" {
  name     = "taskdb"
  instance = google_sql_database_instance.postgres.name
}

# Database User with generated password
resource "google_sql_user" "users" {
  name     = var.db_username
  instance = google_sql_database_instance.postgres.name
  password = random_password.db_password.result
}