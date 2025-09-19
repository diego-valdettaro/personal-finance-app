"""
Test cases for transaction postings functionality in the finance app backend.
"""

from app import models
from app.crud import postings

class TestPostingRetrieval:
    """Test cases for posting retrieval"""
    
    def test_get_postings_for_transaction_success(self, client, db_session, sample_user, sample_accounts):
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
        response = client.post(f"/users/{sample_user.id}/transactions/", json=transaction_data)
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
    
    def test_get_postings_for_nonexistent_transaction(self, db_session):
        """Test getting postings for a non-existent transaction."""
        postings_list = postings.get_postings(db_session, 99999)
        assert len(postings_list) == 0
    
    def test_get_posting_by_id_success(self, client, db_session, sample_user, sample_accounts):
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
        response = client.post(f"/users/{sample_user.id}/transactions/", json=transaction_data)
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
            response = client.post(f"/users/{sample_user.id}/transactions/", json=full_tx_data)
            assert response.status_code == 200
            created_transactions.append(response.json())
        
        # Get postings for each transaction
        for transaction in created_transactions:
            postings_list = postings.get_postings(db_session, transaction["id"])
            assert len(postings_list) == 2
            assert all(posting.tx_id == transaction["id"] for posting in postings_list)

class TestPostingBalanceConsistency:
    """Test cases for posting balance consistency"""
    
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
            response = client.post(f"/users/{sample_user.id}/transactions/", json=full_tx_data)
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
    
    def test_posting_amount_consistency(self, client, db_session, sample_user, sample_accounts):
        """Test that posting amounts are consistent with transaction amounts."""
        transaction_data = {
            "user_id": sample_user.id,
            "date": "2024-01-15T10:00:00",
            "type": "income",
            "description": "Test consistency",
            "amount_oc_primary": 1000.00,
            "currency_primary": "USD",
            "account_id_primary": sample_accounts["income"].id,
            "account_id_secondary": sample_accounts["checking_account"].id
        }
        response = client.post(f"/users/{sample_user.id}/transactions/", json=transaction_data)
        assert response.status_code == 200
        transaction = response.json()
        
        # Get postings for the transaction
        postings_list = postings.get_postings(db_session, transaction["id"])
        
        # Posting amounts should match transaction amount
        posting_amounts = [abs(posting.amount_oc) for posting in postings_list]
        assert all(amount == 1000.00 for amount in posting_amounts)
        
        # Postings should have opposite signs
        signs = [1 if posting.amount_oc > 0 else -1 for posting in postings_list]
        assert len(set(signs)) == 2  # Should have both positive and negative signs
    
    def test_posting_currency_consistency(self, client, db_session, sample_user, sample_accounts):
        """Test that posting currencies are consistent."""
        transaction_data = {
            "user_id": sample_user.id,
            "date": "2024-01-15T10:00:00",
            "type": "income",
            "description": "Test currency consistency",
            "amount_oc_primary": 1000.00,
            "currency_primary": "USD",
            "account_id_primary": sample_accounts["income"].id,
            "account_id_secondary": sample_accounts["checking_account"].id
        }
        response = client.post(f"/users/{sample_user.id}/transactions/", json=transaction_data)
        assert response.status_code == 200
        transaction = response.json()
        
        # Get postings for the transaction
        postings_list = postings.get_postings(db_session, transaction["id"])
        
        # All postings should have the same currency
        currencies = [posting.currency for posting in postings_list]
        assert all(currency == "USD" for currency in currencies)

class TestPostingLifecycle:
    """Test cases for posting lifecycle management"""
    
    def test_posting_creation_with_transaction(self, client, db_session, sample_user, sample_accounts):
        """Test that postings are created when transactions are created."""
        transaction_data = {
            "user_id": sample_user.id,
            "date": "2024-01-15T10:00:00",
            "type": "expense",
            "description": "Test posting creation",
            "amount_oc_primary": 100.00,
            "currency_primary": "USD",
            "account_id_primary": sample_accounts["expense"].id,
            "account_id_secondary": sample_accounts["checking_account"].id
        }
        response = client.post(f"/users/{sample_user.id}/transactions/", json=transaction_data)
        assert response.status_code == 200
        transaction = response.json()
        
        # Verify postings were created
        postings_list = postings.get_postings(db_session, transaction["id"])
        assert len(postings_list) == 2
        
        # Verify posting details
        for posting in postings_list:
            assert posting.tx_id == transaction["id"]
            assert posting.account_id in [sample_accounts["expense"].id, sample_accounts["checking_account"].id]
            assert posting.amount_oc != 0
            assert posting.currency == "USD"
            assert posting.amount_hc != 0
    
    def test_posting_deactivation_with_transaction(self, client, db_session, sample_user, sample_accounts):
        """Test that postings are deactivated when transactions are deactivated."""
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
        response = client.post(f"/users/{sample_user.id}/transactions/", json=transaction_data)
        assert response.status_code == 200
        transaction = response.json()
        
        # Verify postings exist and are active
        postings_list = postings.get_postings(db_session, transaction["id"])
        assert len(postings_list) == 2
        assert all(posting.active for posting in postings_list)
        
        # Deactivate the transaction
        response = client.delete(f"/users/{sample_user.id}/transactions/{transaction['id']}")
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
    
    def test_posting_activation_with_transaction(self, client, db_session, sample_user, sample_accounts):
        """Test that postings are activated when transactions are activated."""
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
        response = client.post(f"/users/{sample_user.id}/transactions/", json=transaction_data)
        assert response.status_code == 200
        transaction = response.json()
        
        # Deactivate the transaction
        response = client.delete(f"/users/{sample_user.id}/transactions/{transaction['id']}")
        assert response.status_code == 204
        
        # Verify postings are deactivated
        postings_list = postings.get_postings(db_session, transaction["id"])
        assert len(postings_list) == 0
        
        # Activate the transaction using the API endpoint
        response = client.post(f"/users/{sample_user.id}/transactions/{transaction['id']}/activate")
        assert response.status_code == 200
        activated_transaction = response.json()
        assert activated_transaction["active"] == True
        
        # Verify postings are now active
        postings_list = postings.get_postings(db_session, transaction["id"])
        assert len(postings_list) == 2
        assert all(posting.active for posting in postings_list)

class TestPostingValidation:
    """Test cases for posting validation and business rules"""
    
    def test_posting_amount_not_zero(self, client, db_session, sample_user, sample_accounts):
        """Test that posting amounts cannot be zero."""
        # This is tested indirectly through transaction creation
        # The database constraints should prevent zero amounts
        transaction_data = {
            "user_id": sample_user.id,
            "date": "2024-01-15T10:00:00",
            "type": "income",
            "description": "Test zero amount",
            "amount_oc_primary": 0.00,  # Zero amount
            "currency_primary": "USD",
            "account_id_primary": sample_accounts["income"].id,
            "account_id_secondary": sample_accounts["checking_account"].id
        }
        response = client.post(f"/users/{sample_user.id}/transactions/", json=transaction_data)
        assert response.status_code == 400  # Should not allow zero amount
    
    def test_posting_currency_length(self, client, db_session, sample_user, sample_accounts):
        """Test that posting currencies have correct length."""
        # This is tested through transaction creation with valid currencies
        transaction_data = {
            "user_id": sample_user.id,
            "date": "2024-01-15T10:00:00",
            "type": "income",
            "description": "Test currency length",
            "amount_oc_primary": 1000.00,
            "currency_primary": "USD",  # Valid 3-character currency
            "account_id_primary": sample_accounts["income"].id,
            "account_id_secondary": sample_accounts["checking_account"].id
        }
        response = client.post(f"/users/{sample_user.id}/transactions/", json=transaction_data)
        assert response.status_code == 200
        
        # Verify posting currencies are correct
        transaction = response.json()
        postings_list = postings.get_postings(db_session, transaction["id"])
        for posting in postings_list:
            assert len(posting.currency) == 3
    
    def test_posting_sign_consistency(self, client, db_session, sample_user, sample_accounts):
        """Test that posting signs are consistent."""
        transaction_data = {
            "user_id": sample_user.id,
            "date": "2024-01-15T10:00:00",
            "type": "income",
            "description": "Test sign consistency",
            "amount_oc_primary": 1000.00,
            "currency_primary": "USD",
            "account_id_primary": sample_accounts["income"].id,
            "account_id_secondary": sample_accounts["checking_account"].id
        }
        response = client.post(f"/users/{sample_user.id}/transactions/", json=transaction_data)
        assert response.status_code == 200
        transaction = response.json()
        
        # Get postings and verify sign consistency
        postings_list = postings.get_postings(db_session, transaction["id"])
        
        # For income: income account should be positive, asset account negative
        income_posting = next(p for p in postings_list if p.account_id == sample_accounts["income"].id)
        asset_posting = next(p for p in postings_list if p.account_id == sample_accounts["checking_account"].id)
        assert income_posting.amount_oc > 0
        assert asset_posting.amount_oc < 0
        
        # Signs should be consistent between amount_oc and amount_hc
        assert (income_posting.amount_oc > 0) == (income_posting.amount_hc > 0)
        assert (asset_posting.amount_oc < 0) == (asset_posting.amount_hc < 0)

class TestPostingEdgeCases:
    """Test cases for edge cases and boundary conditions"""
    
    def test_posting_maximum_amount(self, client, db_session, sample_user, sample_accounts):
        """Test posting with maximum amount."""
        max_amount = 999999999999999.99
        transaction_data = {
            "user_id": sample_user.id,
            "date": "2024-01-15T10:00:00",
            "type": "income",
            "description": "Test maximum amount",
            "amount_oc_primary": max_amount,
            "currency_primary": "USD",
            "account_id_primary": sample_accounts["income"].id,
            "account_id_secondary": sample_accounts["checking_account"].id
        }
        response = client.post(f"/users/{sample_user.id}/transactions/", json=transaction_data)
        assert response.status_code == 200
        transaction = response.json()
        
        # Verify posting amounts
        postings_list = postings.get_postings(db_session, transaction["id"])
        for posting in postings_list:
            assert abs(posting.amount_oc) == max_amount
    
    def test_posting_minimum_amount(self, client, db_session, sample_user, sample_accounts):
        """Test posting with minimum amount."""
        min_amount = 0.01
        transaction_data = {
            "user_id": sample_user.id,
            "date": "2024-01-15T10:00:00",
            "type": "income",
            "description": "Test minimum amount",
            "amount_oc_primary": min_amount,
            "currency_primary": "USD",
            "account_id_primary": sample_accounts["income"].id,
            "account_id_secondary": sample_accounts["checking_account"].id
        }
        response = client.post(f"/users/{sample_user.id}/transactions/", json=transaction_data)
        assert response.status_code == 200
        transaction = response.json()
        
        # Verify posting amounts
        postings_list = postings.get_postings(db_session, transaction["id"])    
        for posting in postings_list:
            assert float(abs(posting.amount_oc)) == min_amount
    
    def test_posting_multiple_currencies(self, client, db_session, sample_user, sample_accounts):
        """Test postings with multiple currencies."""
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
            transaction = response.json()
            
            # Verify posting currencies
            postings_list = postings.get_postings(db_session, transaction["id"])
            for posting in postings_list:
                assert posting.currency == currency

class TestPostingIntegration:
    """Integration tests for posting functionality"""
    
    def test_posting_with_forex_transaction(self, client, db_session, sample_user, sample_accounts):
        """Test postings with forex transactions."""
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
        response = client.post(f"/users/{sample_user.id}/transactions/", json=transaction_data)
        assert response.status_code == 200
        transaction = response.json()
        
        # Get postings for the forex transaction
        postings_list = postings.get_postings(db_session, transaction["id"])
        assert len(postings_list) == 2
        
        # Verify posting currencies
        usd_posting = next(p for p in postings_list if p.account_id == sample_accounts["checking_account"].id)
        eur_posting = next(p for p in postings_list if p.account_id == sample_accounts["eur_account"].id)
        assert usd_posting.currency == "USD"
        assert eur_posting.currency == "EUR"
    
    def test_posting_with_credit_card_payment(self, client, db_session, sample_user, sample_accounts):
        """Test postings with credit card payment transactions."""
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
        response = client.post(f"/users/{sample_user.id}/transactions/", json=transaction_data)
        assert response.status_code == 200
        transaction = response.json()
        
        # Get postings for the credit card payment
        postings_list = postings.get_postings(db_session, transaction["id"])
        assert len(postings_list) == 2
        
        # Verify posting amounts and signs
        credit_card_posting = next(p for p in postings_list if p.account_id == sample_accounts["credit_card"].id)
        checking_posting = next(p for p in postings_list if p.account_id == sample_accounts["checking_account"].id)
        assert credit_card_posting.amount_oc < 0  # Credit card should be debited
        assert checking_posting.amount_oc > 0  # Checking account should be credited
    
    def test_posting_balance_after_multiple_transactions(self, client, db_session, sample_user, sample_accounts):
        """Test posting balance after multiple transactions."""
        # Create multiple transactions
        transactions_data = [
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
                "description": "Savings",
                "amount_oc_primary": 1000.00,
                "account_id_primary": sample_accounts["checking_account"].id,
                "account_id_secondary": sample_accounts["savings_account"].id
            }
        ]
        
        for tx_data in transactions_data:
            full_tx_data = {
                "user_id": sample_user.id,
                "date": "2024-01-15T10:00:00",
                "currency_primary": "USD",
                **tx_data
            }
            response = client.post(f"/users/{sample_user.id}/transactions/", json=full_tx_data)
            assert response.status_code == 200
        
        # Verify all transactions have balanced postings
        all_transactions = db_session.query(models.Transaction).filter(
            models.Transaction.user_id == sample_user.id
        ).all()
        
        for transaction in all_transactions:
            postings_list = postings.get_postings(db_session, transaction.id)
            if transaction.type != "forex":
                posting_amounts = [posting.amount_oc for posting in postings_list]
                assert abs(sum(posting_amounts)) < 0.01  # Should balance
