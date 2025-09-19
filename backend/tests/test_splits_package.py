"""
Test cases for package-based splits functionality (Splitwise-like behavior).
"""

class TestSplitsPackage:
    """Test cases for package-based splits management"""
    
    def test_get_splits_empty(self, client, sample_user, sample_accounts):
        """Test getting splits for a transaction with no splits."""
        # Create a transaction
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
        transaction = response.json()
        
        # Get splits (should be empty)
        response = client.get(f"/users/{sample_user.id}/transactions/{transaction['id']}/splits/")
        assert response.status_code == 200
        splits = response.json()
        assert len(splits) == 0
    
    def test_set_splits_success(self, client, sample_user, sample_accounts, sample_people):
        """Test setting splits for a transaction."""
        # Create a transaction
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
        transaction = response.json()
        
        # Set splits
        splits_data = [
            {"person_id": sample_people[0].id, "share_amount": 60.00},
            {"person_id": sample_people[1].id, "share_amount": 40.00}
        ]
        response = client.put(f"/users/{sample_user.id}/transactions/{transaction['id']}/splits/", json=splits_data)
        assert response.status_code == 200
        splits = response.json()
        assert len(splits) == 2
        assert sum(split["share_amount"] for split in splits) == 100.00
    
    def test_set_splits_invalid_amount(self, client, sample_user, sample_accounts, sample_people):
        """Test setting splits that don't sum to transaction amount."""
        # Create a transaction
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
        transaction = response.json()
        
        # Try to set splits that don't sum to transaction amount
        splits_data = [
            {"person_id": sample_people[0].id, "share_amount": 60.00},
            {"person_id": sample_people[1].id, "share_amount": 50.00}  # Total: 110, should be 100
        ]
        response = client.put(f"/users/{sample_user.id}/transactions/{transaction['id']}/splits/", json=splits_data)
        assert response.status_code == 422
        assert "must equal transaction amount" in response.json()["detail"]
    
    def test_replace_splits(self, client, sample_user, sample_accounts, sample_people):
        """Test replacing existing splits with new ones."""
        # Create a transaction
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
        transaction = response.json()
        
        # Set initial splits
        initial_splits = [
            {"person_id": sample_people[0].id, "share_amount": 60.00},
            {"person_id": sample_people[1].id, "share_amount": 40.00}
        ]
        response = client.put(f"/users/{sample_user.id}/transactions/{transaction['id']}/splits/", json=initial_splits)
        assert response.status_code == 200
        
        # Replace with new splits
        new_splits = [
            {"person_id": sample_people[0].id, "share_amount": 50.00},
            {"person_id": sample_people[1].id, "share_amount": 30.00},
            {"person_id": sample_people[2].id, "share_amount": 20.00}
        ]
        response = client.put(f"/users/{sample_user.id}/transactions/{transaction['id']}/splits/", json=new_splits)
        assert response.status_code == 200
        splits = response.json()
        assert len(splits) == 3
        assert sum(split["share_amount"] for split in splits) == 100.00
    
    def test_clear_splits(self, client, sample_user, sample_accounts, sample_people):
        """Test clearing all splits for a transaction."""
        # Create a transaction
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
        transaction = response.json()
        
        # Set splits
        splits_data = [
            {"person_id": sample_people[0].id, "share_amount": 60.00},
            {"person_id": sample_people[1].id, "share_amount": 40.00}
        ]
        response = client.put(f"/users/{sample_user.id}/transactions/{transaction['id']}/splits/", json=splits_data)
        assert response.status_code == 200
        
        # Clear splits
        response = client.delete(f"/users/{sample_user.id}/transactions/{transaction['id']}/splits/")
        assert response.status_code == 200
        
        # Verify splits are cleared
        response = client.get(f"/users/{sample_user.id}/transactions/{transaction['id']}/splits/")
        assert response.status_code == 200
        splits = response.json()
        assert len(splits) == 0
    
    def test_validate_splits_valid(self, client, sample_user, sample_accounts, sample_people):
        """Test validation when splits sum to transaction amount."""
        # Create a transaction
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
        transaction = response.json()
        
        # Set splits
        splits_data = [
            {"person_id": sample_people[0].id, "share_amount": 60.00},
            {"person_id": sample_people[1].id, "share_amount": 40.00}
        ]
        response = client.put(f"/users/{sample_user.id}/transactions/{transaction['id']}/splits/", json=splits_data)
        assert response.status_code == 200
        
        # Validate splits
        response = client.get(f"/users/{sample_user.id}/transactions/{transaction['id']}/splits/validation")
        assert response.status_code == 200
        validation = response.json()
        assert validation["is_valid"] == True
        assert validation["transaction_amount"] == 100.00
        assert validation["total_split_amount"] == 100.00
        assert validation["difference"] < 0.01
    
    def test_validate_splits_invalid(self, client, sample_user, sample_accounts, sample_people):
        """Test validation when splits don't sum to transaction amount."""
        # Create a transaction
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
        transaction = response.json()
        
        # Set partial splits (this should fail)
        splits_data = [
            {"person_id": sample_people[0].id, "share_amount": 60.00}
        ]
        response = client.put(f"/users/{sample_user.id}/transactions/{transaction['id']}/splits/", json=splits_data)
        assert response.status_code == 422  # Should fail validation
    
    def test_splits_with_transaction_deletion(self, client, sample_user, sample_accounts, sample_people):
        """Test that transaction deletion cascades to splits."""
        # Create a transaction
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
        transaction = response.json()
        
        # Set splits
        splits_data = [
            {"person_id": sample_people[0].id, "share_amount": 60.00},
            {"person_id": sample_people[1].id, "share_amount": 40.00}
        ]
        response = client.put(f"/users/{sample_user.id}/transactions/{transaction['id']}/splits/", json=splits_data)
        assert response.status_code == 200
        
        # Verify splits exist
        response = client.get(f"/users/{sample_user.id}/transactions/{transaction['id']}/splits/")
        assert response.status_code == 200
        assert len(response.json()) == 2
        
        # Delete transaction (soft delete)
        response = client.delete(f"/users/{sample_user.id}/transactions/{transaction['id']}")
        assert response.status_code == 204
        
        # Verify splits are no longer accessible
        response = client.get(f"/users/{sample_user.id}/transactions/{transaction['id']}/splits/")
        assert response.status_code == 404
    
    def test_splits_with_transaction_activation(self, client, sample_user, sample_accounts, sample_people):
        """Test that transaction activation cascades to splits."""
        # Create a transaction
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
        transaction = response.json()
        
        # Set splits
        splits_data = [
            {"person_id": sample_people[0].id, "share_amount": 60.00},
            {"person_id": sample_people[1].id, "share_amount": 40.00}
        ]
        response = client.put(f"/users/{sample_user.id}/transactions/{transaction['id']}/splits/", json=splits_data)
        assert response.status_code == 200
        
        # Delete transaction (soft delete)
        response = client.delete(f"/users/{sample_user.id}/transactions/{transaction['id']}")
        assert response.status_code == 204
        
        # Verify splits are not accessible
        response = client.get(f"/users/{sample_user.id}/transactions/{transaction['id']}/splits/")
        assert response.status_code == 404
        
        # Activate transaction
        response = client.post(f"/users/{sample_user.id}/transactions/{transaction['id']}/activate")
        assert response.status_code == 200
        
        # Verify splits are accessible again
        response = client.get(f"/users/{sample_user.id}/transactions/{transaction['id']}/splits/")
        assert response.status_code == 200
        assert len(response.json()) == 2
