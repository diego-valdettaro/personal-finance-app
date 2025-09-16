"""
Test cases for people functionality in the finance app backend.
"""

import pytest
from fastapi.testclient import TestClient
from app import models, schemas

class TestPersonCreation:
    """Test cases for person creation"""
    
    def test_create_person_success(self, client, db_session, sample_user):
        """Test successful person creation."""
        person_data = {
            "name": "John Doe",
            "is_me": False,
            "user_id": sample_user.id
        }
        response = client.post("/people/", json=person_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == person_data["name"]
        assert data["is_me"] == person_data["is_me"]
        assert "id" in data
    
    def test_create_person_is_me_true(self, client, db_session, sample_user):
        """Test creating a person marked as 'me'."""
        person_data = {
            "name": "Myself",
            "is_me": True,
            "user_id": sample_user.id
        }
        response = client.post("/people/", json=person_data)
        assert response.status_code == 201
        data = response.json()
        assert data["is_me"] == True
    
    def test_create_person_default_is_me(self, client, db_session, sample_user):
        """Test person creation with default is_me value."""
        person_data = {
            "name": "Default Person",
            "user_id": sample_user.id
        }
        response = client.post("/people/", json=person_data)
        assert response.status_code == 201
        data = response.json()
        assert data["is_me"] == False  # Default value
    
    def test_create_person_missing_required_fields(self, client, db_session, sample_user):
        """Test person creation with missing required fields."""
        # Missing name
        response = client.post("/people/", json={
            "is_me": False,
            "user_id": sample_user.id
        })
        assert response.status_code == 422
        
        # Missing user_id
        response = client.post("/people/", json={
            "name": "Test Person",
            "is_me": False
        })
        assert response.status_code == 422
    
    def test_create_person_name_too_long(self, client, db_session, sample_user):
        """Test person creation with name that's too long."""
        long_name = "a" * 101  # > 100 chars
        person_data = {
            "name": long_name,
            "user_id": sample_user.id
        }
        response = client.post("/people/", json=person_data)
        assert response.status_code == 422
    
    def test_create_person_duplicate_name(self, client, db_session, sample_user):
        """Test person creation with duplicate name."""
        person_data = {
            "name": "Duplicate Name",
            "user_id": sample_user.id
        }
        # Create first person
        response = client.post("/people/", json=person_data)
        assert response.status_code == 201
        
        # Try to create duplicate
        response = client.post("/people/", json=person_data)
        assert response.status_code == 409
    
    def test_create_person_duplicate_is_me(self, client, db_session, sample_user):
        """Test creating multiple people marked as 'me'."""
        person_data = {
            "name": "First Me",
            "is_me": True,
            "user_id": sample_user.id
        }
        # Create first "me" person
        response = client.post("/people/", json=person_data)
        assert response.status_code == 201
        
        # Try to create second "me" person
        person_data["name"] = "Second Me"
        response = client.post("/people/", json=person_data)
        assert response.status_code == 409
    
    def test_create_person_empty_name(self, client, db_session, sample_user):
        """Test person creation with empty name."""
        person_data = {
            "name": "",
            "user_id": sample_user.id
        }
        response = client.post("/people/", json=person_data)
        assert response.status_code == 422

class TestGetPeople:
    """Test cases for getting people"""
    
    def test_get_all_people_empty(self, client, db_session):
        """Test getting all people when no people exist."""
        response = client.get("/people/")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_all_people_multiple(self, client, db_session, sample_user):
        """Test getting all people when multiple people exist."""
        # Create multiple people
        people_data = [
            {"name": "Person 1", "user_id": sample_user.id},
            {"name": "Person 2", "user_id": sample_user.id},
            {"name": "Person 3", "user_id": sample_user.id}
        ]
        
        for person_data in people_data:
            response = client.post("/people/", json=person_data)
            assert response.status_code == 201
        
        # Get all people
        response = client.get("/people/")
        assert response.status_code == 200
        people = response.json()
        assert len(people) == 3
    
    def test_get_person_success(self, client, db_session, sample_user):
        """Test getting a specific person by ID."""
        # Create person
        person_data = {
            "name": "Test Person",
            "user_id": sample_user.id
        }
        response = client.post("/people/", json=person_data)
        person = response.json()
        
        # Get person
        response = client.get(f"/people/{person['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == person["id"]
        assert data["name"] == person["name"]
    
    def test_get_person_not_found(self, client, db_session):
        """Test getting a non-existent person."""
        response = client.get("/people/99999")
        assert response.status_code == 404

class TestUpdatePerson:
    """Test cases for updating people"""
    
    def test_update_person_name_only(self, client, db_session, sample_user):
        """Test updating only the person name."""
        # Create person
        person_data = {
            "name": "Original Name",
            "user_id": sample_user.id
        }
        response = client.post("/people/", json=person_data)
        person = response.json()
        
        # Update name
        update_data = {"name": "Updated Name"}
        response = client.patch(f"/people/{person['id']}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["is_me"] == person["is_me"]  # Should remain unchanged
    
    def test_update_person_is_me(self, client, db_session, sample_user):
        """Test updating person is_me status."""
        # Create person
        person_data = {
            "name": "Test Person",
            "is_me": False,
            "user_id": sample_user.id
        }
        response = client.post("/people/", json=person_data)
        person = response.json()
        
        # Update is_me
        update_data = {"is_me": True}
        response = client.patch(f"/people/{person['id']}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["is_me"] == True
    
    def test_update_person_multiple_fields(self, client, db_session, sample_user):
        """Test updating multiple fields at once."""
        # Create person
        person_data = {
            "name": "Original Name",
            "is_me": False,
            "user_id": sample_user.id
        }
        response = client.post("/people/", json=person_data)
        person = response.json()
        
        # Update multiple fields
        update_data = {
            "name": "Updated Name",
            "is_me": True
        }
        response = client.patch(f"/people/{person['id']}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["is_me"] == True
    
    def test_update_person_duplicate_name(self, client, db_session, sample_user):
        """Test updating person with duplicate name."""
        # Create two people
        person1_data = {"name": "Person 1", "user_id": sample_user.id}
        person2_data = {"name": "Person 2", "user_id": sample_user.id}
        
        response = client.post("/people/", json=person1_data)
        person1 = response.json()
        response = client.post("/people/", json=person2_data)
        person2 = response.json()
        
        # Try to update person2 with person1's name
        update_data = {"name": person1["name"]}
        response = client.patch(f"/people/{person2['id']}", json=update_data)
        assert response.status_code == 409
    
    def test_update_person_duplicate_is_me(self, client, db_session, sample_user):
        """Test updating person to duplicate is_me status."""
        # Create two people, one marked as "me"
        person1_data = {"name": "Person 1", "is_me": True, "user_id": sample_user.id}
        person2_data = {"name": "Person 2", "is_me": False, "user_id": sample_user.id}
        
        response = client.post("/people/", json=person1_data)
        person1 = response.json()
        response = client.post("/people/", json=person2_data)
        person2 = response.json()
        
        # Try to update person2 to also be "me"
        update_data = {"is_me": True}
        response = client.patch(f"/people/{person2['id']}", json=update_data)
        assert response.status_code == 409
    
    def test_update_person_not_found(self, client, db_session):
        """Test updating a non-existent person."""
        update_data = {"name": "Updated Name"}
        response = client.patch("/people/99999", json=update_data)
        assert response.status_code == 404
    
    def test_update_person_same_values(self, client, db_session, sample_user):
        """Test updating person with same values (should succeed)."""
        # Create person
        person_data = {
            "name": "Test Person",
            "is_me": False,
            "user_id": sample_user.id
        }
        response = client.post("/people/", json=person_data)
        person = response.json()
        
        # Update with same values
        update_data = {
            "name": person["name"],
            "is_me": person["is_me"]
        }
        response = client.patch(f"/people/{person['id']}", json=update_data)
        assert response.status_code == 200

class TestDeactivatePerson:
    """Test cases for deactivating people"""
    
    def test_deactivate_person_success(self, client, db_session, sample_user):
        """Test successful person deactivation."""
        # Create person
        person_data = {
            "name": "To Deactivate",
            "user_id": sample_user.id
        }
        response = client.post("/people/", json=person_data)
        person = response.json()
        
        # Deactivate person
        response = client.patch(f"/people/{person['id']}/deactivate")
        assert response.status_code == 204
        
        # Verify person is deactivated (not found in active list)
        response = client.get("/people/")
        assert person['id'] not in [p['id'] for p in response.json()]
    
    def test_deactivate_person_not_found(self, client, db_session):
        """Test deactivating a non-existent person."""
        response = client.patch("/people/99999/deactivate")
        assert response.status_code == 404

class TestActivatePerson:
    """Test cases for activating people"""
    
    def test_activate_person_success(self, client, db_session, sample_user):
        """Test successful person activation."""
        # Create person
        person_data = {
            "name": "To Activate",
            "user_id": sample_user.id
        }
        response = client.post("/people/", json=person_data)
        person = response.json()
        
        # Deactivate person first
        response = client.patch(f"/people/{person['id']}/deactivate")
        assert response.status_code == 204
        
        # Activate person
        response = client.patch(f"/people/{person['id']}/activate")
        assert response.status_code == 204
        
        # Verify person is active again
        response = client.get("/people/")
        assert person['id'] in [p['id'] for p in response.json()]
    
    def test_activate_person_not_found(self, client, db_session):
        """Test activating a non-existent person."""
        response = client.patch("/people/99999/activate")
        assert response.status_code == 404

class TestPersonValidation:
    """Test cases for person validation and business rules"""
    
    def test_person_name_maximum_length(self, client, db_session, sample_user):
        """Test person name at maximum length."""
        max_name = "a" * 100  # Maximum length
        person_data = {
            "name": max_name,
            "user_id": sample_user.id
        }
        response = client.post("/people/", json=person_data)
        assert response.status_code == 201
    
    def test_person_name_too_long(self, client, db_session, sample_user):
        """Test person name that's too long."""
        long_name = "a" * 101  # Too long
        person_data = {
            "name": long_name,
            "user_id": sample_user.id
        }
        response = client.post("/people/", json=person_data)
        assert response.status_code == 422
    
    def test_special_characters_in_name(self, client, db_session, sample_user):
        """Test special characters in person name."""
        person_data = {
            "name": "José María O'Connor-Smith",
            "user_id": sample_user.id
        }
        response = client.post("/people/", json=person_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == person_data["name"]

class TestPersonEdgeCases:
    """Test cases for edge cases and boundary conditions"""
    
    def test_multiple_people_same_user(self, client, db_session, sample_user):
        """Test creating multiple people for the same user."""
        people_data = [
            {"name": "Person 1", "user_id": sample_user.id},
            {"name": "Person 2", "user_id": sample_user.id},
            {"name": "Person 3", "user_id": sample_user.id}
        ]
        
        for person_data in people_data:
            response = client.post("/people/", json=person_data)
            assert response.status_code == 201
        
        # Verify all people exist
        response = client.get("/people/")
        assert response.status_code == 200
        assert len(response.json()) == 3
    
    def test_person_with_me_flag(self, client, db_session, sample_user):
        """Test person with is_me flag set to true."""
        person_data = {
            "name": "Myself",
            "is_me": True,
            "user_id": sample_user.id
        }
        response = client.post("/people/", json=person_data)
        assert response.status_code == 201
        data = response.json()
        assert data["is_me"] == True

class TestPersonIntegration:
    """Integration tests for person functionality"""
    
    def test_person_lifecycle(self, client, db_session, sample_user):
        """Test complete person lifecycle: create -> update -> deactivate -> activate."""
        # Create person
        person_data = {
            "name": "Lifecycle Person",
            "user_id": sample_user.id
        }
        response = client.post("/people/", json=person_data)
        assert response.status_code == 201
        person = response.json()
        person_id = person["id"]
        
        # Update person
        update_data = {"name": "Updated Lifecycle Person"}
        response = client.patch(f"/people/{person_id}", json=update_data)
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Lifecycle Person"
        
        # Deactivate person
        response = client.patch(f"/people/{person_id}/deactivate")
        assert response.status_code == 204
        
        # Verify person is deactivated
        response = client.get("/people/")
        assert person_id not in [p['id'] for p in response.json()]
        
        # Activate person
        response = client.patch(f"/people/{person_id}/activate")
        assert response.status_code == 204
        
        # Verify person is active again
        response = client.get("/people/")
        assert person_id in [p['id'] for p in response.json()]
    
    def test_person_me_constraint(self, client, db_session, sample_user):
        """Test the constraint that only one person can be marked as 'me'."""
        # Create first person marked as "me"
        person1_data = {
            "name": "First Me",
            "is_me": True,
            "user_id": sample_user.id
        }
        response = client.post("/people/", json=person1_data)
        assert response.status_code == 201
        
        # Try to create second person marked as "me"
        person2_data = {
            "name": "Second Me",
            "is_me": True,
            "user_id": sample_user.id
        }
        response = client.post("/people/", json=person2_data)
        assert response.status_code == 409
        
        # Verify only one person exists
        response = client.get("/people/")
        assert response.status_code == 200
        assert len(response.json()) == 1
