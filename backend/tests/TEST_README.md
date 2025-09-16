# Finance App Backend Tests

This directory contains comprehensive tests for the finance app backend functionality.

## Project Structure

The project now follows Python testing best practices:

```
finance-app/
├── backend/
│   ├── app/                    # Application code only
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── crud.py
│   │   ├── database.py
│   │   ├── auth.py
│   │   └── routers/
│   ├── tests/                  # All test-related files
│   │   ├── __init__.py
│   │   ├── conftest.py         # Shared test configuration
│   │   ├── test_users.py       # User tests
│   │   ├── test_accounts.py    # Account tests
│   │   ├── test_people.py      # People tests
│   │   ├── requirements-test.txt
│   │   ├── pytest.ini
│   │   ├── run_tests.py
│   │   └── TEST_README.md
│   ├── requirements.txt        # Production dependencies
│   └── app.db                 # Production database
└── frontend/
```

## Test Coverage

The test suite covers all backend functionality:

### **User Tests (46 tests)**

### 1. User Creation (POST /users/)
- ✅ Valid user creation with different currencies
- ✅ Currency normalization (lowercase → uppercase)
- ✅ Validation of required fields
- ✅ Email format validation
- ✅ Field length validation
- ✅ Duplicate email handling
- ✅ Empty field validation

### 2. Get Users (GET /users/ and GET /users/{user_id})
- ✅ Get all active users
- ✅ Get specific user by ID
- ✅ Handle non-existent users
- ✅ Exclude deactivated users
- ✅ Empty user list handling

### 3. Update User (PATCH /users/{user_id})
- ✅ Update individual fields
- ✅ Update multiple fields
- ✅ Currency normalization
- ✅ Duplicate email prevention
- ✅ Validation of updated fields
- ✅ Handle non-existent users
- ✅ Handle deactivated users

### 4. Deactivate User (PATCH /users/{user_id}/deactivate)
- ✅ Successful deactivation
- ✅ Prevent deactivating last user
- ✅ Handle non-existent users
- ✅ Handle already deactivated users

### 5. Activate User (PATCH /users/{user_id}/activate)
- ✅ Successful activation
- ✅ Handle non-existent users
- ✅ Handle already active users

### 6. Database Constraints
- ✅ Unique email constraint
- ✅ Soft delete consistency
- ✅ Currency length validation

### 7. Edge Cases
- ✅ Maximum length strings
- ✅ Special characters in fields
- ✅ Currency case handling

### 8. Integration Tests
- ✅ Complete user lifecycle
- ✅ Multiple user operations

### **Account Tests (35+ tests)**

#### 1. Account Creation
- ✅ Income/expense account creation
- ✅ Asset account creation with currency
- ✅ Liability account creation with billing/due days
- ✅ Validation of required fields per account type
- ✅ Duplicate name prevention
- ✅ Invalid account type handling

#### 2. Account Retrieval
- ✅ Get all accounts for user
- ✅ Get specific account by ID
- ✅ Handle non-existent accounts
- ✅ User-specific account filtering

#### 3. Account Updates
- ✅ Update account name and type
- ✅ Partial updates
- ✅ Validation of updated fields
- ✅ Handle non-existent accounts

#### 4. Account Deactivation/Activation
- ✅ Successful account deactivation
- ✅ Successful account activation
- ✅ Handle non-existent accounts

#### 5. Account Validation
- ✅ Currency required for asset/liability accounts
- ✅ Billing day validation (1-31)
- ✅ Due day validation (1-31)
- ✅ Income/expense accounts don't require currency
- ✅ Opening balance validation

#### 6. Edge Cases
- ✅ Maximum length account names
- ✅ Currency case handling
- ✅ Negative opening balance prevention
- ✅ Special characters in names

#### 7. Integration Tests
- ✅ Complete account lifecycle (create -> update -> deactivate -> activate)
- ✅ Multiple account types creation

### **People Tests (30+ tests)**

#### 1. Person Creation
- ✅ Valid person creation
- ✅ Person marked as "me" (is_me=True)
- ✅ Default is_me value (False)
- ✅ Validation of required fields
- ✅ Name length validation
- ✅ Duplicate name prevention
- ✅ Only one "me" person per user

#### 2. Person Retrieval
- ✅ Get all people
- ✅ Get specific person by ID
- ✅ Handle non-existent people

#### 3. Person Updates
- ✅ Update person name and is_me status
- ✅ Partial updates
- ✅ Duplicate name prevention
- ✅ Duplicate "me" status prevention
- ✅ Handle non-existent people

#### 4. Person Deactivation/Activation
- ✅ Successful person deactivation
- ✅ Successful person activation
- ✅ Handle non-existent people

#### 5. Person Validation
- ✅ Name length validation (1-100 chars)
- ✅ Special characters in names
- ✅ Empty name prevention

#### 6. Edge Cases
- ✅ Multiple people per user
- ✅ "Me" person constraint enforcement
- ✅ Maximum length names

#### 7. Integration Tests
- ✅ Complete person lifecycle (create -> update -> deactivate -> activate)
- ✅ "Me" person constraint testing

## Running Tests

### Prerequisites
Make sure you have the virtual environment activated and install test dependencies:

```bash
# Activate virtual environment (Windows)
venv\Scripts\activate

# Install production dependencies
pip install -r ../requirements.txt

# Install test dependencies
pip install -r requirements-test.txt
```

### Running Tests

#### Option 1: Using the test runner script (from tests directory)
```bash
cd tests
python run_tests.py
```

#### Option 2: Using pytest directly (from backend directory)
```bash
# Run all tests
pytest tests/ -v

# Run specific test files
pytest tests/test_users.py -v
pytest tests/test_accounts.py -v
pytest tests/test_people.py -v

# Run specific test class
pytest tests/test_users.py::TestUserCreation -v
pytest tests/test_accounts.py::TestAccountCreation -v
pytest tests/test_people.py::TestPersonCreation -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

#### Option 3: Using pytest with different options
```bash
# Run tests with detailed output
pytest tests/ -v -s

# Run tests and stop on first failure
pytest tests/ -x

# Run tests in parallel (if pytest-xdist is installed)
pytest tests/ -n auto
```

## Test Database

The tests use a separate SQLite test database (`test.db`) that is created and destroyed for each test session. This ensures:

- Tests don't interfere with each other
- No data pollution between test runs
- Clean state for each test

## Test Fixtures

The test suite uses several pytest fixtures defined in `conftest.py`:

- `db_session` - Fresh database session for each test
- `client` - FastAPI test client
- `sample_user_data` - Sample user data for testing
- `sample_user` - Pre-created user in database
- `multiple_users` - Multiple pre-created users

## Expected Test Results

When all tests pass, you should see output like:
```
tests/test_users.py::TestUserCreation::test_create_user_success PASSED
tests/test_accounts.py::TestAccountCreation::test_create_income_account_success PASSED
tests/test_people.py::TestPersonCreation::test_create_person_success PASSED
...
========================================= 110+ passed in 15.34s =========================================
```

## Troubleshooting

### Common Issues:

1. **Import Errors**: Make sure you're in the backend directory and the virtual environment is activated
2. **Database Errors**: Ensure SQLite is available and the test database can be created
3. **Dependency Errors**: Install all requirements from both `requirements.txt` and `requirements-test.txt`

### Debug Mode:
Run tests with `-s` flag to see print statements and debug output:
```bash
pytest tests/ -v -s
```

## Adding New Tests

To add new test cases:

1. Add new test methods to the appropriate test class in the relevant test file
2. Follow the naming convention: `test_<functionality>_<scenario>`
3. Use descriptive assertions with clear error messages
4. Test both success and failure cases
5. Update this README if adding new test categories

## Test Categories

- **Unit Tests**: Test individual functions/methods
- **Integration Tests**: Test component interactions
- **Edge Case Tests**: Test boundary conditions
- **Validation Tests**: Test input validation
- **Business Logic Tests**: Test business rules and constraints

## Test Files Overview

- **`test_users.py`** - 46 tests covering user CRUD operations, validation, and business rules
- **`test_accounts.py`** - 35+ tests covering account creation, validation, and type-specific logic
- **`test_people.py`** - 30+ tests covering person management and "me" person constraints

## Best Practices Followed

1. **Separation of Concerns**: Tests are completely separate from application code
2. **Shared Configuration**: Common fixtures and setup in `conftest.py`
3. **Isolated Tests**: Each test gets a fresh database
4. **Clear Naming**: Descriptive test names and class organization
5. **Comprehensive Coverage**: Both positive and negative test cases
6. **Proper Dependencies**: Separate requirements for production and testing
