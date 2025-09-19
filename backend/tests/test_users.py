"""
Test cases for user functionality in the finance app backend.
This module contains comprehensive tests for all user-related operations.
"""

import pytest

from app import models

class TestUserCreation:
    """Test cases for user creation (POST /users/)"""
    
    def test_create_user_success(self, client, db_session, sample_user_data):
        """Test successful user creation with valid data."""
        response = client.post("/users/", json=sample_user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_user_data["name"]
        assert data["email"] == sample_user_data["email"]
        assert data["home_currency"] == sample_user_data["home_currency"].upper()
        assert "id" in data
        assert data["id"] > 0
    
    def test_create_user_different_currencies(self, client, db_session):
        """Test user creation with different currency codes."""
        currencies = ["EUR", "GBP", "JPY", "CAD", "AUD"]
        
        for i, currency in enumerate(currencies):
            user_data = {
                "name": f"User {i}",
                "email": f"user{i}@example.com",
                "home_currency": currency,
                "password": "testpassword123"
            }
            response = client.post("/users/", json=user_data)
            assert response.status_code == 201
            assert response.json()["home_currency"] == currency.upper()
    
    def test_create_user_currency_normalization(self, client, db_session):
        """Test that currency codes are normalized to uppercase."""
        user_data = {
            "name": "Test User",
            "email": "test@example.com",
            "home_currency": "usd",
            "password": "testpassword123"
        }
        response = client.post("/users/", json=user_data)
        assert response.status_code == 201
        assert response.json()["home_currency"] == "USD"
    
    def test_create_user_missing_required_fields(self, client, db_session):
        """Test user creation with missing required fields."""
        # Missing name
        response = client.post("/users/", json={
            "email": "test@example.com",
            "home_currency": "USD"
        })
        assert response.status_code == 422
        
        # Missing email
        response = client.post("/users/", json={
            "name": "Test User",
            "home_currency": "USD"
        })
        assert response.status_code == 422
        
        # Missing home_currency
        response = client.post("/users/", json={
            "name": "Test User",
            "email": "test@example.com"
        })
        assert response.status_code == 422
    
    def test_create_user_invalid_email_format(self, client, db_session):
        """Test user creation with invalid email format."""
        user_data = {
            "name": "Test User",
            "email": "invalid-email",
            "home_currency": "USD",
            "password": "testpassword123"
        }
        response = client.post("/users/", json=user_data)
        assert response.status_code == 422
    
    def test_create_user_email_too_long(self, client, db_session):
        """Test user creation with email that's too long."""
        long_email = "a" * 250 + "@example.com"  # > 255 chars
        user_data = {
            "name": "Test User",
            "email": long_email,
            "home_currency": "USD",
            "password": "testpassword123"
        }
        response = client.post("/users/", json=user_data)
        assert response.status_code == 422
    
    def test_create_user_name_too_long(self, client, db_session):
        """Test user creation with name that's too long."""
        long_name = "a" * 101  # > 100 chars
        user_data = {
            "name": long_name,
            "email": "test@example.com",
            "home_currency": "USD"
        }
        response = client.post("/users/", json=user_data)
        assert response.status_code == 422
    
    def test_create_user_invalid_currency(self, client, db_session):
        """Test user creation with invalid currency code."""
        user_data = {
            "name": "Test User",
            "email": "test@example.com",
            "home_currency": "INVALID",
            "password": "testpassword123"
        }
        response = client.post("/users/", json=user_data)
        assert response.status_code == 422
    
    def test_create_user_duplicate_email(self, client, db_session, sample_user):
        """Test user creation with duplicate email."""
        user_data = {
            "name": "Another User",
            "email": sample_user.email,  # Same email as existing user
            "home_currency": "EUR",
            "password": "testpassword123"
        }
        response = client.post("/users/", json=user_data)
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]
    
    def test_create_user_empty_fields(self, client, db_session):
        """Test user creation with empty required fields."""
        # Empty name
        response = client.post("/users/", json={
            "name": "",
            "email": "test@example.com",
            "home_currency": "USD"
        })
        assert response.status_code == 422
        
        # Empty email
        response = client.post("/users/", json={
            "name": "Test User",
            "email": "",
            "home_currency": "USD"
        })
        assert response.status_code == 422

class TestGetUsers:
    """Test cases for getting users (GET /users/ and GET /users/{user_id})"""
    
    def test_get_all_users_empty(self, client, db_session):
        """Test getting all users when no users exist."""
        response = client.get("/users/")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_all_users_multiple(self, client, db_session, multiple_users):
        """Test getting all users when multiple users exist."""
        response = client.get("/users/")
        assert response.status_code == 200
        users = response.json()
        assert len(users) == 3
        
        # Verify all users are returned
        user_ids = [user["id"] for user in users]
        for user in multiple_users:
            assert user.id in user_ids
    
    def test_get_all_users_only_active(self, client, db_session, sample_user):
        """Test that only active users are returned."""
        # Create another user
        user2_data = {
            "name": "User 2",
            "email": "user2@example.com",
            "home_currency": "EUR",
            "password": "testpassword123"
        }
        response = client.post("/users/", json=user2_data)
        user2 = response.json()
        
        # Deactivate the first user
        client.patch(f"/users/{sample_user.id}/deactivate")
        
        # Get all users - should only return active user
        response = client.get("/users/")
        assert response.status_code == 200
        users = response.json()
        assert len(users) == 1
        assert users[0]["id"] == user2["id"]
    
    def test_get_user_success(self, client, db_session, sample_user):
        """Test getting a specific user by ID."""
        response = client.get(f"/users/{sample_user.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_user.id
        assert data["name"] == sample_user.name
        assert data["email"] == sample_user.email
        assert data["home_currency"] == sample_user.home_currency
    
    def test_get_user_not_found(self, client, db_session):
        """Test getting a non-existent user."""
        response = client.get("/users/99999")
        assert response.status_code == 404
    
    def test_get_user_deactivated(self, client, db_session, sample_user):
        """Test getting a deactivated user."""
        # Create another user first to avoid "last user" protection
        user2_data = {
            "name": "User 2",
            "email": "user2@example.com",
            "home_currency": "EUR",
            "password": "testpassword123"
        }
        response = client.post("/users/", json=user2_data)
        assert response.status_code == 201
        
        # Deactivate user
        client.patch(f"/users/{sample_user.id}/deactivate")
        
        # Try to get deactivated user
        response = client.get(f"/users/{sample_user.id}")
        assert response.status_code == 404
    
    def test_get_user_invalid_id(self, client, db_session):
        """Test getting user with invalid ID format."""
        response = client.get("/users/invalid")
        assert response.status_code == 422

class TestUpdateUser:
    """Test cases for updating users (PATCH /users/{user_id})"""
    
    def test_update_user_name_only(self, client, db_session, sample_user):
        """Test updating only the user name."""
        update_data = {"name": "Updated Name"}
        response = client.patch(f"/users/{sample_user.id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["email"] == sample_user.email  # Should remain unchanged
        assert data["home_currency"] == sample_user.home_currency  # Should remain unchanged
    
    def test_update_user_email_only(self, client, db_session, sample_user):
        """Test updating only the user email."""
        update_data = {"email": "updated@example.com"}
        response = client.patch(f"/users/{sample_user.id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "updated@example.com"
        assert data["name"] == sample_user.name  # Should remain unchanged
        assert data["home_currency"] == sample_user.home_currency  # Should remain unchanged
    
    def test_update_user_currency_only(self, client, db_session, sample_user):
        """Test updating only the home currency."""
        update_data = {"home_currency": "EUR"}
        response = client.patch(f"/users/{sample_user.id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["home_currency"] == "EUR"
        assert data["name"] == sample_user.name  # Should remain unchanged
        assert data["email"] == sample_user.email  # Should remain unchanged
    
    def test_update_user_currency_normalization(self, client, db_session, sample_user):
        """Test that currency is normalized to uppercase during update."""
        update_data = {"home_currency": "eur"}
        response = client.patch(f"/users/{sample_user.id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["home_currency"] == "EUR"
    
    def test_update_user_multiple_fields(self, client, db_session, sample_user):
        """Test updating multiple fields at once."""
        update_data = {
            "name": "Updated Name",
            "email": "updated@example.com",
            "home_currency": "GBP"
        }
        response = client.patch(f"/users/{sample_user.id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["email"] == "updated@example.com"
        assert data["home_currency"] == "GBP"
    
    def test_update_user_duplicate_email(self, client, db_session, sample_user):
        """Test updating user with duplicate email."""
        # Create another user
        user2_data = {
            "name": "User 2",
            "email": "user2@example.com",
            "home_currency": "EUR",
            "password": "testpassword123"
        }
        response = client.post("/users/", json=user2_data)
        user2 = response.json()
        
        # Try to update first user with second user's email
        update_data = {"email": user2["email"]}
        response = client.patch(f"/users/{sample_user.id}", json=update_data)
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]
    
    def test_update_user_invalid_email(self, client, db_session, sample_user):
        """Test updating user with invalid email format."""
        update_data = {"email": "invalid-email"}
        response = client.patch(f"/users/{sample_user.id}", json=update_data)
        assert response.status_code == 422
    
    def test_update_user_name_too_long(self, client, db_session, sample_user):
        """Test updating user with name that's too long."""
        long_name = "a" * 101  # > 100 chars
        update_data = {"name": long_name}
        response = client.patch(f"/users/{sample_user.id}", json=update_data)
        assert response.status_code == 422
    
    def test_update_user_email_too_long(self, client, db_session, sample_user):
        """Test updating user with email that's too long."""
        long_email = "a" * 250 + "@example.com"  # > 255 chars
        update_data = {"email": long_email}
        response = client.patch(f"/users/{sample_user.id}", json=update_data)
        assert response.status_code == 422
    
    def test_update_user_invalid_currency(self, client, db_session, sample_user):
        """Test updating user with invalid currency code."""
        update_data = {"home_currency": "INVALID"}
        response = client.patch(f"/users/{sample_user.id}", json=update_data)
        assert response.status_code == 422
    
    def test_update_user_not_found(self, client, db_session):
        """Test updating a non-existent user."""
        update_data = {"name": "Updated Name"}
        response = client.patch("/users/99999", json=update_data)
        assert response.status_code == 404
    
    def test_update_user_deactivated(self, client, db_session, sample_user):
        """Test updating a deactivated user."""
        # Create another user first to avoid "last user" protection
        user2_data = {
            "name": "User 2",
            "email": "user2@example.com",
            "home_currency": "EUR",
            "password": "testpassword123"
        }
        response = client.post("/users/", json=user2_data)
        assert response.status_code == 201
        
        # Deactivate user
        client.patch(f"/users/{sample_user.id}/deactivate")
        
        # Try to update deactivated user
        update_data = {"name": "Updated Name"}
        response = client.patch(f"/users/{sample_user.id}", json=update_data)
        assert response.status_code == 404
    
    def test_update_user_same_values(self, client, db_session, sample_user):
        """Test updating user with same values (should succeed)."""
        update_data = {
            "name": sample_user.name,
            "email": sample_user.email,
            "home_currency": sample_user.home_currency
        }
        response = client.patch(f"/users/{sample_user.id}", json=update_data)
        assert response.status_code == 200

class TestDeactivateUser:
    """Test cases for deactivating users (PATCH /users/{user_id}/deactivate)"""
    
    def test_deactivate_user_success(self, client, db_session, sample_user):
        """Test successful user deactivation."""
        # Create another user first to avoid "last user" protection
        user2_data = {
            "name": "User 2",
            "email": "user2@example.com",
            "home_currency": "EUR",
            "password": "testpassword123"
        }
        response = client.post("/users/", json=user2_data)
        assert response.status_code == 201
        
        # Now deactivate the first user
        response = client.patch(f"/users/{sample_user.id}/deactivate")
        assert response.status_code == 204
        
        # Verify user is no longer returned in GET requests
        response = client.get(f"/users/{sample_user.id}")
        assert response.status_code == 404
        
        # Verify user is not in the list of all users
        response = client.get("/users/")
        user_ids = [user["id"] for user in response.json()]
        assert sample_user.id not in user_ids
    
    def test_deactivate_user_not_found(self, client, db_session):
        """Test deactivating a non-existent user."""
        response = client.patch("/users/99999/deactivate")
        assert response.status_code == 404
    
    def test_deactivate_user_already_deactivated(self, client, db_session, sample_user):
        """Test deactivating an already deactivated user."""
        # Create another user first to avoid "last user" protection
        user2_data = {
            "name": "User 2",
            "email": "user2@example.com",
            "home_currency": "EUR",
            "password": "testpassword123"
        }
        response = client.post("/users/", json=user2_data)
        assert response.status_code == 201
        
        # Deactivate user first
        client.patch(f"/users/{sample_user.id}/deactivate")
        
        # Try to deactivate again
        response = client.patch(f"/users/{sample_user.id}/deactivate")
        assert response.status_code == 404
    
    def test_deactivate_last_user(self, client, db_session, sample_user):
        """Test deactivating the last active user (should fail)."""
        response = client.patch(f"/users/{sample_user.id}/deactivate")
        assert response.status_code == 400
        assert "Cannot deactivate last active user" in response.json()["detail"]
    
    def test_deactivate_user_with_multiple_users(self, client, db_session, sample_user):
        """Test deactivating user when multiple users exist."""
        # Create another user
        user2_data = {
            "name": "User 2",
            "email": "user2@example.com",
            "home_currency": "EUR",
            "password": "testpassword123"
        }
        response = client.post("/users/", json=user2_data)
        user2 = response.json()
        
        # Now deactivate the first user (should succeed)
        response = client.patch(f"/users/{sample_user.id}/deactivate")
        assert response.status_code == 204
        
        # Verify first user is deactivated
        response = client.get(f"/users/{sample_user.id}")
        assert response.status_code == 404
        
        # Verify second user is still active
        response = client.get(f"/users/{user2['id']}")
        assert response.status_code == 200

class TestActivateUser:
    """Test cases for activating users (PATCH /users/{user_id}/activate)"""
    
    def test_activate_user_success(self, client, db_session, sample_user):
        """Test successful user activation."""
        # Create another user first to avoid "last user" protection
        user2_data = {
            "name": "User 2",
            "email": "user2@example.com",
            "home_currency": "EUR",
            "password": "testpassword123"
        }
        response = client.post("/users/", json=user2_data)
        assert response.status_code == 201
        
        # First deactivate the user
        client.patch(f"/users/{sample_user.id}/deactivate")
        
        # Now activate it
        response = client.patch(f"/users/{sample_user.id}/activate")
        assert response.status_code == 204
        
        # Verify user is active again
        response = client.get(f"/users/{sample_user.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_user.id
    
    def test_activate_user_not_found(self, client, db_session):
        """Test activating a non-existent user."""
        response = client.patch("/users/99999/activate")
        assert response.status_code == 404
    
    def test_activate_user_already_active(self, client, db_session, sample_user):
        """Test activating an already active user."""
        response = client.patch(f"/users/{sample_user.id}/activate")
        assert response.status_code == 404

class TestDatabaseConstraints:
    """Test cases for database constraints and business rules"""
    
    def test_unique_email_constraint(self, client, db_session, sample_user):
        """Test database-level unique email constraint."""
        # Try to create user with same email directly in database
        user2 = models.User(
            name="User 2",
            email=sample_user.email,  # Same email
            home_currency="EUR"
        )
        db_session.add(user2)
        
        with pytest.raises(Exception):  # Should raise IntegrityError
            db_session.commit()
    
    def test_soft_delete_consistency(self, client, db_session, sample_user):
        """Test soft delete consistency constraint."""
        # Create another user first to avoid "last user" protection
        user2_data = {
            "name": "User 2",
            "email": "user2@example.com",
            "home_currency": "EUR",
            "password": "testpassword123"
        }
        response = client.post("/users/", json=user2_data)
        assert response.status_code == 201
        
        # Verify active user has deleted_at = null
        assert sample_user.active == True
        assert sample_user.deleted_at is None
        
        # Deactivate user
        client.patch(f"/users/{sample_user.id}/deactivate")
        
        # Refresh from database and verify constraint
        db_session.refresh(sample_user)
        assert sample_user.active == False
        assert sample_user.deleted_at is not None
    
    def test_currency_length_constraint(self, client, db_session):
        """Test currency length constraint."""
        user_data = {
            "name": "Test User",
            "email": "test@example.com",
            "home_currency": "INVALID",  # Not 3 characters
            "password": "testpassword123"
        }
        response = client.post("/users/", json=user_data)
        assert response.status_code == 422

class TestEdgeCases:
    """Test cases for edge cases and boundary conditions"""
    
    def test_maximum_length_strings(self, client, db_session):
        """Test with maximum length strings."""
        # Maximum length name (100 chars)
        max_name = "a" * 100
        # Maximum length email (250 chars total, which is valid for email-validator)
        max_email = "a" * 240 + "@test.com"  # 250 chars total
        
        user_data = {
            "name": max_name,
            "email": max_email,
            "home_currency": "USD",
            "password": "testpassword123"
        }
        response = client.post("/users/", json=user_data)
        assert response.status_code == 201
    
    def test_currency_case_handling(self, client, db_session):
        """Test currency case handling."""
        currencies = ["usd", "Usd", "USD", "eur", "Eur", "EUR"]
        
        for i, currency in enumerate(currencies):
            user_data = {
                "name": f"User {i}",
                "email": f"user{i}@example.com",
                "home_currency": currency,
                "password": "testpassword123"
            }
            response = client.post("/users/", json=user_data)
            assert response.status_code == 201
            assert response.json()["home_currency"] == currency.upper()
    
    def test_special_characters_in_fields(self, client, db_session):
        """Test special characters in user fields."""
        user_data = {
            "name": "José María O'Connor-Smith",
            "email": "josé.maría+test@example.com",
            "home_currency": "USD",
            "password": "testpassword123"
        }
        response = client.post("/users/", json=user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == user_data["name"]
        assert data["email"] == user_data["email"]

class TestIntegration:
    """Integration tests for user functionality"""
    
    def test_user_lifecycle(self, client, db_session):
        """Test complete user lifecycle: create -> update -> deactivate -> activate."""
        # Create user
        user_data = {
            "name": "Lifecycle User",
            "email": "lifecycle@example.com",
            "home_currency": "USD",
            "password": "testpassword123"
        }
        response = client.post("/users/", json=user_data)
        assert response.status_code == 201
        user = response.json()
        user_id = user["id"]
        
        # Create another user to avoid "last user" protection
        user2_data = {
            "name": "User 2",
            "email": "user2@example.com",
            "home_currency": "EUR",
            "password": "testpassword123"
        }
        response = client.post("/users/", json=user2_data)
        assert response.status_code == 201
        
        # Update user
        update_data = {"name": "Updated Lifecycle User"}
        response = client.patch(f"/users/{user_id}", json=update_data)
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Lifecycle User"
        
        # Deactivate user
        response = client.patch(f"/users/{user_id}/deactivate")
        assert response.status_code == 204
        
        # Verify user is not accessible
        response = client.get(f"/users/{user_id}")
        assert response.status_code == 404
        
        # Activate user
        response = client.patch(f"/users/{user_id}/activate")
        assert response.status_code == 204
        
        # Verify user is accessible again
        response = client.get(f"/users/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Lifecycle User"
    
    def test_multiple_users_operations(self, client, db_session):
        """Test operations with multiple users."""
        # Create multiple users
        users = []
        for i in range(3):
            user_data = {
                "name": f"User {i}",
                "email": f"user{i}@example.com",
                "home_currency": "USD",
                "password": "testpassword123"
            }
            response = client.post("/users/", json=user_data)
            users.append(response.json())
        
        # Verify all users are returned
        response = client.get("/users/")
        assert response.status_code == 200
        assert len(response.json()) == 3
        
        # Deactivate one user
        response = client.patch(f"/users/{users[0]['id']}/deactivate")
        assert response.status_code == 204
        
        # Verify only 2 users are returned
        response = client.get("/users/")
        assert response.status_code == 200
        assert len(response.json()) == 2
        
        # Reactivate the user
        response = client.patch(f"/users/{users[0]['id']}/activate")
        assert response.status_code == 204
        
        # Verify all 3 users are returned again
        response = client.get("/users/")
        assert response.status_code == 200
        assert len(response.json()) == 3
