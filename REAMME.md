# 🚀 Task Management API

A modern REST API for task management with CRUD operations, built with **FastAPI** and **PostgreSQL**, deployed on **Google Cloud Platform (GCP)** using **Terraform** and automated CI/CD via **GitHub Actions**.

---

## 📁 Project Structure

```
task-api-project/
├── app/                    # FastAPI application code
│   ├── main.py             # API endpoints
│   ├── models.py           # SQLAlchemy models
│   ├── database.py         # Database configuration
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # Docker configuration
├── tests/                  # Unit and integration tests
│   ├── test_unit.py
│   └── test_integration.py
├── terraform/              # Terraform infrastructure code
│   ├── provider.tf         # Terraform and provider config
│   ├── database.tf         # Cloud SQL and related resources
│   ├── main.tf             # Other infrastructure resources
│   ├── variables.tf        # Input variables
│   ├── outputs.tf          # Output values
│   └── terraform.tfvars.example  # Example variable values
├── .github/workflows/      # CI/CD pipeline
│   └── ci-cd.yml
├── docker-compose.yml      # Local development setup
├── .gitignore              # Git ignore rules
└── README.md               # Project documentation
└── sa-policy.yaml       # Service account policy for Terraform
```

---

## 📝 Overview

This project provides a task management API with endpoints for creating, reading, updating, and deleting tasks. It uses:

- **Backend:** FastAPI, SQLAlchemy, PostgreSQL
- **Infrastructure:** GCP (Cloud Run, Cloud SQL, Artifact Registry), Terraform
- **CI/CD:** GitHub Actions for testing, building, and deploying
- **Testing:** Pytest for unit and integration tests
- **Monitoring:** Health and metrics endpoints for observability

---

## ⚙️ Prerequisites

| Requirement         | Description                                  |
|--------------------|----------------------------------------------|
| GCP account        | Free tier with billing enabled                |
| GitHub account     | For code and CI/CD                           |
| Docker             | Installed locally                            |
| Terraform CLI      | Installed                                    |
| gcloud CLI         | Installed and authenticated                  |
| Python 3.9+        | Installed                                    |

---

## 🚦 Setup

### 1. Configure GCP
- Enable APIs: `run.googleapis.com`, `sqladmin.googleapis.com`, `artifactregistry.googleapis.com`, `cloudbuild.googleapis.com`, `cloudresourcemanager.googleapis.com`, `iam.googleapis.com`.
- Create a service account (`terraform-sa`) with roles:
  - `run.developer`, `cloudsql.admin`, `artifactregistry.admin`, `iam.serviceAccountUser`, `storage.admin`
- Set up Workload Identity Federation for GitHub Actions (see roadmap for details).
- Create a GCS bucket for Terraform state: `gs://YOUR_PROJECT_ID-terraform-state`

### 2. Set GitHub Secrets
| Secret Name         | Value                        |
|---------------------|------------------------------|
| GCP_PROJECT_ID      | Your GCP project ID          |
| GCP_PROJECT_NUMBER  | Your GCP project number      |

Configure Workload Identity Federation in GitHub repository settings.

### 3. Clone Repository
```bash
git clone <your-repo-url>
cd task-api-project
```

### 4. Local Development
```bash
docker-compose up -d
curl http://localhost:8000/health
```
This starts the FastAPI app and PostgreSQL database locally. Access the API at [http://localhost:8000](http://localhost:8000).

### 5. Deploy to GCP
- Push changes to the `main` branch to trigger the CI/CD pipeline.
- The pipeline runs tests, builds/pushes the Docker image, and deploys to Cloud Run using Terraform.

---

## 📚 API Endpoints

| Method | Endpoint                | Description                        |
|--------|-------------------------|------------------------------------|
| GET    | /health                 | Check service health               |
| GET    | /metrics                | View service metrics               |
| POST   | /tasks/?title=&desc=    | Create a task                      |
| GET    | /tasks/                 | List tasks (supports skip/limit)   |
| GET    | /tasks/{id}             | Get a specific task                |
| PUT    | /tasks/{id}?title=&desc=&completed= | Update a task         |
| DELETE | /tasks/{id}             | Delete a task                      |

---

## 🧪 Testing

Run tests locally:
```bash
docker-compose up -d
cd tests
pip install -r ../app/requirements.txt pytest requests
python -m pytest test_unit.py test_integration.py -v
docker-compose down
```
The CI/CD pipeline automatically runs tests on push/pull requests.

---

## 🚢 Deployment

Pushing to the `main` branch triggers:
- Security scans (Trivy, Bandit, Safety)
- Unit and integration tests
- Docker image build and push to Artifact Registry
- Terraform deployment to Cloud Run and Cloud SQL
- Health check to verify deployment

---

## 📈 Monitoring

- Health endpoint: `/health`
- Metrics endpoint: `/metrics`
- Structured logging for integration with tools like Prometheus/Grafana

---

## 📝 Notes

- The API is publicly accessible for demo purposes (`--allow-unauthenticated` in Cloud Run).
- Terraform state is stored in GCS (`YOUR_PROJECT_ID-terraform-state`).
- Use the commit SHA-tagged Docker image for rollbacks if needed.

---

> _Made with ❤️ using FastAPI, Terraform, and GCP._

