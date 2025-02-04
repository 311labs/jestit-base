import pytest
from django.test import Client
import time
from jestit.helpers import paths
paths.configure_paths(__file__, 1)
paths.configure_apps()

from example.models import TODO


@pytest.fixture
def api_client():
    """Fixture for Django test client"""
    return Client()

# @pytest.fixture
# def test_user(db):
#     """Create a test user"""
#     return CustomUser.objects.create_user(email="test@example.com", password="testpass")

# def test_api_get_users(api_client):
#     """Test retrieving a list of users"""
#     response = api_client.get("/api/users/")
#     assert response.status_code == 200
#     assert "users" in response.json()

def test_api_create_todo(api_client):
    """Test TODO creation"""
    data = {"name": f"Example {time.time()}", "kind": "ticket", "description":"this is a test create"}
    response = api_client.post("/api/example/todo", data, content_type="application/json")
    assert response.status_code == 201
    assert response.json()["kind"] == "ticket"
