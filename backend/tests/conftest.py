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
