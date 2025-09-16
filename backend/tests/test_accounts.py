"""
Test cases for account functionality in the finance app backend.
"""

import pytest
from fastapi.testclient import TestClient
from app import models, schemas

class TestAccountCreation:
    """Test cases for account creation"""
    
    def test_create_income_account_success(self, client, db_session, sample_user):
        """Test successful income account creation."""
        account_data = {
            "name": "Salary Income",
            "type": "income",
            "user_id": sample_user.id
        }
        response = client.post("/accounts/", json=account_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == account_data["name"]
        assert data["type"] == account_data["type"]
        assert "id" in data
    
    def test_create_expense_account_success(self, client, db_session, sample_user):
        """Test successful expense account creation."""
        account_data = {
            "name": "Groceries",
            "type": "expense",
            "user_id": sample_user.id
        }
        response = client.post("/accounts/", json=account_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == account_data["name"]
        assert data["type"] == account_data["type"]
    
    def test_create_asset_account_success(self, client, db_session, sample_user):
        """Test successful asset account creation."""
        account_data = {
            "name": "Checking Account",
            "type": "asset",
            "user_id": sample_user.id,
            "currency": "USD",
            "opening_balance": 1000.0,
            "bank_name": "Bank of America"
        }
        response = client.post("/accounts/asset", json=account_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == account_data["name"]
        assert data["type"] == account_data["type"]
        assert data["currency"] == account_data["currency"]
        assert data["opening_balance"] == account_data["opening_balance"]
    
    def test_create_liability_account_success(self, client, db_session, sample_user):
        """Test successful liability account creation."""
        account_data = {
            "name": "Credit Card",
            "type": "liability",
            "user_id": sample_user.id,
            "currency": "USD",
            "opening_balance": 500.0,
            "bank_name": "Chase",
            "billing_day": 15,
            "due_day": 10
        }
        response = client.post("/accounts/liability", json=account_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == account_data["name"]
        assert data["type"] == account_data["type"]
        assert data["billing_day"] == account_data["billing_day"]
        assert data["due_day"] == account_data["due_day"]
    
    def test_create_account_missing_required_fields(self, client, db_session, sample_user):
        """Test account creation with missing required fields."""
        # Missing name
        response = client.post("/accounts/", json={
            "type": "income",
            "user_id": sample_user.id
        })
        assert response.status_code == 422
        
        # Missing type
        response = client.post("/accounts/", json={
            "name": "Test Account",
            "user_id": sample_user.id
        })
        assert response.status_code == 422
    
    def test_create_asset_account_missing_currency(self, client, db_session, sample_user):
        """Test asset account creation without currency."""
        account_data = {
            "name": "Test Asset",
            "type": "asset",
            "user_id": sample_user.id,
            "opening_balance": 100.0
        }
        response = client.post("/accounts/asset", json=account_data)
        assert response.status_code == 422
    
    def test_create_account_duplicate_name(self, client, db_session, sample_user):
        """Test account creation with duplicate name."""
        account_data = {
            "name": "Duplicate Account",
            "type": "income",
            "user_id": sample_user.id
        }
        # Create first account
        response = client.post("/accounts/", json=account_data)
        assert response.status_code == 201
        
        # Try to create duplicate
        response = client.post("/accounts/", json=account_data)
        assert response.status_code == 409
    
    def test_create_account_invalid_type(self, client, db_session, sample_user):
        """Test account creation with invalid type."""
        account_data = {
            "name": "Test Account",
            "type": "invalid_type",
            "user_id": sample_user.id
        }
        response = client.post("/accounts/", json=account_data)
        assert response.status_code == 422

class TestGetAccounts:
    """Test cases for getting accounts"""
    
    def test_get_all_accounts_empty(self, client, db_session, sample_user):
        """Test getting all accounts when no accounts exist."""
        response = client.get("/accounts/", headers={"Authorization": f"Bearer {sample_user.id}"})
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_all_accounts_multiple(self, client, db_session, sample_user):
        """Test getting all accounts when multiple accounts exist."""
        # Create multiple accounts
        accounts_data = [
            {"name": "Account 1", "type": "income", "user_id": sample_user.id},
            {"name": "Account 2", "type": "expense", "user_id": sample_user.id},
            {"name": "Account 3", "type": "asset", "user_id": sample_user.id, "currency": "USD"}
        ]
        
        for account_data in accounts_data:
            if account_data["type"] in ["asset", "liability"]:
                response = client.post("/accounts/asset", json=account_data)
            else:
                response = client.post("/accounts/", json=account_data)
            assert response.status_code == 201
        
        # Get all accounts
        response = client.get("/accounts/", headers={"Authorization": f"Bearer {sample_user.id}"})
        assert response.status_code == 200
        accounts = response.json()
        assert len(accounts) == 3
    
    def test_get_account_success(self, client, db_session, sample_user):
        """Test getting a specific account by ID."""
        # Create account
        account_data = {
            "name": "Test Account",
            "type": "income",
            "user_id": sample_user.id
        }
        response = client.post("/accounts/", json=account_data)
        account = response.json()
        
        # Get account
        response = client.get(f"/accounts/{account['id']}", headers={"Authorization": f"Bearer {sample_user.id}"})
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == account["id"]
        assert data["name"] == account["name"]
    
    def test_get_account_not_found(self, client, db_session, sample_user):
        """Test getting a non-existent account."""
        response = client.get("/accounts/99999", headers={"Authorization": f"Bearer {sample_user.id}"})
        assert response.status_code == 404

class TestUpdateAccount:
    """Test cases for updating accounts"""
    
    def test_update_account_name_only(self, client, db_session, sample_user):
        """Test updating only the account name."""
        # Create account
        account_data = {
            "name": "Original Name",
            "type": "income",
            "user_id": sample_user.id
        }
        response = client.post("/accounts/", json=account_data)
        account = response.json()
        
        # Update name
        update_data = {"name": "Updated Name"}
        response = client.patch(f"/accounts/{account['id']}", json=update_data, headers={"Authorization": f"Bearer {sample_user.id}"})
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["type"] == account["type"]  # Should remain unchanged
    
    def test_update_account_type(self, client, db_session, sample_user):
        """Test updating account type."""
        # Create account
        account_data = {
            "name": "Test Account",
            "type": "income",
            "user_id": sample_user.id
        }
        response = client.post("/accounts/", json=account_data)
        account = response.json()
        
        # Update type
        update_data = {"type": "expense"}
        response = client.patch(f"/accounts/{account['id']}", json=update_data, headers={"Authorization": f"Bearer {sample_user.id}"})
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "expense"
    
    def test_update_account_not_found(self, client, db_session, sample_user):
        """Test updating a non-existent account."""
        update_data = {"name": "Updated Name"}
        response = client.patch("/accounts/99999", json=update_data, headers={"Authorization": f"Bearer {sample_user.id}"})
        assert response.status_code == 404

class TestDeactivateAccount:
    """Test cases for deactivating accounts"""
    
    def test_deactivate_account_success(self, client, db_session, sample_user):
        """Test successful account deactivation."""
        # Create account
        account_data = {
            "name": "To Deactivate",
            "type": "income",
            "user_id": sample_user.id
        }
        response = client.post("/accounts/", json=account_data)
        account = response.json()
        
        # Deactivate account
        response = client.patch(f"/accounts/{account['id']}/deactivate", headers={"Authorization": f"Bearer {sample_user.id}"})
        assert response.status_code == 204
        
        # Verify account is deactivated (not found in active list)
        response = client.get("/accounts/", headers={"Authorization": f"Bearer {sample_user.id}"})
        assert account['id'] not in [acc['id'] for acc in response.json()]
    
    def test_deactivate_account_not_found(self, client, db_session, sample_user):
        """Test deactivating a non-existent account."""
        response = client.patch("/accounts/99999/deactivate", headers={"Authorization": f"Bearer {sample_user.id}"})
        assert response.status_code == 404

class TestActivateAccount:
    """Test cases for activating accounts"""
    
    def test_activate_account_success(self, client, db_session, sample_user):
        """Test successful account activation."""
        # Create account
        account_data = {
            "name": "To Activate",
            "type": "income",
            "user_id": sample_user.id
        }
        response = client.post("/accounts/", json=account_data)
        account = response.json()
        
        # Deactivate account first
        response = client.patch(f"/accounts/{account['id']}/deactivate", headers={"Authorization": f"Bearer {sample_user.id}"})
        assert response.status_code == 204
        
        # Activate account
        response = client.patch(f"/accounts/{account['id']}/activate", headers={"Authorization": f"Bearer {sample_user.id}"})
        assert response.status_code == 204
        
        # Verify account is active again
        response = client.get("/accounts/", headers={"Authorization": f"Bearer {sample_user.id}"})
        assert account['id'] in [acc['id'] for acc in response.json()]
    
    def test_activate_account_not_found(self, client, db_session, sample_user):
        """Test activating a non-existent account."""
        response = client.patch("/accounts/99999/activate", headers={"Authorization": f"Bearer {sample_user.id}"})
        assert response.status_code == 404

class TestAccountValidation:
    """Test cases for account validation and business rules"""
    
    def test_asset_account_currency_required(self, client, db_session, sample_user):
        """Test that currency is required for asset accounts."""
        account_data = {
            "name": "Asset Account",
            "type": "asset",
            "user_id": sample_user.id,
            "opening_balance": 100.0
            # Missing currency
        }
        response = client.post("/accounts/asset", json=account_data)
        assert response.status_code == 422
    
    def test_liability_account_billing_day_validation(self, client, db_session, sample_user):
        """Test billing day validation for liability accounts."""
        account_data = {
            "name": "Credit Card",
            "type": "liability",
            "user_id": sample_user.id,
            "currency": "USD",
            "billing_day": 32  # Invalid day
        }
        response = client.post("/accounts/liability", json=account_data)
        assert response.status_code == 422
    
    def test_liability_account_due_day_validation(self, client, db_session, sample_user):
        """Test due day validation for liability accounts."""
        account_data = {
            "name": "Credit Card",
            "type": "liability",
            "user_id": sample_user.id,
            "currency": "USD",
            "due_day": 0  # Invalid day
        }
        response = client.post("/accounts/liability", json=account_data)
        assert response.status_code == 422
    
    def test_income_expense_account_no_currency(self, client, db_session, sample_user):
        """Test that income/expense accounts don't require currency."""
        account_data = {
            "name": "Income Account",
            "type": "income",
            "user_id": sample_user.id,
            "currency": "USD"  # Should not be allowed
        }
        response = client.post("/accounts/", json=account_data)
        assert response.status_code == 422

class TestAccountEdgeCases:
    """Test cases for edge cases and boundary conditions"""
    
    def test_account_name_maximum_length(self, client, db_session, sample_user):
        """Test account name at maximum length."""
        max_name = "a" * 100  # Maximum length
        account_data = {
            "name": max_name,
            "type": "income",
            "user_id": sample_user.id
        }
        response = client.post("/accounts/", json=account_data)
        assert response.status_code == 201
    
    def test_account_name_too_long(self, client, db_session, sample_user):
        """Test account name that's too long."""
        long_name = "a" * 101  # Too long
        account_data = {
            "name": long_name,
            "type": "income",
            "user_id": sample_user.id
        }
        response = client.post("/accounts/", json=account_data)
        assert response.status_code == 422
    
    def test_currency_case_handling(self, client, db_session, sample_user):
        """Test currency case handling."""
        currencies = ["usd", "Usd", "USD", "eur", "Eur", "EUR"]
        
        for i, currency in enumerate(currencies):
            account_data = {
                "name": f"Account {i}",
                "type": "asset",
                "user_id": sample_user.id,
                "currency": currency
            }
            response = client.post("/accounts/asset", json=account_data)
            assert response.status_code == 201
            assert response.json()["currency"] == currency.upper()
    
    def test_opening_balance_negative(self, client, db_session, sample_user):
        """Test negative opening balance."""
        account_data = {
            "name": "Test Account",
            "type": "asset",
            "user_id": sample_user.id,
            "currency": "USD",
            "opening_balance": -100.0  # Negative balance
        }
        response = client.post("/accounts/asset", json=account_data)
        assert response.status_code == 422

class TestAccountIntegration:
    """Integration tests for account functionality"""
    
    def test_account_lifecycle(self, client, db_session, sample_user):
        """Test complete account lifecycle: create -> update -> deactivate -> activate."""
        # Create account
        account_data = {
            "name": "Lifecycle Account",
            "type": "income",
            "user_id": sample_user.id
        }
        response = client.post("/accounts/", json=account_data)
        assert response.status_code == 201
        account = response.json()
        account_id = account["id"]
        
        # Update account
        update_data = {"name": "Updated Lifecycle Account"}
        response = client.patch(f"/accounts/{account_id}", json=update_data, headers={"Authorization": f"Bearer {sample_user.id}"})
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Lifecycle Account"
        
        # Deactivate account
        response = client.patch(f"/accounts/{account_id}/deactivate", headers={"Authorization": f"Bearer {sample_user.id}"})
        assert response.status_code == 204
        
        # Verify account is deactivated
        response = client.get("/accounts/", headers={"Authorization": f"Bearer {sample_user.id}"})
        assert account_id not in [acc['id'] for acc in response.json()]
        
        # Activate account
        response = client.patch(f"/accounts/{account_id}/activate", headers={"Authorization": f"Bearer {sample_user.id}"})
        assert response.status_code == 204
        
        # Verify account is active again
        response = client.get("/accounts/", headers={"Authorization": f"Bearer {sample_user.id}"})
        assert account_id in [acc['id'] for acc in response.json()]
    
    def test_multiple_account_types(self, client, db_session, sample_user):
        """Test creating multiple account types."""
        account_types = [
            {"name": "Income", "type": "income", "user_id": sample_user.id},
            {"name": "Expense", "type": "expense", "user_id": sample_user.id},
            {"name": "Asset", "type": "asset", "user_id": sample_user.id, "currency": "USD"},
            {"name": "Liability", "type": "liability", "user_id": sample_user.id, "currency": "USD"}
        ]
        
        for account_data in account_types:
            if account_data["type"] in ["asset", "liability"]:
                response = client.post("/accounts/asset", json=account_data)
            else:
                response = client.post("/accounts/", json=account_data)
            assert response.status_code == 201
        
        # Verify all accounts exist
        response = client.get("/accounts/", headers={"Authorization": f"Bearer {sample_user.id}"})
        assert response.status_code == 200
        assert len(response.json()) == 4
