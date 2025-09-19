"""
Test cases for budget functionality in the finance app backend.
"""

class TestBudgetCreation:
    """Test cases for budget creation"""
    
    def test_create_budget_success(self, client, sample_user, sample_accounts):
        """Test successful budget creation."""
        budget_data = {
            "user_id": sample_user.id,
            "name": "2024 Budget",
            "year": 2024,
            "lines": [
                {
                    "month": 1,
                    "account_id": sample_accounts["income"].id,
                    "amount_oc": 5000.00,
                    "currency": "USD",
                    "amount_hc": 5000.00,
                    "description": "Salary"
                },
                {
                    "month": 1,
                    "account_id": sample_accounts["expense"].id,
                    "amount_oc": 2000.00,
                    "currency": "USD",
                    "amount_hc": 2000.00,
                    "description": "Monthly expenses"
                }
            ]
        }
        response = client.post(f"/users/{sample_user.id}/budgets/", json=budget_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == budget_data["name"]
        assert data["year"] == budget_data["year"]
        assert len(data["budget_lines"]) == 2
        assert "id" in data
    
    def test_create_budget_missing_required_fields(self, client, sample_user):
        """Test budget creation with missing required fields."""
        # Missing name
        budget_data = {
            "user_id": sample_user.id,
            "year": 2024,
            "lines": []
        }
        response = client.post(f"/users/{sample_user.id}/budgets/", json=budget_data)
        assert response.status_code == 422
        
        # Missing year
        budget_data = {
            "user_id": sample_user.id,
            "name": "2024 Budget",
            "lines": []
        }
        response = client.post(f"/users/{sample_user.id}/budgets/", json=budget_data)
        assert response.status_code == 422
    
    def test_create_budget_invalid_month(self, client, sample_user, sample_accounts):
        """Test budget creation with invalid month."""
        budget_data = {
            "user_id": sample_user.id,
            "name": "2024 Budget",
            "year": 2024,
            "lines": [
                {
                    "month": 13,  # Invalid month
                    "account_id": sample_accounts["income"].id,
                    "amount_oc": 5000.00,
                    "currency": "USD",
                    "amount_hc": 5000.00
                }
            ]
        }
        response = client.post(f"/users/{sample_user.id}/budgets/", json=budget_data)
        assert response.status_code == 422
    
    def test_create_budget_duplicate_name_year(self, client, sample_user, sample_accounts):
        """Test budget creation with duplicate name and year."""
        budget_data = {
            "user_id": sample_user.id,
            "name": "2024 Budget",
            "year": 2024,
            "lines": []
        }
        # Create first budget
        response = client.post(f"/users/{sample_user.id}/budgets/", json=budget_data)
        assert response.status_code == 200
        
        # Try to create duplicate
        response = client.post(f"/users/{sample_user.id}/budgets/", json=budget_data)
        assert response.status_code == 409

class TestGetBudgets:
    """Test cases for getting budgets"""
    
    def test_get_budget_success(self, client, sample_user, sample_accounts):
        """Test getting a specific budget."""
        # Create budget first
        budget_data = {
            "user_id": sample_user.id,
            "name": "2024 Budget",
            "year": 2024,
            "lines": [
                {
                    "month": 1,
                    "account_id": sample_accounts["income"].id,
                    "amount_oc": 5000.00,
                    "currency": "USD",
                    "amount_hc": 5000.00
                }
            ]
        }
        response = client.post(f"/users/{sample_user.id}/budgets/", json=budget_data)
        budget = response.json()
        
        # Get budget
        response = client.get(f"/users/{sample_user.id}/budgets/{budget['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == budget["id"]
        assert data["name"] == budget["name"]
    
    def test_get_budget_not_found(self, client, sample_user):
        """Test getting a non-existent budget."""
        response = client.get(f"/users/{sample_user.id}/budgets/99999")
        assert response.status_code == 404
    
    def test_get_budget_month_success(self, client, sample_user, sample_accounts):
        """Test getting a specific month of a budget."""
        # Create budget first
        budget_data = {
            "user_id": sample_user.id,
            "name": "2024 Budget",
            "year": 2024,
            "lines": [
                {
                    "month": 1,
                    "account_id": sample_accounts["income"].id,
                    "amount_oc": 5000.00,
                    "currency": "USD",
                    "amount_hc": 5000.00
                }
            ]
        }
        response = client.post(f"/users/{sample_user.id}/budgets/", json=budget_data)
        budget = response.json()
        
        # Get budget month
        response = client.get(f"/users/{sample_user.id}/budgets/{budget['id']}/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == budget["id"]
        assert len(data["budget_lines"]) == 1
        assert data["budget_lines"][0]["month"] == 1

class TestUpdateBudget:
    """Test cases for updating budgets"""
    
    def test_update_budget_success(self, client, sample_user, sample_accounts):
        """Test successful budget update."""
        # Create budget first
        budget_data = {
            "user_id": sample_user.id,
            "name": "2024 Budget",
            "year": 2024,
            "lines": [
                {
                    "month": 1,
                    "account_id": sample_accounts["income"].id,
                    "amount_oc": 5000.00,
                    "currency": "USD",
                    "amount_hc": 5000.00
                }
            ]
        }
        response = client.post(f"/users/{sample_user.id}/budgets/", json=budget_data)
        budget = response.json()
        
        # Update budget
        update_data = {
            "name": "Updated 2024 Budget",
            "lines": [
                {
                    "month": 1,
                    "account_id": sample_accounts["income"].id,
                    "amount_oc": 6000.00,
                    "currency": "USD",
                    "amount_hc": 6000.00
                }
            ]
        }
        response = client.patch(f"/users/{sample_user.id}/budgets/{budget['id']}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated 2024 Budget"
    
    def test_update_budget_not_found(self, client, sample_user):
        """Test updating a non-existent budget."""
        update_data = {
            "name": "Updated Budget",
            "lines": []
        }
        response = client.patch(f"/users/{sample_user.id}/budgets/99999", json=update_data)
        assert response.status_code == 404
    
    def test_update_budget_name_only(self, client, sample_user, sample_accounts):
        """Test updating only the budget name."""
        # Create budget first
        budget_data = {
            "user_id": sample_user.id,
            "name": "2024 Budget",
            "year": 2024,
            "lines": [
                {
                    "month": 1,
                    "account_id": sample_accounts["income"].id,
                    "amount_oc": 5000.00,
                    "currency": "USD",
                    "amount_hc": 5000.00
                }
            ]
        }
        response = client.post(f"/users/{sample_user.id}/budgets/", json=budget_data)
        budget = response.json()
        
        # Update only name
        update_data = {"name": "Updated Budget Name"}
        response = client.patch(f"/users/{sample_user.id}/budgets/{budget['id']}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Budget Name"
        assert data["year"] == 2024  # Should remain unchanged
        assert len(data["budget_lines"]) == 1  # Lines should remain unchanged
    
    def test_update_budget_year_only(self, client, sample_user, sample_accounts):
        """Test updating only the budget year."""
        # Create budget first
        budget_data = {
            "user_id": sample_user.id,
            "name": "2024 Budget",
            "year": 2024,
            "lines": [
                {
                    "month": 1,
                    "account_id": sample_accounts["income"].id,
                    "amount_oc": 5000.00,
                    "currency": "USD",
                    "amount_hc": 5000.00
                }
            ]
        }
        response = client.post(f"/users/{sample_user.id}/budgets/", json=budget_data)
        budget = response.json()
        
        # Update only year
        update_data = {"year": 2025}
        response = client.patch(f"/users/{sample_user.id}/budgets/{budget['id']}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["year"] == 2025
        assert data["name"] == "2024 Budget"  # Should remain unchanged
        assert len(data["budget_lines"]) == 1  # Lines should remain unchanged
    
    def test_update_budget_lines_only(self, client, sample_user, sample_accounts):
        """Test updating only the budget lines."""
        # Create budget first
        budget_data = {
            "user_id": sample_user.id,
            "name": "2024 Budget",
            "year": 2024,
            "lines": [
                {
                    "month": 1,
                    "account_id": sample_accounts["income"].id,
                    "amount_oc": 5000.00,
                    "currency": "USD",
                    "amount_hc": 5000.00
                }
            ]
        }
        response = client.post(f"/users/{sample_user.id}/budgets/", json=budget_data)
        budget = response.json()
        
        # Update only lines
        update_data = {
            "lines": [
                {
                    "month": 2,
                    "account_id": sample_accounts["expense"].id,
                    "amount_oc": 3000.00,
                    "currency": "USD",
                    "amount_hc": 3000.00
                },
                {
                    "month": 3,
                    "account_id": sample_accounts["asset"].id,
                    "amount_oc": 2000.00,
                    "currency": "USD",
                    "amount_hc": 2000.00
                }
            ]
        }
        response = client.patch(f"/users/{sample_user.id}/budgets/{budget['id']}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "2024 Budget"  # Should remain unchanged
        assert data["year"] == 2024  # Should remain unchanged
        assert len(data["budget_lines"]) == 2  # Should have new lines
        # Lines might be sorted by month
        months = [line["month"] for line in data["budget_lines"]]
        assert 2 in months
        assert 3 in months
    
    def test_update_budget_empty_data(self, client, sample_user, sample_accounts):
        """Test updating budget with empty data (should not change anything)."""
        # Create budget first
        budget_data = {
            "user_id": sample_user.id,
            "name": "2024 Budget",
            "year": 2024,
            "lines": [
                {
                    "month": 1,
                    "account_id": sample_accounts["income"].id,
                    "amount_oc": 5000.00,
                    "currency": "USD",
                    "amount_hc": 5000.00
                }
            ]
        }
        response = client.post(f"/users/{sample_user.id}/budgets/", json=budget_data)
        budget = response.json()
        
        # Update with empty data
        update_data = {}
        response = client.patch(f"/users/{sample_user.id}/budgets/{budget['id']}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "2024 Budget"  # Should remain unchanged
        assert data["year"] == 2024  # Should remain unchanged
        assert len(data["budget_lines"]) == 1  # Should remain unchanged
    
    def test_update_budget_invalid_year(self, client, sample_user, sample_accounts):
        """Test updating budget with invalid year."""
        # Create budget first
        budget_data = {
            "user_id": sample_user.id,
            "name": "2024 Budget",
            "year": 2024,
            "lines": []
        }
        response = client.post(f"/users/{sample_user.id}/budgets/", json=budget_data)
        budget = response.json()
        
        # Update with invalid year
        update_data = {"year": 1800}  # Too old
        response = client.patch(f"/users/{sample_user.id}/budgets/{budget['id']}", json=update_data)
        assert response.status_code == 422
    
    def test_update_budget_duplicate_name_year(self, client, sample_user, sample_accounts):
        """Test updating budget with duplicate name and year."""
        # Create two budgets
        budget1_data = {
            "user_id": sample_user.id,
            "name": "2024 Budget",
            "year": 2024,
            "lines": []
        }
        response = client.post(f"/users/{sample_user.id}/budgets/", json=budget1_data)
        budget1 = response.json()
        
        budget2_data = {
            "user_id": sample_user.id,
            "name": "2025 Budget",
            "year": 2025,
            "lines": []
        }
        response = client.post(f"/users/{sample_user.id}/budgets/", json=budget2_data)
        budget2 = response.json()
        
        # Try to update budget2 with budget1's name and year
        update_data = {"name": "2024 Budget", "year": 2024}
        response = client.patch(f"/users/{sample_user.id}/budgets/{budget2['id']}", json=update_data)
        assert response.status_code == 409  # Conflict

class TestDeleteBudget:
    """Test cases for deleting budgets"""
    
    def test_delete_budget_success(self, client, sample_user, sample_accounts):
        """Test successful budget deletion."""
        # Create budget first
        budget_data = {
            "user_id": sample_user.id,
            "name": "2024 Budget",
            "year": 2024,
            "lines": [
                {
                    "month": 1,
                    "account_id": sample_accounts["income"].id,
                    "amount_oc": 5000.00,
                    "currency": "USD",
                    "amount_hc": 5000.00
                }
            ]
        }
        response = client.post(f"/users/{sample_user.id}/budgets/", json=budget_data)
        budget = response.json()
        
        # Delete budget
        response = client.delete(f"/users/{sample_user.id}/budgets/{budget['id']}")
        assert response.status_code == 204
    
    def test_delete_budget_not_found(self, client, sample_user):
        """Test deleting a non-existent budget."""
        response = client.delete(f"/users/{sample_user.id}/budgets/99999")
        assert response.status_code == 404

class TestBudgetValidation:
    """Test cases for budget validation and business rules"""
    
    def test_budget_line_amount_validation(self, client, sample_user, sample_accounts):
        """Test budget line amount validation."""
        budget_data = {
            "user_id": sample_user.id,
            "name": "2024 Budget",
            "year": 2024,
            "lines": [
                {
                    "month": 1,
                    "account_id": sample_accounts["income"].id,
                    "amount_oc": -1000.00,  # Negative amount
                    "currency": "USD",
                    "amount_hc": -1000.00
                }
            ]
        }
        response = client.post(f"/users/{sample_user.id}/budgets/", json=budget_data)
        assert response.status_code == 409
    
    def test_budget_currency_validation(self, client, sample_user, sample_accounts):
        """Test budget currency validation."""
        budget_data = {
            "user_id": sample_user.id,
            "name": "2024 Budget",
            "year": 2024,
            "lines": [
                {
                    "month": 1,
                    "account_id": sample_accounts["income"].id,
                    "amount_oc": 1000.00,
                    "currency": "INVALID",  # Invalid currency
                    "amount_hc": 1000.00
                }
            ]
        }
        response = client.post(f"/users/{sample_user.id}/budgets/", json=budget_data)
        assert response.status_code == 422
    
    def test_budget_year_validation(self, client, sample_user, sample_accounts):
        """Test budget year validation."""
        budget_data = {
            "user_id": sample_user.id,
            "name": "2024 Budget",
            "year": 1900,  # Invalid year
            "lines": [
                {
                    "month": 1,
                    "account_id": sample_accounts["income"].id,
                    "amount_oc": 1000.00,
                    "currency": "USD",
                    "amount_hc": 1000.00
                }
            ]
        }
        response = client.post(f"/users/{sample_user.id}/budgets/", json=budget_data)
        # This might pass validation but could be tested for business logic
        assert response.status_code in [200, 422]

class TestBudgetEdgeCases:
    """Test cases for edge cases and boundary conditions"""
    
    def test_budget_maximum_amount(self, client, sample_user, sample_accounts):
        """Test budget with maximum amount."""
        max_amount = 999999999999999.99
        budget_data = {
            "user_id": sample_user.id,
            "name": "2024 Budget",
            "year": 2024,
            "lines": [
                {
                    "month": 1,
                    "account_id": sample_accounts["income"].id,
                    "amount_oc": max_amount,
                    "currency": "USD",
                    "amount_hc": max_amount
                }
            ]
        }
        response = client.post(f"/users/{sample_user.id}/budgets/", json=budget_data)
        assert response.status_code == 200
    
    def test_budget_minimum_amount(self, client, sample_user, sample_accounts):
        """Test budget with minimum amount."""
        min_amount = 0.01
        budget_data = {
            "user_id": sample_user.id,
            "name": "2024 Budget",
            "year": 2024,
            "lines": [
                {
                    "month": 1,
                    "account_id": sample_accounts["income"].id,
                    "amount_oc": min_amount,
                    "currency": "USD",
                    "amount_hc": min_amount
                }
            ]
        }
        response = client.post(f"/users/{sample_user.id}/budgets/", json=budget_data)
        assert response.status_code == 200
    
    def test_budget_multiple_months(self, client, sample_user, sample_accounts):
        """Test budget with multiple months."""
        budget_data = {
            "user_id": sample_user.id,
            "name": "2024 Budget",
            "year": 2024,
            "lines": [
                {
                    "month": 1,
                    "account_id": sample_accounts["income"].id,
                    "amount_oc": 5000.00,
                    "currency": "USD",
                    "amount_hc": 5000.00
                },
                {
                    "month": 2,
                    "account_id": sample_accounts["income"].id,
                    "amount_oc": 5500.00,
                    "currency": "USD",
                    "amount_hc": 5500.00
                },
                {
                    "month": 3,
                    "account_id": sample_accounts["income"].id,
                    "amount_oc": 6000.00,
                    "currency": "USD",
                    "amount_hc": 6000.00
                }
            ]
        }
        response = client.post(f"/users/{sample_user.id}/budgets/", json=budget_data)
        assert response.status_code == 200
        data = response.json()
        assert len(data["budget_lines"]) == 3

class TestBudgetIntegration:
    """Integration tests for budget functionality"""
    
    def test_budget_lifecycle(self, client, sample_user, sample_accounts):
        """Test complete budget lifecycle: create -> update -> delete."""
        # Create budget
        budget_data = {
            "user_id": sample_user.id,
            "name": "2024 Budget",
            "year": 2024,
            "lines": [
                {
                    "month": 1,
                    "account_id": sample_accounts["income"].id,
                    "amount_oc": 5000.00,
                    "currency": "USD",
                    "amount_hc": 5000.00
                }
            ]
        }
        response = client.post(f"/users/{sample_user.id}/budgets/", json=budget_data)
        assert response.status_code == 200
        budget = response.json()
        budget_id = budget["id"]
        
        # Update budget
        update_data = {
            "name": "Updated 2024 Budget",
            "lines": [
                {
                    "month": 1,
                    "account_id": sample_accounts["income"].id,
                    "amount_oc": 6000.00,
                    "currency": "USD",
                    "amount_hc": 6000.00
                }
            ]
        }
        response = client.patch(f"/users/{sample_user.id}/budgets/{budget_id}", json=update_data)
        assert response.status_code == 200
        assert response.json()["name"] == "Updated 2024 Budget"
        
        # Delete budget
        response = client.delete(f"/users/{sample_user.id}/budgets/{budget_id}")
        assert response.status_code == 204
    
    def test_multiple_budgets_same_user(self, client, sample_user, sample_accounts):
        """Test creating multiple budgets for the same user."""
        budgets_data = [
            {
                "user_id": sample_user.id,
                "name": "2024 Budget",
                "year": 2024,
                "lines": []
            },
            {
                "user_id": sample_user.id,
                "name": "2025 Budget",
                "year": 2025,
                "lines": []
            }
        ]
        
        for budget_data in budgets_data:
            response = client.post(f"/users/{sample_user.id}/budgets/", json=budget_data)
            assert response.status_code == 200
        
        # Verify both budgets exist
        response1 = client.get(f"/users/{sample_user.id}/budgets/1")
        response2 = client.get(f"/users/{sample_user.id}/budgets/2")
        assert response1.status_code == 200
        assert response2.status_code == 200
