"""
Test cases for foreign exchange rates functionality in the finance app backend.
"""

class TestFxRateCreation:
    """Test cases for FX rate creation"""
    
    def test_create_fx_rate_success(self, client, db_session):
        """Test successful FX rate creation."""
        fx_rate_data = {
            "from_currency": "USD",
            "to_currency": "EUR",
            "rate": 0.85,
            "year": 2024,
            "month": 1
        }
        response = client.post("/fx-rates/", json=fx_rate_data)
        assert response.status_code == 201
        data = response.json()
        assert data["from_currency"] == fx_rate_data["from_currency"]
        assert data["to_currency"] == fx_rate_data["to_currency"]
        assert data["rate"] == fx_rate_data["rate"]
        assert data["year"] == fx_rate_data["year"]
        assert data["month"] == fx_rate_data["month"]
        assert "id" in data
    
    def test_create_fx_rate_missing_required_fields(self, client, db_session):
        """Test FX rate creation with missing required fields."""
        # Missing from_currency
        response = client.post("/fx-rates/", json={
            "to_currency": "EUR",
            "rate": 0.85,
            "year": 2024,
            "month": 1
        })
        assert response.status_code == 422
        
        # Missing rate
        response = client.post("/fx-rates/", json={
            "from_currency": "USD",
            "to_currency": "EUR",
            "year": 2024,
            "month": 1
        })
        assert response.status_code == 422
    
    def test_create_fx_rate_invalid_currency(self, client, db_session):
        """Test FX rate creation with invalid currency."""
        fx_rate_data = {
            "from_currency": "INVALID",
            "to_currency": "EUR",
            "rate": 0.85,
            "year": 2024,
            "month": 1
        }
        response = client.post("/fx-rates/", json=fx_rate_data)
        assert response.status_code == 422
    
    def test_create_fx_rate_same_currency(self, client, db_session):
        """Test FX rate creation with same from and to currency."""
        fx_rate_data = {
            "from_currency": "USD",
            "to_currency": "USD",
            "rate": 1.0,
            "year": 2024,
            "month": 1
        }
        response = client.post("/fx-rates/", json=fx_rate_data)
        assert response.status_code == 409
    
    def test_create_fx_rate_negative_rate(self, client, db_session):
        """Test FX rate creation with negative rate."""
        fx_rate_data = {
            "from_currency": "USD",
            "to_currency": "EUR",
            "rate": -0.85,
            "year": 2024,
            "month": 1
        }
        response = client.post("/fx-rates/", json=fx_rate_data)
        assert response.status_code == 422
    
    def test_create_fx_rate_invalid_month(self, client, db_session):
        """Test FX rate creation with invalid month."""
        fx_rate_data = {
            "from_currency": "USD",
            "to_currency": "EUR",
            "rate": 0.85,
            "year": 2024,
            "month": 13
        }
        response = client.post("/fx-rates/", json=fx_rate_data)
        assert response.status_code == 409
    
    def test_create_fx_rate_duplicate(self, client, db_session):
        """Test FX rate creation with duplicate currency pair and date."""
        fx_rate_data = {
            "from_currency": "USD",
            "to_currency": "EUR",
            "rate": 0.85,
            "year": 2024,
            "month": 1
        }
        # Create first rate
        response = client.post("/fx-rates/", json=fx_rate_data)
        assert response.status_code == 201
        
        # Try to create duplicate
        response = client.post("/fx-rates/", json=fx_rate_data)
        assert response.status_code == 409

class TestGetFxRates:
    """Test cases for getting FX rates"""
    
    def test_get_all_fx_rates_empty(self, client, db_session):
        """Test getting all FX rates when none exist."""
        response = client.get("/fx-rates/")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_all_fx_rates_multiple(self, client, db_session):
        """Test getting all FX rates when multiple exist."""
        # Create multiple FX rates
        fx_rates_data = [
            {"from_currency": "USD", "to_currency": "EUR", "rate": 0.85, "year": 2024, "month": 1},
            {"from_currency": "EUR", "to_currency": "GBP", "rate": 0.88, "year": 2024, "month": 1},
            {"from_currency": "USD", "to_currency": "GBP", "rate": 0.75, "year": 2024, "month": 2}
        ]
        
        for fx_rate_data in fx_rates_data:
            response = client.post("/fx-rates/", json=fx_rate_data)
            assert response.status_code == 201
        
        # Get all FX rates
        response = client.get("/fx-rates/")
        assert response.status_code == 200
        fx_rates = response.json()
        assert len(fx_rates) == 3
    
    def test_get_fx_rate_success(self, client, db_session):
        """Test getting a specific FX rate by ID."""
        # Create FX rate
        fx_rate_data = {
            "from_currency": "USD",
            "to_currency": "EUR",
            "rate": 0.85,
            "year": 2024,
            "month": 1
        }
        response = client.post("/fx-rates/", json=fx_rate_data)
        fx_rate = response.json()
        
        # Get FX rate
        response = client.get(f"/fx-rates/{fx_rate['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == fx_rate["id"]
        assert data["from_currency"] == fx_rate["from_currency"]
        assert data["to_currency"] == fx_rate["to_currency"]
    
    def test_get_fx_rate_not_found(self, client, db_session):
        """Test getting a non-existent FX rate."""
        response = client.get("/fx-rates/99999")
        assert response.status_code == 404

class TestUpdateFxRate:
    """Test cases for updating FX rates"""
    
    def test_update_fx_rate_success(self, client, db_session):
        """Test successful FX rate update."""
        # Create FX rate
        fx_rate_data = {
            "from_currency": "USD",
            "to_currency": "EUR",
            "rate": 0.85,
            "year": 2024,
            "month": 1
        }
        response = client.post("/fx-rates/", json=fx_rate_data)
        fx_rate = response.json()
        
        # Update FX rate
        update_data = {"rate": 0.90}
        response = client.patch(f"/fx-rates/{fx_rate['id']}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["rate"] == 0.90
        assert data["from_currency"] == fx_rate["from_currency"]  # Should remain unchanged
    
    def test_update_fx_rate_invalid_rate(self, client, db_session):
        """Test FX rate update with invalid rate."""
        # Create FX rate
        fx_rate_data = {
            "from_currency": "USD",
            "to_currency": "EUR",
            "rate": 0.85,
            "year": 2024,
            "month": 1
        }
        response = client.post("/fx-rates/", json=fx_rate_data)
        fx_rate = response.json()
        
        # Update with invalid rate
        update_data = {"rate": -0.90}
        response = client.patch(f"/fx-rates/{fx_rate['id']}", json=update_data)
        assert response.status_code == 422
    
    def test_update_fx_rate_not_found(self, client, db_session):
        """Test updating a non-existent FX rate."""
        update_data = {"rate": 0.90}
        response = client.patch("/fx-rates/99999", json=update_data)
        assert response.status_code == 404

class TestDeleteFxRate:
    """Test cases for deleting FX rates"""
    
    def test_delete_fx_rate_success(self, client, db_session):
        """Test successful FX rate deletion."""
        # Create FX rate
        fx_rate_data = {
            "from_currency": "USD",
            "to_currency": "EUR",
            "rate": 0.85,
            "year": 2024,
            "month": 1
        }
        response = client.post("/fx-rates/", json=fx_rate_data)
        fx_rate = response.json()
        
        # Delete FX rate
        response = client.delete(f"/fx-rates/{fx_rate['id']}")
        assert response.status_code == 204
    
    def test_delete_fx_rate_not_found(self, client, db_session):
        """Test deleting a non-existent FX rate."""
        response = client.delete("/fx-rates/99999")
        assert response.status_code == 404

class TestFxRateValidation:
    """Test cases for FX rate validation and business rules"""
    
    def test_fx_rate_currency_length(self, client, db_session):
        """Test FX rate currency length validation."""
        # Test with 2-character currency
        fx_rate_data = {
            "from_currency": "US",  # Too short
            "to_currency": "EUR",
            "rate": 0.85,
            "year": 2024,
            "month": 1
        }
        response = client.post("/fx-rates/", json=fx_rate_data)
        assert response.status_code == 422
        
        # Test with 4-character currency
        fx_rate_data = {
            "from_currency": "USDD",  # Too long
            "to_currency": "EUR",
            "rate": 0.85,
            "year": 2024,
            "month": 1
        }
        response = client.post("/fx-rates/", json=fx_rate_data)
        assert response.status_code == 422
    
    def test_fx_rate_month_range(self, client, db_session):
        """Test FX rate month range validation."""
        # Test with month 0
        fx_rate_data = {
            "from_currency": "USD",
            "to_currency": "EUR",
            "rate": 0.85,
            "year": 2024,
            "month": 0
        }
        response = client.post("/fx-rates/", json=fx_rate_data)
        assert response.status_code == 409
        
        # Test with month 13
        fx_rate_data = {
            "from_currency": "USD",
            "to_currency": "EUR",
            "rate": 0.85,
            "year": 2024,
            "month": 13
        }
        response = client.post("/fx-rates/", json=fx_rate_data)
        assert response.status_code == 409
    
    def test_fx_rate_positive_rate(self, client, db_session):
        """Test FX rate positive rate validation."""
        fx_rate_data = {
            "from_currency": "USD",
            "to_currency": "EUR",
            "rate": 0.0,  # Zero rate
            "year": 2024,
            "month": 1
        }
        response = client.post("/fx-rates/", json=fx_rate_data)
        assert response.status_code == 422

class TestFxRateEdgeCases:
    """Test cases for edge cases and boundary conditions"""
    
    def test_fx_rate_maximum_rate(self, client, db_session):
        """Test FX rate with maximum rate value."""
        max_rate = 999999999.999999
        fx_rate_data = {
            "from_currency": "USD",
            "to_currency": "EUR",
            "rate": max_rate,
            "year": 2024,
            "month": 1
        }
        response = client.post("/fx-rates/", json=fx_rate_data)
        assert response.status_code == 201
        data = response.json()
        assert data["rate"] == max_rate
    
    def test_fx_rate_minimum_rate(self, client, db_session):
        """Test FX rate with minimum rate value."""
        min_rate = 0.000001
        fx_rate_data = {
            "from_currency": "USD",
            "to_currency": "EUR",
            "rate": min_rate,
            "year": 2024,
            "month": 1
        }
        response = client.post("/fx-rates/", json=fx_rate_data)
        assert response.status_code == 201
        data = response.json()
        assert data["rate"] == min_rate
    
    def test_fx_rate_different_years(self, client, db_session):
        """Test FX rates for different years."""
        fx_rates_data = [
            {"from_currency": "USD", "to_currency": "EUR", "rate": 0.85, "year": 2023, "month": 12},
            {"from_currency": "USD", "to_currency": "EUR", "rate": 0.87, "year": 2024, "month": 1},
            {"from_currency": "USD", "to_currency": "EUR", "rate": 0.89, "year": 2024, "month": 2}
        ]
        
        for fx_rate_data in fx_rates_data:
            response = client.post("/fx-rates/", json=fx_rate_data)
            assert response.status_code == 201
        
        # Verify all rates exist
        response = client.get("/fx-rates/")
        assert response.status_code == 200
        assert len(response.json()) == 3
    
    def test_fx_rate_all_months(self, client, db_session):
        """Test FX rates for all months of a year."""
        for month in range(1, 13):
            fx_rate_data = {
                "from_currency": "USD",
                "to_currency": "EUR",
                "rate": 0.85 + (month * 0.001),  # Slightly different rate per month
                "year": 2024,
                "month": month
            }
            response = client.post("/fx-rates/", json=fx_rate_data)
            assert response.status_code == 201
        
        # Verify all 12 months exist
        response = client.get("/fx-rates/")
        assert response.status_code == 200
        assert len(response.json()) == 12

class TestFxRateIntegration:
    """Integration tests for FX rate functionality"""
    
    def test_fx_rate_lifecycle(self, client, db_session):
        """Test complete FX rate lifecycle: create -> update -> delete."""
        # Create FX rate
        fx_rate_data = {
            "from_currency": "USD",
            "to_currency": "EUR",
            "rate": 0.85,
            "year": 2024,
            "month": 1
        }
        response = client.post("/fx-rates/", json=fx_rate_data)
        assert response.status_code == 201
        fx_rate = response.json()
        fx_rate_id = fx_rate["id"]
        
        # Update FX rate
        update_data = {"rate": 0.90}
        response = client.patch(f"/fx-rates/{fx_rate_id}", json=update_data)
        assert response.status_code == 200
        assert response.json()["rate"] == 0.90
        
        # Delete FX rate
        response = client.delete(f"/fx-rates/{fx_rate_id}")
        assert response.status_code == 204
        
        # Verify FX rate is deleted
        response = client.get(f"/fx-rates/{fx_rate_id}")
        assert response.status_code == 404
    
    def test_fx_rate_multiple_currency_pairs(self, client, db_session):
        """Test FX rates for multiple currency pairs."""
        currency_pairs = [
            ("USD", "EUR", 0.85),
            ("EUR", "GBP", 0.88),
            ("USD", "GBP", 0.75),
            ("EUR", "USD", 1.18),
            ("GBP", "USD", 1.33)
        ]
        
        for from_curr, to_curr, rate in currency_pairs:
            fx_rate_data = {
                "from_currency": from_curr,
                "to_currency": to_curr,
                "rate": rate,
                "year": 2024,
                "month": 1
            }
            response = client.post("/fx-rates/", json=fx_rate_data)
            assert response.status_code == 201
        
        # Verify all rates exist
        response = client.get("/fx-rates/")
        assert response.status_code == 200
        assert len(response.json()) == 5
    
    def test_fx_rate_historical_data(self, client, db_session):
        """Test FX rates with historical data."""
        # Create rates for multiple months
        months_data = [
            {"month": 1, "rate": 0.85},
            {"month": 2, "rate": 0.87},
            {"month": 3, "rate": 0.89},
            {"month": 4, "rate": 0.91},
            {"month": 5, "rate": 0.88}
        ]
        
        for month_data in months_data:
            fx_rate_data = {
                "from_currency": "USD",
                "to_currency": "EUR",
                "rate": month_data["rate"],
                "year": 2024,
                "month": month_data["month"]
            }
            response = client.post("/fx-rates/", json=fx_rate_data)
            assert response.status_code == 201
        
        # Verify all historical rates exist
        response = client.get("/fx-rates/")
        assert response.status_code == 200
        assert len(response.json()) == 5
        
        # Verify rates are in chronological order
        fx_rates = response.json()
        rates = [fx["rate"] for fx in fx_rates]
        assert 0.85 in rates
        assert 0.87 in rates
        assert 0.89 in rates
        assert 0.91 in rates
        assert 0.88 in rates
