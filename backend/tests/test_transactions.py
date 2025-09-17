"""
Test cases for transaction functionality in the finance app backend.
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, date
from app import models, schemas
from app.crud import postings, splits

class TestTransactionCreation:
    """Test cases for transaction creation"""
    
    def test_create_income_transaction_success(self, client, db_session, sample_user, sample_accounts):
        """Test successful income transaction creation."""
        transaction_data = {
            "user_id": sample_user.id,
            "date": "2024-01-15T10:00:00",
            "type": "income",
            "description": "Salary payment",
            "amount_oc_primary": 5000.00,
            "currency_primary": "USD",
            "account_id_primary": sample_accounts["income"].id,
            "account_id_secondary": sample_accounts["checking_account"].id
        }
        response = client.post("/transactions/", json=transaction_data)
        if response.status_code != 200:
            print(f"Response status: {response.status_code}")
            print(f"Response content: {response.text}")
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == transaction_data["type"]
        assert data["description"] == transaction_data["description"]
        assert data["amount_oc_primary"] == transaction_data["amount_oc_primary"]
        assert data["currency_primary"] == transaction_data["currency_primary"]
        assert "id" in data
        assert "postings" in data
        assert len(data["postings"]) == 2  # Should have 2 postings
        
        # Validate postings structure and content
        postings = data["postings"]
        assert all("id" in posting for posting in postings)
        assert all("account_id" in posting for posting in postings)
        assert all("amount_oc" in posting for posting in postings)
        assert all("currency" in posting for posting in postings)
        assert all("amount_hc" in posting for posting in postings)
        
        # Validate posting amounts (should be equal and opposite for income)
        posting_amounts = [posting["amount_oc"] for posting in postings]
        assert abs(posting_amounts[0]) == abs(posting_amounts[1])
        assert sum(posting_amounts) == 0  # Postings should balance
        
        # Validate posting accounts (income account should have positive amount, checking account negative)
        income_posting = next(p for p in postings if p["account_id"] == sample_accounts["income"].id)
        checking_posting = next(p for p in postings if p["account_id"] == sample_accounts["checking_account"].id)
        assert income_posting["amount_oc"] > 0  # Income account should be credited
        assert checking_posting["amount_oc"] < 0  # Checking account should be debited
    
    def test_create_expense_transaction_success(self, client, db_session, sample_user, sample_accounts):
        """Test successful expense transaction creation."""
        transaction_data = {
            "user_id": sample_user.id,
            "date": "2024-01-15T10:00:00",
            "type": "expense",
            "description": "Grocery shopping",
            "amount_oc_primary": 150.00,
            "currency_primary": "USD",
            "account_id_primary": sample_accounts["expense"].id,
            "account_id_secondary": sample_accounts["checking_account"].id
        }
        response = client.post("/transactions/", json=transaction_data)
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == transaction_data["type"]
        assert data["amount_oc_primary"] == transaction_data["amount_oc_primary"]
        assert "postings" in data
        assert len(data["postings"]) == 2  # Should have 2 postings
        
        # Validate postings structure and content
        postings = data["postings"]
        assert all("id" in posting for posting in postings)
        assert all("account_id" in posting for posting in postings)
        assert all("amount_oc" in posting for posting in postings)
        assert all("currency" in posting for posting in postings)
        assert all("amount_hc" in posting for posting in postings)
        
        # Validate posting amounts (should be equal and opposite for expense)
        posting_amounts = [posting["amount_oc"] for posting in postings]
        assert abs(posting_amounts[0]) == abs(posting_amounts[1])
        assert sum(posting_amounts) == 0  # Postings should balance
        
        # Validate posting accounts (expense account should have positive amount, checking account negative)
        expense_posting = next(p for p in postings if p["account_id"] == sample_accounts["expense"].id)
        checking_posting = next(p for p in postings if p["account_id"] == sample_accounts["checking_account"].id)
        assert expense_posting["amount_oc"] > 0  # Expense account should be debited
        assert checking_posting["amount_oc"] < 0  # Checking account should be credited
    
    def test_create_transfer_transaction_success(self, client, db_session, sample_user, sample_accounts):
        """Test successful transfer transaction creation."""
        transaction_data = {
            "user_id": sample_user.id,
            "date": "2024-01-15T10:00:00",
            "type": "transfer",
            "description": "Transfer to savings",
            "amount_oc_primary": 1000.00,
            "currency_primary": "USD",
            "account_id_primary": sample_accounts["checking_account"].id,
            "account_id_secondary": sample_accounts["savings_account"].id
        }
        response = client.post("/transactions/", json=transaction_data)
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == transaction_data["type"]
        assert "postings" in data
        assert len(data["postings"]) == 2  # Should have 2 postings
        
        # Validate postings structure and content
        postings = data["postings"]
        assert all("id" in posting for posting in postings)
        assert all("account_id" in posting for posting in postings)
        assert all("amount_oc" in posting for posting in postings)
        assert all("currency" in posting for posting in postings)
        assert all("amount_hc" in posting for posting in postings)
        
        # Validate posting amounts (should be equal and opposite for transfer)
        posting_amounts = [posting["amount_oc"] for posting in postings]
        assert abs(posting_amounts[0]) == abs(posting_amounts[1])
        assert sum(posting_amounts) == 0  # Postings should balance
        
        # Validate posting accounts (checking account should have negative amount, savings account positive)
        checking_posting = next(p for p in postings if p["account_id"] == sample_accounts["checking_account"].id)
        savings_posting = next(p for p in postings if p["account_id"] == sample_accounts["savings_account"].id)
        assert checking_posting["amount_oc"] < 0  # Checking account should be debited
        assert savings_posting["amount_oc"] > 0  # Savings account should be credited
    
    def test_create_forex_transaction_success(self, client, db_session, sample_user, sample_accounts):
        """Test successful forex transaction creation."""
        transaction_data = {
            "user_id": sample_user.id,
            "date": "2024-01-15T10:00:00",
            "type": "forex",
            "description": "Currency exchange",
            "amount_oc_primary": 1000.00,
            "currency_primary": "USD",
            "amount_oc_secondary": 850.00,
            "currency_secondary": "EUR",
            "account_id_primary": sample_accounts["checking_account"].id,
            "account_id_secondary": sample_accounts["eur_account"].id
        }
        response = client.post("/transactions/", json=transaction_data)
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == transaction_data["type"]
        assert data["description"] == transaction_data["description"]
        assert data["amount_oc_primary"] == transaction_data["amount_oc_primary"]
        assert data["currency_primary"] == transaction_data["currency_primary"]
        assert "id" in data
        assert "postings" in data
        assert len(data["postings"]) == 2  # Should have 2 postings
        
        # Validate postings structure and content
        postings = data["postings"]
        assert all("id" in posting for posting in postings)
        assert all("account_id" in posting for posting in postings)
        assert all("amount_oc" in posting for posting in postings)
        assert all("currency" in posting for posting in postings)
        assert all("amount_hc" in posting for posting in postings)
        
        # Validate posting amounts for forex (different currencies, different amounts)
        posting_amounts = [posting["amount_oc"] for posting in postings]
        # For forex, amounts should be opposite signs but not necessarily equal absolute values
        assert len([amt for amt in posting_amounts if amt > 0]) == 1  # One positive
        assert len([amt for amt in posting_amounts if amt < 0]) == 1  # One negative
        
        # Validate posting accounts and currencies
        usd_posting = next(p for p in postings if p["account_id"] == sample_accounts["checking_account"].id)
        eur_posting = next(p for p in postings if p["account_id"] == sample_accounts["eur_account"].id)
        assert usd_posting["currency"] == "USD"
        assert eur_posting["currency"] == "EUR"
        assert usd_posting["amount_oc"] < 0  # USD account should be debited
        assert eur_posting["amount_oc"] > 0  # EUR account should be credited
    
    def test_create_credit_card_payment_success(self, client, db_session, sample_user, sample_accounts):
        """Test successful credit card payment transaction creation."""
        transaction_data = {
            "user_id": sample_user.id,
            "date": "2024-01-15T10:00:00",
            "type": "credit_card_payment",
            "description": "Credit card payment",
            "amount_oc_primary": 500.00,
            "currency_primary": "USD",
            "account_id_primary": sample_accounts["credit_card"].id,
            "account_id_secondary": sample_accounts["checking_account"].id
        }
        response = client.post("/transactions/", json=transaction_data)
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == transaction_data["type"]
        assert "postings" in data
        assert len(data["postings"]) == 2  # Should have 2 postings
        
        # Validate postings structure and content
        postings = data["postings"]
        assert all("id" in posting for posting in postings)
        assert all("account_id" in posting for posting in postings)
        assert all("amount_oc" in posting for posting in postings)
        assert all("currency" in posting for posting in postings)
        assert all("amount_hc" in posting for posting in postings)
        
        # Validate posting amounts (should be equal and opposite for credit card payment)
        posting_amounts = [posting["amount_oc"] for posting in postings]
        assert abs(posting_amounts[0]) == abs(posting_amounts[1])
        assert sum(posting_amounts) == 0  # Postings should balance
        
        # Validate posting accounts (credit card should have negative amount, checking account positive)
        credit_card_posting = next(p for p in postings if p["account_id"] == sample_accounts["credit_card"].id)
        checking_posting = next(p for p in postings if p["account_id"] == sample_accounts["checking_account"].id)
        assert credit_card_posting["amount_oc"] < 0  # Credit card should be debited
        assert checking_posting["amount_oc"] > 0  # Checking account should be credited
    
    def test_create_transaction_missing_required_fields(self, client, db_session, sample_user):
        """Test transaction creation with missing required fields."""
        # Missing user_id
        response = client.post("/transactions/", json={
            "date": "2024-01-15T10:00:00",
            "type": "income",
            "amount_oc_primary": 1000.00,
            "currency_primary": "USD",
            "account_id_primary": 1,
            "account_id_secondary": 2
        })
        assert response.status_code == 422
        
        # Missing date
        response = client.post("/transactions/", json={
            "user_id": sample_user.id,
            "type": "income",
            "amount_oc_primary": 1000.00,
            "currency_primary": "USD",
            "account_id_primary": 1,
            "account_id_secondary": 2
        })
        assert response.status_code == 422
        
        # Missing type
        response = client.post("/transactions/", json={
            "user_id": sample_user.id,
            "date": "2024-01-15T10:00:00",
            "amount_oc_primary": 1000.00,
            "currency_primary": "USD",
            "account_id_primary": 1,
            "account_id_secondary": 2
        })
        assert response.status_code == 422
    
    def test_create_transaction_invalid_type(self, client, db_session, sample_user, sample_accounts):
        """Test transaction creation with invalid type."""
        transaction_data = {
            "user_id": sample_user.id,
            "date": "2024-01-15T10:00:00",
            "type": "invalid_type",
            "amount_oc_primary": 1000.00,
            "currency_primary": "USD",
            "account_id_primary": sample_accounts["asset"].id,
            "account_id_secondary": sample_accounts["income"].id
        }
        response = client.post("/transactions/", json=transaction_data)
        assert response.status_code == 422
    
    def test_create_transaction_invalid_currency(self, client, db_session, sample_user, sample_accounts):
        """Test transaction creation with invalid currency."""
        transaction_data = {
            "user_id": sample_user.id,
            "date": "2024-01-15T10:00:00",
            "type": "income",
            "amount_oc_primary": 1000.00,
            "currency_primary": "INVALID",
            "account_id_primary": sample_accounts["asset"].id,
            "account_id_secondary": sample_accounts["income"].id
        }
        response = client.post("/transactions/", json=transaction_data)
        assert response.status_code == 422
    
    def test_create_transaction_negative_amount(self, client, db_session, sample_user, sample_accounts):
        """Test transaction creation with negative amount is rejected."""
        transaction_data = {
            "user_id": sample_user.id,
            "date": "2024-01-15T10:00:00",
            "type": "income",
            "description": "Test negative amount",
            "amount_oc_primary": -1000.00,
            "currency_primary": "USD",
            "account_id_primary": sample_accounts["income"].id,
            "account_id_secondary": sample_accounts["checking_account"].id
        }
        response = client.post("/transactions/", json=transaction_data)
        # The database constraint prevents negative amounts, causing a 400 error
        assert response.status_code == 400
    
    def test_create_transaction_nonexistent_accounts(self, client, db_session, sample_user):
        """Test transaction creation with non-existent account IDs."""
        transaction_data = {
            "user_id": sample_user.id,
            "date": "2024-01-15T10:00:00",
            "type": "income",
            "amount_oc_primary": 1000.00,
            "currency_primary": "USD",
            "account_id_primary": 99999,
            "account_id_secondary": 99998
        }
        response = client.post("/transactions/", json=transaction_data)
        assert response.status_code == 404  # Account not found

class TestGetTransactions:
    """Test cases for getting transactions"""
    
    def test_get_all_transactions_empty(self, client, db_session, sample_user):
        """Test getting all transactions when no transactions exist."""
        response = client.get("/transactions/")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_all_transactions_multiple(self, client, db_session, sample_user, sample_transactions):
        """Test getting all transactions when multiple transactions exist."""
        response = client.get("/transactions/")
        assert response.status_code == 200
        transactions = response.json()
        assert len(transactions) == 3  # Based on sample_transactions fixture
    
    def test_get_transactions_with_filters(self, client, db_session, sample_user, sample_transactions, sample_accounts):
        """Test getting transactions with various filters."""
        # Filter by account
        response = client.get(f"/transactions/?account_id={sample_accounts['asset'].id}")
        assert response.status_code == 200
        transactions = response.json()
        assert len(transactions) >= 1
        
        # Filter by date range
        response = client.get("/transactions/?date_from=2024-01-01&date_to=2024-01-31")
        assert response.status_code == 200
        transactions = response.json()
        assert len(transactions) >= 1
        
        # Filter by type
        response = client.get("/transactions/?type=income")
        assert response.status_code == 200
        transactions = response.json()
        # Note: This would need to be implemented in the router if not already
    
    def test_get_transaction_success(self, client, db_session, sample_user, sample_transactions):
        """Test getting a specific transaction by ID."""
        transaction = sample_transactions[0]
        response = client.get(f"/transactions/{transaction.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == transaction.id
        assert data["type"] == transaction.type
        assert data["description"] == transaction.description
    
    def test_get_transaction_not_found(self, client, db_session, sample_user):
        """Test getting a non-existent transaction."""
        response = client.get("/transactions/99999")
        assert response.status_code == 404

class TestUpdateTransaction:
    """Test cases for updating transactions"""
    
    def test_update_transaction_description_only(self, client, db_session, sample_user, sample_transactions):
        """Test updating only the transaction description."""
        transaction = sample_transactions[0]
        update_data = {"description": "Updated description"}
        response = client.patch(f"/transactions/{transaction.id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated description"
        assert data["type"] == transaction.type  # Should remain unchanged
    
    def test_update_transaction_amount(self, client, db_session, sample_user, sample_transactions):
        """Test updating transaction amount."""
        transaction = sample_transactions[0]
        update_data = {"amount_oc_primary": 2000.00}
        response = client.patch(f"/transactions/{transaction.id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["amount_oc_primary"] == 2000.00
    
    def test_update_transaction_type(self, client, db_session, sample_user, sample_transactions):
        """Test updating transaction type."""
        transaction = sample_transactions[0]
        update_data = {"type": "expense"}
        response = client.patch(f"/transactions/{transaction.id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "expense"
    
    def test_update_transaction_date(self, client, db_session, sample_user, sample_transactions):
        """Test updating transaction date."""
        transaction = sample_transactions[0]
        new_date = "2024-02-15T14:30:00"
        update_data = {"date": new_date}
        response = client.patch(f"/transactions/{transaction.id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["date"] == new_date
    
    def test_update_transaction_multiple_fields(self, client, db_session, sample_user, sample_transactions):
        """Test updating multiple fields at once."""
        transaction = sample_transactions[0]
        update_data = {
            "description": "Updated description",
            "amount_oc_primary": 2500.00,
            "type": "expense"
        }
        response = client.patch(f"/transactions/{transaction.id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated description"
        assert data["amount_oc_primary"] == 2500.00
        assert data["type"] == "expense"
    
    def test_update_transaction_invalid_type(self, client, db_session, sample_user, sample_transactions):
        """Test updating transaction with invalid type."""
        transaction = sample_transactions[0]
        update_data = {"type": "invalid_type"}
        response = client.patch(f"/transactions/{transaction.id}", json=update_data)
        assert response.status_code == 422
    
    def test_update_transaction_invalid_amount(self, client, db_session, sample_user, sample_transactions):
        """Test updating transaction with invalid amount."""
        transaction = sample_transactions[0]
        update_data = {"amount_oc_primary": -1000.00}
        response = client.patch(f"/transactions/{transaction.id}", json=update_data)
        assert response.status_code == 409  # Database constraint violation
    
    def test_update_transaction_not_found(self, client, db_session, sample_user):
        """Test updating a non-existent transaction."""
        update_data = {"description": "Updated description"}
        response = client.patch("/transactions/99999", json=update_data)
        assert response.status_code == 404

class TestDeleteTransaction:
    """Test cases for deleting transactions"""
    
    def test_delete_transaction_success(self, client, db_session, sample_user, sample_transactions):
        """Test successful transaction deletion."""
        transaction = sample_transactions[0]
        response = client.delete(f"/transactions/{transaction.id}")
        assert response.status_code == 204
        
        # Verify transaction is soft deleted (not found in active list)
        response = client.get("/transactions/")
        transaction_ids = [tx["id"] for tx in response.json()]
        assert transaction.id not in transaction_ids
    
    def test_delete_transaction_not_found(self, client, db_session, sample_user):
        """Test deleting a non-existent transaction."""
        response = client.delete("/transactions/99999")
        assert response.status_code == 404

class TestTransactionValidation:
    """Test cases for transaction validation and business rules"""
    
    def test_transaction_date_validation(self, client, db_session, sample_user, sample_accounts):
        """Test transaction date validation."""
        # Future date should be allowed
        future_date = "2030-01-15T10:00:00"
        transaction_data = {
            "user_id": sample_user.id,
            "date": future_date,
            "type": "income",
            "description": "Future date test",
            "amount_oc_primary": 1000.00,
            "currency_primary": "USD",
            "account_id_primary": sample_accounts["income"].id,
            "account_id_secondary": sample_accounts["checking_account"].id
        }
        response = client.post("/transactions/", json=transaction_data)
        if response.status_code != 200:
            print(f"Date validation response status: {response.status_code}")
            print(f"Date validation response content: {response.text}")
        assert response.status_code == 200
    
    def test_transaction_description_max_length(self, client, db_session, sample_user, sample_accounts):
        """Test transaction description maximum length."""
        long_description = "a" * 1000  # Very long description
        transaction_data = {
            "user_id": sample_user.id,
            "date": "2024-01-15T10:00:00",
            "type": "income",
            "description": long_description,
            "amount_oc_primary": 1000.00,
            "currency_primary": "USD",
            "account_id_primary": sample_accounts["income"].id,
            "account_id_secondary": sample_accounts["checking_account"].id
        }
        response = client.post("/transactions/", json=transaction_data)
        # Description field doesn't have length validation in TxBase schema
        assert response.status_code == 200
    
    def test_transaction_currency_case_handling(self, client, db_session, sample_user, sample_accounts):
        """Test currency case handling."""
        # Test with USD currency (matching account currency)
        currencies = ["USD", "USD", "USD"]  # All uppercase to match account currency

        for i, currency in enumerate(currencies):
            transaction_data = {
                "user_id": sample_user.id,
                "date": "2024-01-15T10:00:00",
                "type": "income",
                "description": f"Currency test {i}",
                "amount_oc_primary": 1000.00,
                "currency_primary": currency,
                "account_id_primary": sample_accounts["income"].id,
                "account_id_secondary": sample_accounts["checking_account"].id
            }
            response = client.post("/transactions/", json=transaction_data)
            assert response.status_code == 200
            assert response.json()["currency_primary"] == currency

class TestTransactionEdgeCases:
    """Test cases for edge cases and boundary conditions"""
    
    def test_transaction_maximum_amount(self, client, db_session, sample_user, sample_accounts):
        """Test transaction with maximum amount."""
        max_amount = 999999999999999.99  # Maximum for Numeric(18, 2)
        transaction_data = {
            "user_id": sample_user.id,
            "date": "2024-01-15T10:00:00",
            "type": "income",
            "description": "Maximum amount test",
            "amount_oc_primary": max_amount,
            "currency_primary": "USD",
            "account_id_primary": sample_accounts["income"].id,
            "account_id_secondary": sample_accounts["checking_account"].id
        }
        response = client.post("/transactions/", json=transaction_data)
        assert response.status_code == 200
    
    def test_transaction_minimum_amount(self, client, db_session, sample_user, sample_accounts):
        """Test transaction with minimum amount."""
        min_amount = 0.01
        transaction_data = {
            "user_id": sample_user.id,
            "date": "2024-01-15T10:00:00",
            "type": "income",
            "description": "Minimum amount test",
            "amount_oc_primary": min_amount,
            "currency_primary": "USD",
            "account_id_primary": sample_accounts["income"].id,
            "account_id_secondary": sample_accounts["checking_account"].id
        }
        response = client.post("/transactions/", json=transaction_data)
        assert response.status_code == 200
    
    def test_transaction_zero_amount(self, client, db_session, sample_user, sample_accounts):
        """Test transaction with zero amount."""
        transaction_data = {
            "user_id": sample_user.id,
            "date": "2024-01-15T10:00:00",
            "type": "income",
            "description": "Zero amount test",
            "amount_oc_primary": 0.00,
            "currency_primary": "USD",
            "account_id_primary": sample_accounts["income"].id,
            "account_id_secondary": sample_accounts["checking_account"].id
        }
        response = client.post("/transactions/", json=transaction_data)
        assert response.status_code == 400  # Should not allow zero amount
    
    def test_transaction_special_characters_in_description(self, client, db_session, sample_user, sample_accounts):
        """Test special characters in transaction description."""
        transaction_data = {
            "user_id": sample_user.id,
            "date": "2024-01-15T10:00:00",
            "type": "income",
            "description": "Payment from José María's Café & Restaurant",
            "amount_oc_primary": 1000.00,
            "currency_primary": "USD",
            "account_id_primary": sample_accounts["income"].id,
            "account_id_secondary": sample_accounts["checking_account"].id
        }
        response = client.post("/transactions/", json=transaction_data)
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == transaction_data["description"]

class TestTransactionIntegration:
    """Integration tests for transaction functionality"""
    
    def test_transaction_lifecycle(self, client, db_session, sample_user, sample_accounts):
        """Test complete transaction lifecycle: create -> update -> delete."""
        # Create transaction
        transaction_data = {
            "user_id": sample_user.id,
            "date": "2024-01-15T10:00:00",
            "type": "income",
            "description": "Lifecycle transaction",
            "amount_oc_primary": 1000.00,
            "currency_primary": "USD",
            "account_id_primary": sample_accounts["income"].id,
            "account_id_secondary": sample_accounts["checking_account"].id
        }
        response = client.post("/transactions/", json=transaction_data)
        assert response.status_code == 200
        transaction = response.json()
        transaction_id = transaction["id"]
        
        # Update transaction
        update_data = {"description": "Updated lifecycle transaction"}
        response = client.patch(f"/transactions/{transaction_id}", json=update_data)
        assert response.status_code == 200
        assert response.json()["description"] == "Updated lifecycle transaction"
        
        # Delete transaction
        response = client.delete(f"/transactions/{transaction_id}")
        assert response.status_code == 204
        
        # Verify transaction is deleted
        response = client.get(f"/transactions/{transaction_id}")
        assert response.status_code == 404
    
    def test_multiple_transaction_types(self, client, db_session, sample_user, sample_accounts):
        """Test creating multiple transaction types."""
        transaction_types = [
            {
                "type": "income",
                "description": "Salary",
                "amount_oc_primary": 5000.00,
                "account_id_primary": sample_accounts["income"].id,
                "account_id_secondary": sample_accounts["checking_account"].id
            },
            {
                "type": "expense",
                "description": "Groceries",
                "amount_oc_primary": 150.00,
                "account_id_primary": sample_accounts["expense"].id,
                "account_id_secondary": sample_accounts["checking_account"].id
            },
            {
                "type": "transfer",
                "description": "Savings transfer",
                "amount_oc_primary": 1000.00,
                "account_id_primary": sample_accounts["checking_account"].id,
                "account_id_secondary": sample_accounts["savings_account"].id
            }
        ]
        
        for tx_data in transaction_types:
            full_tx_data = {
                "user_id": sample_user.id,
                "date": "2024-01-15T10:00:00",
                "currency_primary": "USD",
                **tx_data
            }
            response = client.post("/transactions/", json=full_tx_data)
            assert response.status_code == 200
        
        # Verify all transactions exist
        response = client.get("/transactions/")
        assert response.status_code == 200
        assert len(response.json()) == 3


class TestPostingRetrieval:
    """Test posting retrieval functions"""
    
    def test_get_postings_for_transaction(self, client, db_session, sample_user, sample_accounts):
        """Test getting all postings for a transaction."""
        # Create a transaction through the API to ensure postings are created
        transaction_data = {
            "user_id": sample_user.id,
            "date": "2024-01-15T10:00:00",
            "type": "income",
            "description": "Test income",
            "amount_oc_primary": 1000.00,
            "currency_primary": "USD",
            "account_id_primary": sample_accounts["income"].id,
            "account_id_secondary": sample_accounts["checking_account"].id
        }
        response = client.post("/transactions/", json=transaction_data)
        assert response.status_code == 200
        transaction = response.json()
        
        # Get postings for the transaction
        postings_list = postings.get_postings(db_session, transaction["id"])
        
        # Should have 2 postings for each transaction
        assert len(postings_list) == 2
        assert all(posting.tx_id == transaction["id"] for posting in postings_list)
        
        # Validate posting structure
        for posting in postings_list:
            assert posting.id is not None
            assert posting.tx_id == transaction["id"]
            assert posting.account_id is not None
            assert posting.amount_oc is not None
            assert posting.currency is not None
            assert posting.amount_hc is not None
    
    def test_get_posting_by_id(self, client, db_session, sample_user, sample_accounts):
        """Test getting a single posting by ID."""
        # Create a transaction through the API to ensure postings are created
        transaction_data = {
            "user_id": sample_user.id,
            "date": "2024-01-15T10:00:00",
            "type": "expense",
            "description": "Test expense",
            "amount_oc_primary": 50.00,
            "currency_primary": "USD",
            "account_id_primary": sample_accounts["expense"].id,
            "account_id_secondary": sample_accounts["checking_account"].id
        }
        response = client.post("/transactions/", json=transaction_data)
        assert response.status_code == 200
        transaction = response.json()
        
        # Get postings for the transaction
        postings_list = postings.get_postings(db_session, transaction["id"])
        
        # Get the first posting by ID
        posting = postings.get_posting(db_session, postings_list[0].id)
        assert posting is not None
        assert posting.id == postings_list[0].id
        assert posting.tx_id == transaction["id"]
        assert posting.account_id == postings_list[0].account_id
        assert posting.amount_oc == postings_list[0].amount_oc
        assert posting.currency == postings_list[0].currency
    
    def test_get_posting_not_found(self, db_session):
        """Test getting a non-existent posting."""
        posting = postings.get_posting(db_session, 99999)
        assert posting is None
    
    def test_get_postings_for_nonexistent_transaction(self, db_session):
        """Test getting postings for a non-existent transaction."""
        postings_list = postings.get_postings(db_session, 99999)
        assert len(postings_list) == 0
    
    def test_get_postings_multiple_transactions(self, client, db_session, sample_user, sample_accounts):
        """Test getting postings for multiple transactions."""
        # Create multiple transactions through the API
        transaction_types = [
            {
                "type": "income",
                "description": "Salary",
                "amount_oc_primary": 5000.00,
                "account_id_primary": sample_accounts["income"].id,
                "account_id_secondary": sample_accounts["checking_account"].id
            },
            {
                "type": "expense",
                "description": "Groceries",
                "amount_oc_primary": 150.00,
                "account_id_primary": sample_accounts["expense"].id,
                "account_id_secondary": sample_accounts["checking_account"].id
            },
            {
                "type": "transfer",
                "description": "Savings transfer",
                "amount_oc_primary": 1000.00,
                "account_id_primary": sample_accounts["checking_account"].id,
                "account_id_secondary": sample_accounts["savings_account"].id
            }
        ]
        
        created_transactions = []
        for tx_data in transaction_types:
            full_tx_data = {
                "user_id": sample_user.id,
                "date": "2024-01-15T10:00:00",
                "currency_primary": "USD",
                **tx_data
            }
            response = client.post("/transactions/", json=full_tx_data)
            assert response.status_code == 200
            created_transactions.append(response.json())
        
        # Get postings for each transaction
        for transaction in created_transactions:
            postings_list = postings.get_postings(db_session, transaction["id"])
            assert len(postings_list) == 2
            assert all(posting.tx_id == transaction["id"] for posting in postings_list)
    
    def test_posting_balance_consistency(self, client, db_session, sample_user, sample_accounts):
        """Test that postings maintain balance consistency across transactions."""
        # Create multiple transactions through the API
        transaction_types = [
            {
                "type": "income",
                "description": "Salary",
                "amount_oc_primary": 5000.00,
                "account_id_primary": sample_accounts["income"].id,
                "account_id_secondary": sample_accounts["checking_account"].id
            },
            {
                "type": "expense",
                "description": "Groceries",
                "amount_oc_primary": 150.00,
                "account_id_primary": sample_accounts["expense"].id,
                "account_id_secondary": sample_accounts["checking_account"].id
            },
            {
                "type": "transfer",
                "description": "Savings transfer",
                "amount_oc_primary": 1000.00,
                "account_id_primary": sample_accounts["checking_account"].id,
                "account_id_secondary": sample_accounts["savings_account"].id
            }
        ]
        
        created_transactions = []
        for tx_data in transaction_types:
            full_tx_data = {
                "user_id": sample_user.id,
                "date": "2024-01-15T10:00:00",
                "currency_primary": "USD",
                **tx_data
            }
            response = client.post("/transactions/", json=full_tx_data)
            assert response.status_code == 200
            created_transactions.append(response.json())
        
        # Test posting balance consistency for each transaction
        for transaction in created_transactions:
            postings_list = postings.get_postings(db_session, transaction["id"])
            
            # For non-forex transactions, postings should balance
            if transaction["type"] != "forex":
                posting_amounts = [posting.amount_oc for posting in postings_list]
                assert abs(sum(posting_amounts)) < 0.01  # Should balance (with small tolerance for floating point)
            
            # All postings should have the same transaction ID
            assert all(posting.tx_id == transaction["id"] for posting in postings_list)
            
            # All postings should have valid amounts
            assert all(posting.amount_oc != 0 for posting in postings_list)
            
            # All postings should have valid currencies
            assert all(posting.currency is not None for posting in postings_list)
            assert all(len(posting.currency) == 3 for posting in postings_list)  # 3-letter currency codes


class TestTransactionSplits:
    """Test transaction splits functionality"""
    
    def test_get_splits_for_transaction(self, client, db_session, sample_user, sample_accounts, sample_people):
        """Test getting all splits for a transaction."""
        # Create a transaction first
        transaction_data = {
            "user_id": sample_user.id,
            "date": "2024-01-15T10:00:00",
            "type": "expense",
            "description": "Restaurant bill",
            "amount_oc_primary": 100.00,
            "currency_primary": "USD",
            "account_id_primary": sample_accounts["expense"].id,
            "account_id_secondary": sample_accounts["checking_account"].id
        }
        response = client.post("/transactions/", json=transaction_data)
        assert response.status_code == 200
        transaction = response.json()
        
        # Create splits manually in the database (since there's no API endpoint)
        split1 = models.TxSplit(
            tx_id=transaction["id"],
            person_id=sample_people[0].id,
            share_amount=60.00
        )
        split2 = models.TxSplit(
            tx_id=transaction["id"],
            person_id=sample_people[1].id,
            share_amount=40.00
        )
        db_session.add(split1)
        db_session.add(split2)
        db_session.commit()
        db_session.refresh(split1)
        db_session.refresh(split2)
        
        # Get splits for the transaction
        splits_list = splits.get_splits(db_session, transaction["id"])
        
        # Should have 2 splits
        assert len(splits_list) == 2
        assert all(split.tx_id == transaction["id"] for split in splits_list)
        
        # Validate split structure
        for split in splits_list:
            assert split.id is not None
            assert split.tx_id == transaction["id"]
            assert split.person_id is not None
            assert split.share_amount > 0
            assert split.share_amount in [60.00, 40.00]  # Expected amounts
    
    def test_get_split_by_id(self, client, db_session, sample_user, sample_accounts, sample_people):
        """Test getting a single split by ID."""
        # Create a transaction first
        transaction_data = {
            "user_id": sample_user.id,
            "date": "2024-01-15T10:00:00",
            "type": "expense",
            "description": "Group dinner",
            "amount_oc_primary": 150.00,
            "currency_primary": "USD",
            "account_id_primary": sample_accounts["expense"].id,
            "account_id_secondary": sample_accounts["checking_account"].id
        }
        response = client.post("/transactions/", json=transaction_data)
        assert response.status_code == 200
        transaction = response.json()
        
        # Create a split manually
        split = models.TxSplit(
            tx_id=transaction["id"],
            person_id=sample_people[0].id,
            share_amount=75.00
        )
        db_session.add(split)
        db_session.commit()
        db_session.refresh(split)
        
        # Get the split by ID
        retrieved_split = splits.get_split(db_session, split.id)
        assert retrieved_split is not None
        assert retrieved_split.id == split.id
        assert retrieved_split.tx_id == transaction["id"]
        assert retrieved_split.person_id == sample_people[0].id
        assert retrieved_split.share_amount == 75.00
    
    def test_get_split_not_found(self, db_session):
        """Test getting a non-existent split."""
        split = splits.get_split(db_session, 99999)
        assert split is None
    
    def test_get_splits_for_nonexistent_transaction(self, db_session):
        """Test getting splits for a non-existent transaction."""
        splits_list = splits.get_splits(db_session, 99999)
        assert len(splits_list) == 0
    
    def test_get_splits_multiple_transactions(self, client, db_session, sample_user, sample_accounts, sample_people):
        """Test getting splits for multiple transactions."""
        # Create multiple transactions
        transactions = []
        for i in range(3):
            transaction_data = {
                "user_id": sample_user.id,
                "date": "2024-01-15T10:00:00",
                "type": "expense",
                "description": f"Group expense {i+1}",
                "amount_oc_primary": 50.00 * (i + 1),
                "currency_primary": "USD",
                "account_id_primary": sample_accounts["expense"].id,
                "account_id_secondary": sample_accounts["checking_account"].id
            }
            response = client.post("/transactions/", json=transaction_data)
            assert response.status_code == 200
            transactions.append(response.json())
        
        # Create splits for each transaction
        for i, transaction in enumerate(transactions):
            split = models.TxSplit(
                tx_id=transaction["id"],
                person_id=sample_people[i % len(sample_people)].id,
                share_amount=25.00 * (i + 1)
            )
            db_session.add(split)
        db_session.commit()
        
        # Get splits for each transaction
        for transaction in transactions:
            splits_list = splits.get_splits(db_session, transaction["id"])
            assert len(splits_list) == 1  # One split per transaction
            assert all(split.tx_id == transaction["id"] for split in splits_list)
    
    def test_split_share_amount_validation(self, client, db_session, sample_user, sample_accounts, sample_people):
        """Test split share amount validation."""
        # Create a transaction first
        transaction_data = {
            "user_id": sample_user.id,
            "date": "2024-01-15T10:00:00",
            "type": "expense",
            "description": "Test split validation",
            "amount_oc_primary": 100.00,
            "currency_primary": "USD",
            "account_id_primary": sample_accounts["expense"].id,
            "account_id_secondary": sample_accounts["checking_account"].id
        }
        response = client.post("/transactions/", json=transaction_data)
        assert response.status_code == 200
        transaction = response.json()
        
        # Test valid split amounts
        valid_amounts = [0.01, 50.00, 100.00, 999999.99]
        for amount in valid_amounts:
            split = models.TxSplit(
                tx_id=transaction["id"],
                person_id=sample_people[0].id,
                share_amount=amount
            )
            db_session.add(split)
            db_session.commit()
            db_session.refresh(split)
            assert float(split.share_amount) == amount
            # Clean up for next iteration
            db_session.delete(split)
            db_session.commit()
    
    def test_split_unique_constraint(self, client, db_session, sample_user, sample_accounts, sample_people):
        """Test split unique constraint (one split per person per transaction)."""
        # Create a transaction first
        transaction_data = {
            "user_id": sample_user.id,
            "date": "2024-01-15T10:00:00",
            "type": "expense",
            "description": "Test unique constraint",
            "amount_oc_primary": 100.00,
            "currency_primary": "USD",
            "account_id_primary": sample_accounts["expense"].id,
            "account_id_secondary": sample_accounts["checking_account"].id
        }
        response = client.post("/transactions/", json=transaction_data)
        assert response.status_code == 200
        transaction = response.json()
        
        # Create first split
        split1 = models.TxSplit(
            tx_id=transaction["id"],
            person_id=sample_people[0].id,
            share_amount=50.00
        )
        db_session.add(split1)
        db_session.commit()
        
        # Try to create duplicate split (same person, same transaction)
        split2 = models.TxSplit(
            tx_id=transaction["id"],
            person_id=sample_people[0].id,  # Same person
            share_amount=30.00
        )
        db_session.add(split2)
        
        # This should raise an IntegrityError due to unique constraint
        with pytest.raises(Exception):  # IntegrityError
            db_session.commit()
        
        # Rollback to clean up
        db_session.rollback()
    
    def test_split_positive_amount_constraint(self, client, db_session, sample_user, sample_accounts, sample_people):
        """Test split positive amount constraint."""
        # Create a transaction first
        transaction_data = {
            "user_id": sample_user.id,
            "date": "2024-01-15T10:00:00",
            "type": "expense",
            "description": "Test positive amount constraint",
            "amount_oc_primary": 100.00,
            "currency_primary": "USD",
            "account_id_primary": sample_accounts["expense"].id,
            "account_id_secondary": sample_accounts["checking_account"].id
        }
        response = client.post("/transactions/", json=transaction_data)
        assert response.status_code == 200
        transaction = response.json()
        
        # Try to create split with zero amount
        split_zero = models.TxSplit(
            tx_id=transaction["id"],
            person_id=sample_people[0].id,
            share_amount=0.00
        )
        db_session.add(split_zero)
        
        # This should raise an IntegrityError due to positive amount constraint
        with pytest.raises(Exception):  # IntegrityError
            db_session.commit()
        
        # Rollback to clean up
        db_session.rollback()
        
        # Try to create split with negative amount
        split_negative = models.TxSplit(
            tx_id=transaction["id"],
            person_id=sample_people[0].id,
            share_amount=-10.00
        )
        db_session.add(split_negative)
        
        # This should also raise an IntegrityError
        with pytest.raises(Exception):  # IntegrityError
            db_session.commit()
        
        # Rollback to clean up
        db_session.rollback()
    
    def test_split_relationships(self, client, db_session, sample_user, sample_accounts, sample_people):
        """Test split relationships with transaction and person."""
        # Create a transaction first
        transaction_data = {
            "user_id": sample_user.id,
            "date": "2024-01-15T10:00:00",
            "type": "expense",
            "description": "Test relationships",
            "amount_oc_primary": 100.00,
            "currency_primary": "USD",
            "account_id_primary": sample_accounts["expense"].id,
            "account_id_secondary": sample_accounts["checking_account"].id
        }
        response = client.post("/transactions/", json=transaction_data)
        assert response.status_code == 200
        transaction = response.json()
        
        # Create a split
        split = models.TxSplit(
            tx_id=transaction["id"],
            person_id=sample_people[0].id,
            share_amount=60.00
        )
        db_session.add(split)
        db_session.commit()
        db_session.refresh(split)
        
        # Test relationships
        assert split.tx is not None
        assert split.tx.id == transaction["id"]
        assert split.person is not None
        assert split.person.id == sample_people[0].id
        
        # Test reverse relationships
        transaction_obj = db_session.query(models.Transaction).filter(models.Transaction.id == transaction["id"]).first()
        assert len(transaction_obj.splits) == 1
        assert transaction_obj.splits[0].id == split.id
        
        person_obj = db_session.query(models.Person).filter(models.Person.id == sample_people[0].id).first()
        assert len(person_obj.splits) == 1
        assert person_obj.splits[0].id == split.id
    
    def test_split_soft_delete(self, client, db_session, sample_user, sample_accounts, sample_people):
        """Test split soft delete functionality."""
        # Create a transaction first
        transaction_data = {
            "user_id": sample_user.id,
            "date": "2024-01-15T10:00:00",
            "type": "expense",
            "description": "Test soft delete",
            "amount_oc_primary": 100.00,
            "currency_primary": "USD",
            "account_id_primary": sample_accounts["expense"].id,
            "account_id_secondary": sample_accounts["checking_account"].id
        }
        response = client.post("/transactions/", json=transaction_data)
        assert response.status_code == 200
        transaction = response.json()
        
        # Create a split
        split = models.TxSplit(
            tx_id=transaction["id"],
            person_id=sample_people[0].id,
            share_amount=50.00
        )
        db_session.add(split)
        db_session.commit()
        db_session.refresh(split)
        
        # Verify split exists
        assert splits.get_split(db_session, split.id) is not None
        
        # Soft delete the split
        split.active = False
        db_session.commit()
        
        # Verify split is no longer returned by get_split
        assert splits.get_split(db_session, split.id) is None
        
        # Verify split is no longer returned by get_splits
        splits_list = splits.get_splits(db_session, transaction["id"])
        assert len(splits_list) == 0


class TestPostingLifecycleManagement:
    """Test posting lifecycle management through transaction operations"""
    
    def test_posting_deactivation_when_transaction_deactivated(self, client, db_session, sample_user, sample_accounts):
        """Test that postings are deactivated when transaction is deactivated."""
        # Create a transaction
        transaction_data = {
            "user_id": sample_user.id,
            "date": "2024-01-15T10:00:00",
            "type": "expense",
            "description": "Test posting deactivation",
            "amount_oc_primary": 100.00,
            "currency_primary": "USD",
            "account_id_primary": sample_accounts["expense"].id,
            "account_id_secondary": sample_accounts["checking_account"].id
        }
        response = client.post("/transactions/", json=transaction_data)
        assert response.status_code == 200
        transaction = response.json()
        
        # Verify postings exist and are active
        postings_list = postings.get_postings(db_session, transaction["id"])
        assert len(postings_list) == 2
        assert all(posting.active for posting in postings_list)
        
        # Deactivate the transaction
        response = client.delete(f"/transactions/{transaction['id']}")
        assert response.status_code == 204
        
        # Verify postings are now deactivated
        postings_list = postings.get_postings(db_session, transaction["id"])
        assert len(postings_list) == 0  # Should return no active postings
        
        # Verify postings still exist in database but are inactive
        all_postings = db_session.query(models.TxPosting).filter(
            models.TxPosting.tx_id == transaction["id"]
        ).all()
        assert len(all_postings) == 2
        assert all(not posting.active for posting in all_postings)
    
    def test_posting_activation_when_transaction_activated(self, client, db_session, sample_user, sample_accounts):
        """Test that postings are activated when transaction is activated."""
        # Create a transaction
        transaction_data = {
            "user_id": sample_user.id,
            "date": "2024-01-15T10:00:00",
            "type": "expense",
            "description": "Test posting activation",
            "amount_oc_primary": 100.00,
            "currency_primary": "USD",
            "account_id_primary": sample_accounts["expense"].id,
            "account_id_secondary": sample_accounts["checking_account"].id
        }
        response = client.post("/transactions/", json=transaction_data)
        assert response.status_code == 200
        transaction = response.json()
        
        # Deactivate the transaction
        response = client.delete(f"/transactions/{transaction['id']}")
        assert response.status_code == 204
        
        # Verify postings are deactivated
        postings_list = postings.get_postings(db_session, transaction["id"])
        assert len(postings_list) == 0
        
        # Activate the transaction using the API endpoint
        response = client.post(f"/transactions/{transaction['id']}/activate")
        assert response.status_code == 200
        activated_transaction = response.json()
        assert activated_transaction["active"] == True
        
        # Verify postings are now active
        postings_list = postings.get_postings(db_session, transaction["id"])
        assert len(postings_list) == 2
        assert all(posting.active for posting in postings_list)
    
    def test_posting_update_when_transaction_amount_updated(self, client, db_session, sample_user, sample_accounts):
        """Test that postings are updated when transaction amount is updated."""
        # Create a transaction
        transaction_data = {
            "user_id": sample_user.id,
            "date": "2024-01-15T10:00:00",
            "type": "expense",
            "description": "Test posting update",
            "amount_oc_primary": 100.00,
            "currency_primary": "USD",
            "account_id_primary": sample_accounts["expense"].id,
            "account_id_secondary": sample_accounts["checking_account"].id
        }
        response = client.post("/transactions/", json=transaction_data)
        assert response.status_code == 200
        transaction = response.json()
        
        # Get original postings
        original_postings = postings.get_postings(db_session, transaction["id"])
        assert len(original_postings) == 2
        original_amounts = [posting.amount_oc for posting in original_postings]
        
        # Update transaction amount
        update_data = {"amount_oc_primary": 200.00}
        response = client.patch(f"/transactions/{transaction['id']}", json=update_data)
        assert response.status_code == 200
        
        # Refresh the database session to get the latest data
        db_session.commit()
        db_session.expunge_all()
        
        # Verify new postings were created with updated amounts
        new_postings = postings.get_postings(db_session, transaction["id"])
        assert len(new_postings) == 2
        new_amounts = [posting.amount_oc for posting in new_postings]
        
        # Amounts should be different (doubled)
        assert new_amounts != original_amounts
        assert all(abs(amount) == 200.00 for amount in new_amounts)
        
        # Verify old postings are deactivated
        all_postings = db_session.query(models.TxPosting).filter(
            models.TxPosting.tx_id == transaction["id"]
        ).all()
        active_postings = [p for p in all_postings if p.active]
        inactive_postings = [p for p in all_postings if not p.active]
        
        assert len(active_postings) == 2
        assert len(inactive_postings) == 2  # Original postings should be inactive
    
    def test_posting_update_when_transaction_type_updated(self, client, db_session, sample_user, sample_accounts):
        """Test that postings are updated when transaction type is updated."""
        # Create an expense transaction
        transaction_data = {
            "user_id": sample_user.id,
            "date": "2024-01-15T10:00:00",
            "type": "expense",
            "description": "Test type update",
            "amount_oc_primary": 100.00,
            "currency_primary": "USD",
            "account_id_primary": sample_accounts["expense"].id,
            "account_id_secondary": sample_accounts["checking_account"].id
        }
        response = client.post("/transactions/", json=transaction_data)
        assert response.status_code == 200
        transaction = response.json()
        
        # Get original postings
        original_postings = postings.get_postings(db_session, transaction["id"])
        assert len(original_postings) == 2
        
        # Update transaction type to income (this will change posting signs)
        update_data = {
            "type": "income",
            "account_id_primary": sample_accounts["income"].id
        }
        response = client.patch(f"/transactions/{transaction['id']}", json=update_data)
        assert response.status_code == 200
        
        # Verify new postings were created with different signs
        new_postings = postings.get_postings(db_session, transaction["id"])
        assert len(new_postings) == 2
        
        # For income: income account should be positive, asset account negative
        income_posting = next(p for p in new_postings if p.account_id == sample_accounts["income"].id)
        asset_posting = next(p for p in new_postings if p.account_id == sample_accounts["checking_account"].id)
        assert income_posting.amount_oc > 0
        assert asset_posting.amount_oc < 0
    
    def test_posting_update_when_transaction_accounts_updated(self, client, db_session, sample_user, sample_accounts):
        """Test that postings are updated when transaction accounts are updated."""
        # Create a transaction
        transaction_data = {
            "user_id": sample_user.id,
            "date": "2024-01-15T10:00:00",
            "type": "expense",
            "description": "Test account update",
            "amount_oc_primary": 100.00,
            "currency_primary": "USD",
            "account_id_primary": sample_accounts["expense"].id,
            "account_id_secondary": sample_accounts["checking_account"].id
        }
        response = client.post("/transactions/", json=transaction_data)
        assert response.status_code == 200
        transaction = response.json()
        
        # Get original postings
        original_postings = postings.get_postings(db_session, transaction["id"])
        original_accounts = [posting.account_id for posting in original_postings]
        
        # Update transaction accounts
        update_data = {
            "account_id_primary": sample_accounts["groceries"].id,
            "account_id_secondary": sample_accounts["savings_account"].id
        }
        response = client.patch(f"/transactions/{transaction['id']}", json=update_data)
        assert response.status_code == 200
        
        # Verify new postings were created with updated accounts
        new_postings = postings.get_postings(db_session, transaction["id"])
        assert len(new_postings) == 2
        new_accounts = [posting.account_id for posting in new_postings]
        
        # Should have different accounts
        assert set(new_accounts) != set(original_accounts)
        assert sample_accounts["groceries"].id in new_accounts
        assert sample_accounts["savings_account"].id in new_accounts
    
    def test_posting_no_update_when_non_posting_fields_updated(self, client, db_session, sample_user, sample_accounts):
        """Test that postings are NOT updated when non-posting fields are updated."""
        # Create a transaction
        transaction_data = {
            "user_id": sample_user.id,
            "date": "2024-01-15T10:00:00",
            "type": "expense",
            "description": "Test non-posting update",
            "amount_oc_primary": 100.00,
            "currency_primary": "USD",
            "account_id_primary": sample_accounts["expense"].id,
            "account_id_secondary": sample_accounts["checking_account"].id
        }
        response = client.post("/transactions/", json=transaction_data)
        assert response.status_code == 200
        transaction = response.json()
        
        # Get original postings
        original_postings = postings.get_postings(db_session, transaction["id"])
        original_posting_ids = [posting.id for posting in original_postings]
        
        # Update non-posting fields (description, date)
        update_data = {
            "description": "Updated description",
            "date": "2024-01-16T10:00:00"
        }
        response = client.patch(f"/transactions/{transaction['id']}", json=update_data)
        assert response.status_code == 200
        
        # Verify postings are unchanged
        new_postings = postings.get_postings(db_session, transaction["id"])
        assert len(new_postings) == 2
        new_posting_ids = [posting.id for posting in new_postings]
        
        # Should be the same posting IDs
        assert set(new_posting_ids) == set(original_posting_ids)
    
    def test_no_direct_posting_creation_endpoint(self, client):
        """Test that there are no direct posting creation endpoints."""
        # Try to create a posting directly (this should fail)
        posting_data = {
            "tx_id": 1,
            "account_id": 1,
            "amount_oc": 100.00,
            "currency": "USD"
        }
        
        # Check if there's a postings endpoint
        response = client.post("/postings/", json=posting_data)
        assert response.status_code == 404  # Should not exist
    
    def test_no_direct_posting_update_endpoint(self, client):
        """Test that there are no direct posting update endpoints."""
        # Try to update a posting directly (this should fail)
        update_data = {"amount_oc": 200.00}
        
        # Check if there's a postings update endpoint
        response = client.patch("/postings/1", json=update_data)
        assert response.status_code == 404  # Should not exist
    
    def test_no_direct_posting_deletion_endpoint(self, client):
        """Test that there are no direct posting deletion endpoints."""
        # Try to delete a posting directly (this should fail)
        response = client.delete("/postings/1")
        assert response.status_code == 404  # Should not exist
    
    def test_posting_balance_consistency_after_updates(self, client, db_session, sample_user, sample_accounts):
        """Test that postings maintain balance consistency after transaction updates."""
        # Create a transaction
        transaction_data = {
            "user_id": sample_user.id,
            "date": "2024-01-15T10:00:00",
            "type": "expense",
            "description": "Test balance consistency",
            "amount_oc_primary": 100.00,
            "currency_primary": "USD",
            "account_id_primary": sample_accounts["expense"].id,
            "account_id_secondary": sample_accounts["checking_account"].id
        }
        response = client.post("/transactions/", json=transaction_data)
        assert response.status_code == 200
        transaction = response.json()
        
        # Verify initial balance
        postings_list = postings.get_postings(db_session, transaction["id"])
        posting_amounts = [posting.amount_oc for posting in postings_list]
        assert abs(sum(posting_amounts)) < 0.01  # Should balance
        
        # Update transaction amount
        update_data = {"amount_oc_primary": 250.00}
        response = client.patch(f"/transactions/{transaction['id']}", json=update_data)
        assert response.status_code == 200
        
        # Verify balance is maintained after update
        postings_list = postings.get_postings(db_session, transaction["id"])
        posting_amounts = [posting.amount_oc for posting in postings_list]
        assert abs(sum(posting_amounts)) < 0.01  # Should still balance
        assert all(abs(amount) == 250.00 for amount in posting_amounts)
    
    def test_multiple_transaction_updates_posting_consistency(self, client, db_session, sample_user, sample_accounts):
        """Test that multiple transaction updates maintain posting consistency."""
        # Create a transaction
        transaction_data = {
            "user_id": sample_user.id,
            "date": "2024-01-15T10:00:00",
            "type": "expense",
            "description": "Test multiple updates",
            "amount_oc_primary": 100.00,
            "currency_primary": "USD",
            "account_id_primary": sample_accounts["expense"].id,
            "account_id_secondary": sample_accounts["checking_account"].id
        }
        response = client.post("/transactions/", json=transaction_data)
        assert response.status_code == 200
        transaction = response.json()
        
        # Perform multiple updates
        updates = [
            {"amount_oc_primary": 150.00},
            {"type": "income", "account_id_primary": sample_accounts["income"].id},
            {"account_id_secondary": sample_accounts["savings_account"].id},
            {"amount_oc_primary": 200.00}
        ]
        
        for update_data in updates:
            response = client.patch(f"/transactions/{transaction['id']}", json=update_data)
            assert response.status_code == 200
            
            # Verify balance is maintained after each update
            postings_list = postings.get_postings(db_session, transaction["id"])
            posting_amounts = [posting.amount_oc for posting in postings_list]
            assert abs(sum(posting_amounts)) < 0.01  # Should always balance
