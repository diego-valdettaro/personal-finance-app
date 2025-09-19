"""
Tests for authentication system.
"""
from app.auth import create_access_token, verify_password, get_password_hash

def test_create_access_token():
    """Test JWT token creation."""
    token = create_access_token(data={"sub": "test@example.com"})
    assert token is not None
    assert isinstance(token, str)

def test_verify_password():
    """Test password verification."""
    password = "testpassword123"
    hashed = get_password_hash(password)
    
    assert verify_password(password, hashed) == True
    assert verify_password("wrongpassword", hashed) == False

def test_register_user(client):
    """Test user registration."""
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword123",
        "home_currency": "USD"
    }
    
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["name"] == user_data["name"]
    assert data["email"] == user_data["email"]
    assert data["home_currency"] == user_data["home_currency"]
    assert "id" in data
    assert "password" not in data  # Password should not be returned

def test_register_duplicate_email(client):
    """Test registration with duplicate email fails."""
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword123",
        "home_currency": "USD"
    }
    
    # First registration should succeed
    response1 = client.post("/auth/register", json=user_data)
    assert response1.status_code == 201
    
    # Second registration with same email should fail
    response2 = client.post("/auth/register", json=user_data)
    assert response2.status_code == 409

def test_login_user(client):
    """Test user login."""
    # First register a user
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword123",
        "home_currency": "USD"
    }
    
    client.post("/auth/register", json=user_data)
    
    # Then login
    login_data = {
        "username": "test@example.com",
        "password": "testpassword123"
    }
    
    response = client.post("/auth/login", data=login_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client):
    """Test login with invalid credentials fails."""
    login_data = {
        "username": "nonexistent@example.com",
        "password": "wrongpassword"
    }
    
    response = client.post("/auth/login", data=login_data)
    assert response.status_code == 401

def test_protected_endpoint_with_valid_token(client):
    """Test accessing protected endpoint with valid token."""
    # Register and login
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword123",
        "home_currency": "USD"
    }
    
    register_response = client.post("/auth/register", json=user_data)
    user_id = register_response.json()["id"]
    
    login_data = {
        "username": "test@example.com",
        "password": "testpassword123"
    }
    
    login_response = client.post("/auth/login", data=login_data)
    token = login_response.json()["access_token"]
    
    # Access protected endpoint
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(f"/users/{user_id}/accounts", headers=headers)
    assert response.status_code == 200

def test_protected_endpoint_without_token(client, sample_user):
    """Test accessing protected endpoint without token fails."""
    # Temporarily disable authentication override for this test
    from app.dependencies import get_authenticated_user
    from app.main import app
    
    # Store original dependency
    original_dependency = app.dependency_overrides.get(get_authenticated_user)
    
    # Remove override temporarily
    if get_authenticated_user in app.dependency_overrides:
        del app.dependency_overrides[get_authenticated_user]
    
    try:
        response = client.get(f"/users/{sample_user.id}/accounts")
        assert response.status_code == 403
    finally:
        # Restore original dependency
        if original_dependency:
            app.dependency_overrides[get_authenticated_user] = original_dependency

def test_protected_endpoint_with_invalid_token(client, sample_user):
    """Test accessing protected endpoint with invalid token fails."""
    # Temporarily disable authentication override for this test
    from app.dependencies import get_authenticated_user
    from app.main import app
    
    # Store original dependency
    original_dependency = app.dependency_overrides.get(get_authenticated_user)
    
    # Remove override temporarily
    if get_authenticated_user in app.dependency_overrides:
        del app.dependency_overrides[get_authenticated_user]
    
    try:
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get(f"/users/{sample_user.id}/accounts", headers=headers)
        assert response.status_code == 401
    finally:
        # Restore original dependency
        if original_dependency:
            app.dependency_overrides[get_authenticated_user] = original_dependency
