"""
Shared test configuration and fixtures for the finance app backend.
This file is automatically loaded by pytest and provides common fixtures
and configuration for all test modules.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime
import os
import sys

# Add the parent directory to the path so we can import from app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.main import app
from app.database import get_db, Base
from app import models, schemas

# Test database setup - always create in tests directory
import os
TEST_DB_PATH = os.path.join(os.path.dirname(__file__), "test.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{TEST_DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """Override the database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)

@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "home_currency": "USD"
    }

@pytest.fixture
def sample_user(db_session, sample_user_data):
    """Create a sample user in the database."""
    user = models.User(**sample_user_data)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def multiple_users(db_session):
    """Create multiple users for testing."""
    users_data = [
        {"name": "User 1", "email": "user1@example.com", "home_currency": "USD"},
        {"name": "User 2", "email": "user2@example.com", "home_currency": "EUR"},
        {"name": "User 3", "email": "user3@example.com", "home_currency": "GBP"}
    ]
    
    users = []
    for user_data in users_data:
        user = models.User(**user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        users.append(user)
    
    return users

@pytest.fixture
def sample_accounts(db_session, sample_user):
    """Create sample accounts for testing."""
    accounts_data = [
        {
            "name": "Checking Account",
            "type": "asset",
            "user_id": sample_user.id,
            "currency": "USD",
            "opening_balance": 1000.0,
            "bank_name": "Test Bank"
        },
        {
            "name": "Savings Account",
            "type": "asset",
            "user_id": sample_user.id,
            "currency": "USD",
            "opening_balance": 5000.0,
            "bank_name": "Test Bank"
        },
        {
            "name": "EUR Account",
            "type": "asset",
            "user_id": sample_user.id,
            "currency": "EUR",
            "opening_balance": 2000.0,
            "bank_name": "Test Bank"
        },
        {
            "name": "Credit Card",
            "type": "liability",
            "user_id": sample_user.id,
            "currency": "USD",
            "opening_balance": 0.0,
            "bank_name": "Test Bank",
            "billing_day": 15,
            "due_day": 10
        },
        {
            "name": "Salary Income",
            "type": "income",
            "user_id": sample_user.id
        },
        {
            "name": "Groceries",
            "type": "expense",
            "user_id": sample_user.id
        }
    ]
    
    accounts = {}
    for account_data in accounts_data:
        if account_data["type"] in ["asset", "liability"]:
            account = models.Account(**account_data)
        else:
            account = models.Account(
                name=account_data["name"],
                type=account_data["type"],
                user_id=account_data["user_id"]
            )
        db_session.add(account)
        db_session.commit()
        db_session.refresh(account)
        # Create multiple keys for easier access
        key = account_data["name"].lower().replace(" ", "_")
        accounts[key] = account
        # Also add type-based keys
        accounts[account_data["type"]] = account
        if account_data["type"] == "asset" and "checking" in account_data["name"].lower():
            accounts["asset"] = account
        elif account_data["type"] == "asset" and "savings" in account_data["name"].lower():
            accounts["savings"] = account
        elif account_data["type"] == "asset" and "eur" in account_data["name"].lower():
            accounts["asset_eur"] = account
        elif account_data["type"] == "liability":
            accounts["liability"] = account
        elif account_data["type"] == "income":
            accounts["income"] = account
        elif account_data["type"] == "expense":
            accounts["expense"] = account
    
    return accounts

@pytest.fixture
def sample_transactions(db_session, sample_user, sample_accounts):
    """Create sample transactions for testing."""
    transactions_data = [
        {
            "user_id": sample_user.id,
            "date": "2024-01-15T10:00:00",
            "type": "income",
            "description": "Salary payment",
            "amount_oc_primary": 5000.00,
            "currency_primary": "USD",
            "account_id_primary": sample_accounts["income"].id,
            "account_id_secondary": sample_accounts["checking_account"].id
        },
        {
            "user_id": sample_user.id,
            "date": "2024-01-16T14:30:00",
            "type": "expense",
            "description": "Grocery shopping",
            "amount_oc_primary": 150.00,
            "currency_primary": "USD",
            "account_id_primary": sample_accounts["expense"].id,
            "account_id_secondary": sample_accounts["checking_account"].id
        },
        {
            "user_id": sample_user.id,
            "date": "2024-01-17T09:15:00",
            "type": "transfer",
            "description": "Transfer to savings",
            "amount_oc_primary": 1000.00,
            "currency_primary": "USD",
            "account_id_primary": sample_accounts["checking_account"].id,
            "account_id_secondary": sample_accounts["savings_account"].id
        }
    ]
    
    transactions = []
    for tx_data in transactions_data:
        # Convert string date to datetime object
        from datetime import datetime
        tx_data_copy = tx_data.copy()
        tx_data_copy["date"] = datetime.fromisoformat(tx_data["date"])
        # Set tx_amount_hc to match amount_oc_primary for consistency
        tx_data_copy["tx_amount_hc"] = tx_data_copy["amount_oc_primary"]
        transaction = models.Transaction(**tx_data_copy)
        db_session.add(transaction)
        db_session.commit()
        db_session.refresh(transaction)
        transactions.append(transaction)

    return transactions

@pytest.fixture
def sample_people(db_session, sample_user):
    """Create sample people for testing."""
    people_data = [
        {
            "name": "John Doe",
            "user_id": sample_user.id,
            "is_me": False
        },
        {
            "name": "Jane Smith", 
            "user_id": sample_user.id,
            "is_me": False
        },
        {
            "name": "Bob Johnson",
            "user_id": sample_user.id,
            "is_me": False
        }
    ]

    people = []
    for person_data in people_data:
        person = models.Person(**person_data)
        db_session.add(person)
        db_session.commit()
        db_session.refresh(person)
        people.append(person)

    return people