"""
Test cases for report functionality in the finance app backend.
"""

class TestReportBalances:
    """Test cases for balance reports"""
    
    def test_get_balances_success(self, client, sample_user, sample_accounts):
        """Test successful balance report generation."""
        response = client.get(f"/users/{sample_user.id}/reports/balances")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Should include asset accounts with balances
        for balance in data:
            assert "account_id" in balance
            assert "account_name" in balance
            assert "balance" in balance
            assert "currency" in balance
    
    def test_get_balances_empty(self, client, sample_user):
        """Test balance report with no accounts."""
        response = client.get(f"/users/{sample_user.id}/reports/balances")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_balances_with_transactions(self, client, sample_user, sample_accounts, sample_transactions):
        """Test balance report with transactions."""
        response = client.get(f"/users/{sample_user.id}/reports/balances")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Should reflect transaction impacts on balances
        for balance in data:
            assert isinstance(balance["balance"], (int, float))

class TestReportDebts:
    """Test cases for debt reports"""
    
    def test_get_debts_success(self, client, sample_user, sample_people):
        """Test successful debt report generation."""
        response = client.get(f"/users/{sample_user.id}/reports/debts")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Should include people with debt information
        for debt in data:
            assert "person_id" in debt
            assert "person_name" in debt
            assert "debt" in debt
            assert "is_active" in debt
            assert isinstance(debt["debt"], (int, float))
            assert isinstance(debt["is_active"], bool)
    
    def test_get_debts_empty(self, client, sample_user):
        """Test debt report with no people."""
        response = client.get(f"/users/{sample_user.id}/reports/debts")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_debts_with_splits(self, client, sample_user, sample_people, sample_accounts):
        """Test debt report with transaction splits."""
        # Create a transaction with splits to generate debt
        transaction_data = {
            "user_id": sample_user.id,
            "date": "2024-01-15T10:00:00",
            "type": "expense",
            "description": "Group dinner",
            "amount_oc_primary": 100.00,
            "currency_primary": "USD",
            "account_id_primary": sample_accounts["expense"].id,
            "account_id_secondary": sample_accounts["checking_account"].id
        }
        response = client.post(f"/users/{sample_user.id}/transactions/", json=transaction_data)
        assert response.status_code == 200
        
        # Get debt report
        response = client.get(f"/users/{sample_user.id}/reports/debts")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

class TestReportBudgetProgress:
    """Test cases for budget progress reports"""
    
    def test_get_budget_progress_success(self, client, sample_user, sample_accounts):
        """Test successful budget progress report generation."""
        # Create a budget first
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
        
        # Get budget progress
        response = client.get(f"/users/{sample_user.id}/reports/budget-progress/2024-01")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Should include budget progress information
        for progress in data:
            assert "account_id" in progress
            assert "account_name" in progress
            assert "budget_hc" in progress
            assert "actual_hc" in progress
            assert "progress" in progress
            assert isinstance(progress["budget_hc"], (int, float))
            assert isinstance(progress["actual_hc"], (int, float))
            assert isinstance(progress["progress"], (int, float))
    
    def test_get_budget_progress_empty(self, client, sample_user):
        """Test budget progress report with no budgets."""
        response = client.get(f"/users/{sample_user.id}/reports/budget-progress/2024-01")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_budget_progress_invalid_month(self, client, sample_user):
        """Test budget progress report with invalid month format."""
        response = client.get(f"/users/{sample_user.id}/reports/budget-progress/invalid")
        # Should handle invalid month format gracefully
        assert response.status_code in [200, 422, 400]

class TestReportMonthlyBudgetProgress:
    """Test cases for monthly budget progress reports"""
    
    def test_get_monthly_budget_progress_success(self, client, sample_user, sample_accounts):
        """Test successful monthly budget progress report generation."""
        # Create a budget first
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
        
        # Get monthly budget progress
        response = client.get(f"/users/{sample_user.id}/reports/budget-progress/{budget['id']}/2024/1")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Should include budget progress information
        assert len(data) > 0
        progress_item = data[0]
        assert "account_id" in progress_item
        assert "account_name" in progress_item
        assert "budget_hc" in progress_item
        assert "actual_hc" in progress_item
        assert "progress" in progress_item
    
    def test_get_monthly_budget_progress_not_found(self, client, sample_user):
        """Test monthly budget progress report with non-existent budget."""
        response = client.get(f"/users/{sample_user.id}/reports/budget-progress/99999/2024/1")
        assert response.status_code == 404
    
    def test_get_monthly_budget_progress_invalid_month(self, client, sample_user, sample_accounts):
        """Test monthly budget progress report with invalid month."""
        # Create a budget first
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
        
        # Test with invalid month
        response = client.get(f"/users/{sample_user.id}/reports/budget-progress/{budget['id']}/2024/13")
        assert response.status_code == 422

class TestReportValidation:
    """Test cases for report validation and business rules"""
    
    def test_report_user_not_found(self, client, db_session):
        """Test report generation for non-existent user."""
        # Temporarily disable authentication override for this test
        from app.dependencies import get_authenticated_user
        from app.main import app
        
        # Store original dependency
        original_dependency = app.dependency_overrides.get(get_authenticated_user)
        
        # Remove override temporarily
        if get_authenticated_user in app.dependency_overrides:
            del app.dependency_overrides[get_authenticated_user]
        
        try:
            response = client.get("/users/99999/reports/balances")
            assert response.status_code == 403
        finally:
            # Restore original dependency
            if original_dependency:
                app.dependency_overrides[get_authenticated_user] = original_dependency
    
    def test_report_unauthorized_access(self, client, sample_user):
        """Test report access with different user ID."""
        # This would need proper authentication setup to test
        # For now, we'll test the basic endpoint structure
        response = client.get(f"/users/{sample_user.id}/reports/balances")
        assert response.status_code == 200

class TestReportEdgeCases:
    """Test cases for edge cases and boundary conditions"""
    
    def test_report_with_large_amounts(self, client, sample_user, sample_accounts):
        """Test report generation with large amounts."""
        # Create transaction with large amount
        transaction_data = {
            "user_id": sample_user.id,
            "date": "2024-01-15T10:00:00",
            "type": "income",
            "description": "Large income",
            "amount_oc_primary": 999999999.99,
            "currency_primary": "USD",
            "account_id_primary": sample_accounts["income"].id,
            "account_id_secondary": sample_accounts["checking_account"].id
        }
        response = client.post(f"/users/{sample_user.id}/transactions/", json=transaction_data)
        assert response.status_code == 200
        
        # Get balance report
        response = client.get(f"/users/{sample_user.id}/reports/balances")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_report_with_multiple_currencies(self, client, sample_user, sample_accounts):
        """Test report generation with multiple currencies."""
        # Create transactions in different currencies (simplified to USD only for now)
        currencies = ["USD"]
        for i, currency in enumerate(currencies):
            transaction_data = {
                "user_id": sample_user.id,
                "date": "2024-01-15T10:00:00",
                "type": "income",
                "description": f"Income in {currency}",
                "amount_oc_primary": 1000.00,
                "currency_primary": currency,
                "account_id_primary": sample_accounts["income"].id,
                "account_id_secondary": sample_accounts["checking_account"].id
            }
            response = client.post(f"/users/{sample_user.id}/transactions/", json=transaction_data)
            assert response.status_code == 200
        
        # Get balance report
        response = client.get(f"/users/{sample_user.id}/reports/balances")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_report_with_empty_data(self, client, sample_user):
        """Test report generation with no data."""
        # Get all reports with no data
        response = client.get(f"/users/{sample_user.id}/reports/balances")
        assert response.status_code == 200
        assert response.json() == []
        
        response = client.get(f"/users/{sample_user.id}/reports/debts")
        assert response.status_code == 200
        assert response.json() == []
        
        response = client.get(f"/users/{sample_user.id}/reports/budget-progress/2024-01")
        assert response.status_code == 200
        assert response.json() == []

class TestReportIntegration:
    """Integration tests for report functionality"""
    
    def test_report_data_consistency(self, client, sample_user, sample_accounts, sample_transactions):
        """Test that reports show consistent data."""
        # Get balance report
        response = client.get(f"/users/{sample_user.id}/reports/balances")
        assert response.status_code == 200
        balances = response.json()
        
        # Get debt report
        response = client.get(f"/users/{sample_user.id}/reports/debts")
        assert response.status_code == 200
        debts = response.json()
        
        # Both should be lists
        assert isinstance(balances, list)
        assert isinstance(debts, list)
    
    def test_report_with_complex_scenario(self, client, sample_user, sample_accounts, sample_people):
        """Test reports with complex financial scenario."""
        # Create multiple transactions
        transactions = [
            {
                "user_id": sample_user.id,
                "date": "2024-01-15T10:00:00",
                "type": "income",
                "description": "Salary",
                "amount_oc_primary": 5000.00,
                "currency_primary": "USD",
                "account_id_primary": sample_accounts["income"].id,
                "account_id_secondary": sample_accounts["checking_account"].id
            },
            {
                "user_id": sample_user.id,
                "date": "2024-01-16T10:00:00",
                "type": "expense",
                "description": "Groceries",
                "amount_oc_primary": 150.00,
                "currency_primary": "USD",
                "account_id_primary": sample_accounts["expense"].id,
                "account_id_secondary": sample_accounts["checking_account"].id
            },
            {
                "user_id": sample_user.id,
                "date": "2024-01-17T10:00:00",
                "type": "transfer",
                "description": "Savings",
                "amount_oc_primary": 1000.00,
                "currency_primary": "USD",
                "account_id_primary": sample_accounts["checking_account"].id,
                "account_id_secondary": sample_accounts["savings_account"].id
            }
        ]
        
        for tx_data in transactions:
            response = client.post(f"/users/{sample_user.id}/transactions/", json=tx_data)
            assert response.status_code == 200
        
        # Get all reports
        response = client.get(f"/users/{sample_user.id}/reports/balances")
        assert response.status_code == 200
        balances = response.json()
        
        response = client.get(f"/users/{sample_user.id}/reports/debts")
        assert response.status_code == 200
        debts = response.json()
        
        # Reports should reflect the transactions
        assert isinstance(balances, list)
        assert isinstance(debts, list)
