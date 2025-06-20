import pytest
import requests
import time
import subprocess
import os

# Simple function to check if service is available
def is_service_running():
    try:
        response = requests.get("http://localhost:8000/health", timeout=1)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

# Mark to skip tests in CI if services aren't running
skip_if_ci_no_service = pytest.mark.skipif(
    os.environ.get("CI") == "true" and not is_service_running(),
    reason="Skipping integration tests in CI if Docker services are not available"
)

@skip_if_ci_no_service
class TestIntegration:
    @classmethod
    def setup_class(cls):
        """Set up integration test environment"""
        cls.base_url = "http://localhost:8000"
        
        # Only start docker-compose if not running in CI
        if os.environ.get("CI") != "true":
            cls.start_test_environment()
            
        cls.wait_for_services()

    @classmethod
    def teardown_class(cls):
        """Tear down integration test environment"""
        # Only stop docker-compose if not running in CI
        if os.environ.get("CI") != "true":
            cls.stop_test_environment()

    @classmethod
    def start_test_environment(cls):
        """Start docker-compose for integration tests"""
        try:
            subprocess.run(["docker-compose", "up", "-d"], check=True)
            print("Started docker-compose services")
        except subprocess.CalledProcessError as e:
            print(f"Failed to start services: {e}")
            raise

    @classmethod
    def stop_test_environment(cls):
        """Stop docker-compose"""
        try:
            subprocess.run(["docker-compose", "down"], check=True)
            print("Stopped docker-compose services")
        except subprocess.CalledProcessError as e:
            print(f"Failed to stop services: {e}")
            raise

    @classmethod
    def wait_for_services(cls):
        """Wait for services to be healthy"""
        max_attempts = 60  # Increased from 30 to 60 attempts
        attempt = 0
        while attempt < max_attempts:
            try:
                response = requests.get(f"{cls.base_url}/health")
                if response.status_code == 200:
                    print("Services are ready!")
                    return
            except requests.exceptions.ConnectionError:
                print(f"Waiting for services... attempt {attempt + 1}/{max_attempts}")
                time.sleep(2)  # Increased from 1 to 2 seconds
                attempt += 1
        
        # If we reach here, dump logs to help debugging
        try:
            logs = subprocess.check_output(["docker-compose", "logs", "app"]).decode("utf-8")
            print("App logs:")
            print(logs)
        except:
            print("Could not get app container logs")
            
        raise Exception("Services failed to start in time")

    def test_api_health(self):
        """Test API health endpoint"""
        response = requests.get(f"{self.base_url}/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_full_crud_workflow(self):
        """Test complete CRUD workflow"""
        # Create task
        create_response = requests.post(
            f"{self.base_url}/tasks/",
            params={"title": "Integration Test Task", "description": "Test Description"}
        )
        assert create_response.status_code == 201
        task = create_response.json()
        task_id = task["id"]

        # Read task
        get_response = requests.get(f"{self.base_url}/tasks/{task_id}")
        assert get_response.status_code == 200
        assert get_response.json()["title"] == "Integration Test Task"

        # Update task
        update_response = requests.put(
            f"{self.base_url}/tasks/{task_id}",
            params={"title": "Updated Integration Task", "completed": True}
        )
        assert update_response.status_code == 200
        assert update_response.json()["completed"] == True

        # Delete task
        delete_response = requests.delete(f"{self.base_url}/tasks/{task_id}")
        assert delete_response.status_code == 200

        # Verify deletion
        get_deleted_response = requests.get(f"{self.base_url}/tasks/{task_id}")
        assert get_deleted_response.status_code == 404

    def test_metrics_endpoint(self):
        """Test metrics endpoint for monitoring"""
        response = requests.get(f"{self.base_url}/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "total_tasks" in data
        assert "service_status" in data
        assert data["service_status"] == "running"
