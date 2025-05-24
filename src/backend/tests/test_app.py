import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import app
from database import Base, get_db
from models import User

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)

@pytest.fixture(scope="function")
def test_db():
    # Create the database tables
    Base.metadata.create_all(bind=engine)
    
    # Create a test admin user
    db = TestingSessionLocal()
    admin_user = User(
        username="admin",
        email="admin@example.com",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
        role="admin"
    )
    db.add(admin_user)
    db.commit()
    
    yield  # Run the tests
    
    # Drop the tables after the test
    Base.metadata.drop_all(bind=engine)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_login(test_db):
    response = client.post(
        "/token",
        data={"username": "admin", "password": "password"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_wrong_password(test_db):
    response = client.post(
        "/token",
        data={"username": "admin", "password": "wrong"}
    )
    assert response.status_code == 401

def test_get_current_user(test_db):
    # First login to get token
    login_response = client.post(
        "/token",
        data={"username": "admin", "password": "password"}
    )
    token = login_response.json()["access_token"]
    
    # Use token to get current user
    response = client.get(
        "/users/me/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "admin"
    assert response.json()["role"] == "admin"

def test_unauthorized_access(test_db):
    response = client.get("/clients/")
    assert response.status_code == 401

def test_create_client(test_db):
    # First login to get token
    login_response = client.post(
        "/token",
        data={"username": "admin", "password": "password"}
    )
    token = login_response.json()["access_token"]
    
    # Create a client
    response = client.post(
        "/clients/",
        json={"name": "Test Client", "description": "Test Description"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Test Client"
    assert response.json()["description"] == "Test Description"
    
    # Get the client
    client_id = response.json()["id"]
    response = client.get(
        f"/clients/{client_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Test Client"

def test_get_clients(test_db):
    # First login to get token
    login_response = client.post(
        "/token",
        data={"username": "admin", "password": "password"}
    )
    token = login_response.json()["access_token"]
    
    # Create a client
    client.post(
        "/clients/",
        json={"name": "Test Client 1", "description": "Test Description 1"},
        headers={"Authorization": f"Bearer {token}"}
    )
    client.post(
        "/clients/",
        json={"name": "Test Client 2", "description": "Test Description 2"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Get all clients
    response = client.get(
        "/clients/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["name"] == "Test Client 1"
    assert response.json()[1]["name"] == "Test Client 2"

def test_update_client(test_db):
    # First login to get token
    login_response = client.post(
        "/token",
        data={"username": "admin", "password": "password"}
    )
    token = login_response.json()["access_token"]
    
    # Create a client
    create_response = client.post(
        "/clients/",
        json={"name": "Test Client", "description": "Test Description"},
        headers={"Authorization": f"Bearer {token}"}
    )
    client_id = create_response.json()["id"]
    
    # Update the client
    response = client.put(
        f"/clients/{client_id}",
        json={"name": "Updated Client", "description": "Updated Description"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Client"
    assert response.json()["description"] == "Updated Description"

def test_delete_client(test_db):
    # First login to get token
    login_response = client.post(
        "/token",
        data={"username": "admin", "password": "password"}
    )
    token = login_response.json()["access_token"]
    
    # Create a client
    create_response = client.post(
        "/clients/",
        json={"name": "Test Client", "description": "Test Description"},
        headers={"Authorization": f"Bearer {token}"}
    )
    client_id = create_response.json()["id"]
    
    # Delete the client
    response = client.delete(
        f"/clients/{client_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    
    # Verify client is deleted
    response = client.get(
        f"/clients/{client_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404
